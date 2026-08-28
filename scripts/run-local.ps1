param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$EnvironmentPrefix = Join-Path $ProjectDir ".molood-env"
$PythonExe = Join-Path $EnvironmentPrefix "python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "MolOOD Explorer is not installed. Run scripts\install-local.ps1 first."
}

Set-Location $ProjectDir

$PortProbe = @'
import socket, sys
start = int(sys.argv[1])
with socket.socket() as sock:
    try:
        sock.bind(("127.0.0.1", start))
    except OSError:
        # Port 0 asks Windows to allocate an available ephemeral local port.
        sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
'@
$SelectedPort = & $PythonExe -c $PortProbe $Port
if ($LASTEXITCODE -ne 0 -or -not $SelectedPort) {
    throw "Could not allocate a local port for MolOOD Explorer."
}
$SelectedPort = [int]($SelectedPort | Select-Object -Last 1)
if ($SelectedPort -ne $Port) {
    Write-Host "Port $Port is busy; using $SelectedPort instead."
}
$LocalUrl = "http://127.0.0.1:$SelectedPort"
Write-Host "MolOOD Explorer URL: $LocalUrl"
Write-Host "Keep this PowerShell window open. Press Ctrl+C here to stop the app."
& $PythonExe -m streamlit run app.py --server.address 127.0.0.1 --server.port $SelectedPort
