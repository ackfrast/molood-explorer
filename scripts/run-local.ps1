param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MicromambaExe = Join-Path $ProjectDir ".local-tools\micromamba.exe"
$EnvironmentPrefix = Join-Path $ProjectDir ".molood-env"
$env:MAMBA_ROOT_PREFIX = Join-Path $ProjectDir ".local-tools\mamba-root"

if (-not (Test-Path $MicromambaExe) -or -not (Test-Path (Join-Path $EnvironmentPrefix "python.exe"))) {
    throw "MolOOD Explorer is not installed. Run scripts\install-local.ps1 first."
}

Set-Location $ProjectDir

$PortProbe = @'
import socket, sys
start = int(sys.argv[1])
for port in range(start, min(start + 20, 65536)):
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        continue
    finally:
        sock.close()
    print(port)
    raise SystemExit(0)
raise SystemExit(1)
'@
$SelectedPort = & $MicromambaExe run --prefix $EnvironmentPrefix python -c $PortProbe $Port
if ($LASTEXITCODE -ne 0 -or -not $SelectedPort) {
    throw "No available local port found between $Port and $([Math]::Min($Port + 19, 65535))."
}
$SelectedPort = [int]($SelectedPort | Select-Object -Last 1)
if ($SelectedPort -ne $Port) {
    Write-Host "Port $Port is busy; using $SelectedPort instead."
}
Write-Host "Open http://127.0.0.1:$SelectedPort in your browser."
& $MicromambaExe run --prefix $EnvironmentPrefix streamlit run app.py --server.address 127.0.0.1 --server.port $SelectedPort
