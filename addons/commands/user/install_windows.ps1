param(
    [string]$AppPath = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($AppPath)) {
    $AppPath = Join-Path $PSScriptRoot "WwiseSelectionInspector.exe"
}

if (!(Test-Path $AppPath)) {
    Write-Error @"
WwiseSelectionInspector.exe was not found at:
$AppPath

Run this script from the packaged WwiseSelectionInspector folder, or pass the executable path explicitly:
.\install_windows.ps1 -AppPath "C:\Path\To\WwiseSelectionInspector.exe"
"@
    exit 1
}

$AppPath = (Resolve-Path $AppPath).Path
$CommandDir = Join-Path $env:APPDATA "Audiokinetic\Wwise\Add-ons\Commands"
$CommandFile = Join-Path $CommandDir "kameron_wwise_selection_inspector.json"

New-Item -ItemType Directory -Force -Path $CommandDir | Out-Null

$Command = [ordered]@{
    version = 2
    commands = @(
        [ordered]@{
            id = "kameron.wwise-selection-inspector.open"
            displayName = "Open Wwise Selection Inspector"
            program = $AppPath
            args = ""
            cwd = (Split-Path $AppPath -Parent)
            startMode = "MultipleSelectionSingleProcessSpaceSeparated"
            redirectOutputs = $false
            contextMenu = [ordered]@{
                basePath = "Wwise Selection Inspector"
            }
            mainMenu = [ordered]@{
                basePath = "Tools/Wwise Selection Inspector"
            }
        }
    )
}

$Command | ConvertTo-Json -Depth 8 | Set-Content -Path $CommandFile -Encoding UTF8

Write-Host "Installed Wwise Selection Inspector command add-on:"
Write-Host $CommandFile
Write-Host ""
Write-Host "Restart Wwise, then run:"
Write-Host "Tools > Wwise Selection Inspector > Open Wwise Selection Inspector"
