#!/bin/bash
# RANNI - Instalador para Linux

set -e

RANNI_PATH="/opt/ranni"
REPO_URL="https://github.com/strem5059/ranni.git"

echo "=== RANNI - Instalador Linux ==="

# 1. Dependencias del sistema
echo "Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv portaudio19-dev \
    pulseaudio-utils espeak-ng git nodejs npm

# 2. Clonar repositorio
if [ ! -d "$RANNI_PATH" ]; then
    sudo git clone $REPO_URL $RANNI_PATH
fi

# 3. Python venv + dependencias
sudo python3 -m venv $RANNI_PATH/venv
sudo $RANNI_PATH/venv/bin/pip install -r $RANNI_PATH/requirements.txt

# 4. UI dependencies
cd $RANNI_PATH/ui
sudo npm install
cd ..

# 5. Servicio systemd
sudo cp $RANNI_PATH/installer/linux/ranni.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ranni
sudo systemctl start ranni

# 6. Logs
sudo mkdir -p /var/log/ranni
sudo chown -R $USER:$USER /var/log/ranni

echo "RANNI instalado correctamente."
echo "Estado: sudo systemctl status ranni"
