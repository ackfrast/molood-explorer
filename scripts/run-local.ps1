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

function Get-AvailablePort([int]$PreferredPort) {
    $Listener = $null
    try {
        $Listener = [System.Net.Sockets.TcpListener]::new(
            [System.Net.IPAddress]::Loopback, $PreferredPort
        )
        $Listener.Start()
        return [int]$Listener.LocalEndpoint.Port
    }
    finally {
        if ($null -ne $Listener) {
            $Listener.Stop()
        }
    }
}

try {
    $SelectedPort = Get-AvailablePort $Port
}
catch {
    $SelectedPort = Get-AvailablePort 0
}
if (-not $SelectedPort) {
    throw "Could not allocate a local port for MolOOD Explorer."
}
if ($SelectedPort -ne $Port) {
    Write-Host "Port $Port is busy; using $SelectedPort instead."
}
$LocalUrl = "http://127.0.0.1:$SelectedPort"
Write-Host "MolOOD Explorer URL: $LocalUrl"
Write-Host "Keep this PowerShell window open. Press Ctrl+C here to stop the app."
& $PythonExe -m streamlit run app.py --server.address 127.0.0.1 --server.port $SelectedPort
