$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ToolsDir = Join-Path $ProjectDir ".local-tools"
$EnvironmentPrefix = Join-Path $ProjectDir ".molood-env"
$MicromambaExe = Join-Path $ToolsDir "micromamba.exe"
$env:MAMBA_ROOT_PREFIX = Join-Path $ToolsDir "mamba-root"

if (-not [Environment]::Is64BitOperatingSystem) {
    throw "MolOOD Explorer requires 64-bit Windows."
}
if ($env:PROCESSOR_ARCHITECTURE -notin @("AMD64", "ARM64")) {
    throw "Unsupported Windows architecture: $env:PROCESSOR_ARCHITECTURE"
}
# Micromamba's win-64 package runs natively on x64 and through Windows x64
# emulation on supported ARM64 systems.
$Platform = "win-64"

New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectDir "outputs") | Out-Null

if (-not (Test-Path $MicromambaExe)) {
    Write-Host "Downloading Micromamba for Windows..."
    $Archive = Join-Path $ToolsDir "micromamba.tar.bz2"
    Invoke-WebRequest -Uri "https://micro.mamba.pm/api/micromamba/$Platform/latest" -OutFile $Archive
    tar.exe -xjf $Archive -C $ToolsDir
    $Extracted = Get-ChildItem -Path $ToolsDir -Recurse -Filter "micromamba.exe" | Select-Object -First 1
    if (-not $Extracted) { throw "Could not find micromamba.exe in the downloaded archive." }
    Copy-Item -Force $Extracted.FullName $MicromambaExe
}

$PythonExe = Join-Path $EnvironmentPrefix "python.exe"
if (Test-Path $PythonExe) {
    Write-Host "Updating the local MolOOD environment..."
    & $MicromambaExe install --yes --prefix $EnvironmentPrefix --file (Join-Path $ProjectDir "environment.yml")
} else {
    Write-Host "Installing Python, RDKit, Streamlit, and scientific dependencies..."
    & $MicromambaExe create --yes --prefix $EnvironmentPrefix --file (Join-Path $ProjectDir "environment.yml")
}
if ($LASTEXITCODE -ne 0) { throw "Environment installation failed." }

& $MicromambaExe run --prefix $EnvironmentPrefix python -m pip install --no-deps --editable $ProjectDir
if ($LASTEXITCODE -ne 0) { throw "Project installation failed." }
& $MicromambaExe run --prefix $EnvironmentPrefix python -m pytest -q (Join-Path $ProjectDir "tests")
if ($LASTEXITCODE -ne 0) { throw "Project tests failed." }

Write-Host ""
Write-Host "Installation complete. Start MolOOD Explorer with:"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\run-local.ps1"
