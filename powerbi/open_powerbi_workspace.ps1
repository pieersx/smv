$ProjectRoot = Split-Path -Parent $PSScriptRoot
$GoldPath = Join-Path $ProjectRoot "data\gold"

Write-Host "Opening gold data folder: $GoldPath"
Start-Process explorer.exe $GoldPath

Write-Host "Opening Power BI Desktop..."
Start-Process "shell:AppsFolder\Microsoft.MicrosoftPowerBIDesktop_8wekyb3d8bbwe!Microsoft.MicrosoftPowerBIDesktop"
