$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MicromambaExe = Join-Path $ProjectDir ".local-tools\micromamba.exe"
$EnvironmentPrefix = Join-Path $ProjectDir ".molood-env"
$env:MAMBA_ROOT_PREFIX = Join-Path $ProjectDir ".local-tools\mamba-root"

if (-not (Test-Path $MicromambaExe) -or -not (Test-Path (Join-Path $EnvironmentPrefix "python.exe"))) {
    throw "MolOOD Explorer is not installed. Run scripts\install-local.ps1 first."
}

Set-Location $ProjectDir
& $MicromambaExe run --prefix $EnvironmentPrefix streamlit run app.py --server.address 127.0.0.1 --server.port 8501
