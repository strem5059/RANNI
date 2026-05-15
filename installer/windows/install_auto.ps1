# RANNI - Instalación automática completa
# Ejecutar como Administrador

$RepoUrl = "https://github.com/strem5059/ranni.git"
$RanniPath = "$env:USERPROFILE\RANNI"

Write-Host "=== RANNI - Instalación Automática ===" -ForegroundColor Cyan

# Clonar repositorio
if (-not (Test-Path $RanniPath)) {
    git clone $RepoUrl $RanniPath
}

Set-Location $RanniPath

# Python dependencies
pip install -r requirements.txt

# UI dependencies
Set-Location ui
npm install
Set-Location ..

# Instalar NSSM y crear servicio
$nssm = "$RanniPath\installer\nssm.exe"
if (-not (Test-Path $nssm)) {
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$env:TEMP\nssm.zip"
    Expand-Archive "$env:TEMP\nssm.zip" "$env:TEMP\nssm" -Force
    Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" $nssm
}

& $nssm install RANNI "pythonw.exe" "$RanniPath\core\main.py"
& $nssm set RANNI Start SERVICE_AUTO_START
Start-Service RANNI

# Startup shortcut
$wshell = New-Object -ComObject WScript.Shell
$lnk = $wshell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\RANNI.lnk")
$lnk.TargetPath = "pythonw.exe"
$lnk.Arguments = "$RanniPath\core\main.py"
$lnk.WorkingDirectory = $RanniPath
$lnk.Save()

Write-Host "RANNI instalado y corriendo." -ForegroundColor Green
