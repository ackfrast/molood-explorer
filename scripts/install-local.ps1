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
$LocalTemp = Join-Path $ProjectDir ".local-temp"
New-Item -ItemType Directory -Force -Path $LocalTemp | Out-Null
# Some managed Windows installations deny pytest/pip access to AppData\Temp.
# Keep all installer temporary files inside the extracted project instead.
$env:TEMP = $LocalTemp
$env:TMP = $LocalTemp

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

$ExampleFile = Join-Path $ProjectDir "examples\synthetic_molecules.csv"
$SmokeReport = Join-Path $LocalTemp "scenario_report.json"
& $MicromambaExe run --prefix $EnvironmentPrefix python -c "import rdkit, streamlit, plotly, molood_explorer; print('Core imports OK')"
if ($LASTEXITCODE -ne 0) { throw "Core dependency check failed." }
& $MicromambaExe run --prefix $EnvironmentPrefix molood explore $ExampleFile --smiles-column smiles --target-column activity --output $SmokeReport
if ($LASTEXITCODE -ne 0) { throw "Synthetic-data smoke test failed." }

Write-Host ""
Write-Host "Installation and smoke test complete. Start MolOOD Explorer with:"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\run-local.ps1"
