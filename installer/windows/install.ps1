# RANNI - Instalador para Windows
# Ejecutar como Administrador: powershell -ExecutionPolicy Bypass -File install.ps1

$RanniPath = "$env:USERPROFILE\RANNI"
$PythonPath = "python"
$PipPath = "pip"

Write-Host "=== RANNI - Instalador Windows ===" -ForegroundColor Cyan
Write-Host ""

# 1. Clonar o copiar archivos
if (-not (Test-Path $RanniPath)) {
    Write-Host "Creando directorio en $RanniPath..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $RanniPath -Force | Out-Null
    Write-Host "Copia los archivos del proyecto a $RanniPath" -ForegroundColor Yellow
} else {
    Write-Host "Directorio ya existe: $RanniPath" -ForegroundColor Green
}

# 2. Instalar dependencias Python
Write-Host "Instalando dependencias Python..." -ForegroundColor Yellow
if (Test-Path "$RanniPath\requirements.txt") {
    & $PipPath install -r "$RanniPath\requirements.txt"
}

# 3. Instalar Node.js y Electron (para UI)
Write-Host "Instalando dependencias UI (Electron + Three.js)..." -ForegroundColor Yellow
if (Test-Path "$RanniPath\ui\package.json") {
    Set-Location "$RanniPath\ui"
    npm install
    Set-Location $RanniPath
}

# 4. Crear servicio con NSSM
$NssmPath = "$RanniPath\installer\nssm.exe"
if (-not (Test-Path $NssmPath)) {
    Write-Host "Descargando NSSM..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$env:TEMP\nssm.zip"
    Expand-Archive -Path "$env:TEMP\nssm.zip" -DestinationPath "$env:TEMP\nssm" -Force
    Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" $NssmPath -Force
}

# 5. Registrar servicio
Write-Host "Registrando servicio RANNI..." -ForegroundColor Yellow
$NssmPath install RANNI "pythonw.exe" "$RanniPath\core\main.py"
$NssmPath set RANNI DisplayName "RANNI - Asistente Virtual"
$NssmPath set RANNI Description "Asistente virtual de escritorio con control por voz"
$NssmPath set RANNI Start SERVICE_AUTO_START
$NssmPath set RANNI AppStdout "$RanniPath\data\service.log"
$NssmPath set RANNI AppStderr "$RanniPath\data\service-error.log"

# 6. Iniciar servicio
Write-Host "Iniciando servicio RANNI..." -ForegroundColor Yellow
Start-Service RANNI

# 7. Añadir acceso directo al Startup
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\RANNI.lnk")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "$RanniPath\core\main.py"
$Shortcut.WorkingDirectory = $RanniPath
$Shortcut.Save()

Write-Host ""
Write-Host "=== RANNI instalado correctamente ===" -ForegroundColor Green
Write-Host "El asistente se iniciará automáticamente al encender el equipo." -ForegroundColor Cyan
Write-Host "Comando: Say 'Ranni' para activarme." -ForegroundColor Cyan
Write-Host ""
Write-Host "Para desinstalar:" -ForegroundColor Yellow
Write-Host "  nssm remove RANNI confirm" -ForegroundColor Gray
Write-Host "  Remove-Item '$RanniPath' -Recurse -Force" -ForegroundColor Gray
