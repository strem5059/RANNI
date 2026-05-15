#!/bin/bash
# RANNI - Instalador para macOS

set -e

RANNI_PATH="/opt/ranni"

echo "=== RANNI - Instalador macOS ==="

# 1. Instalar dependencias con Homebrew
if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

brew install python3 portaudio node

# 2. Clonar
if [ ! -d "$RANNI_PATH" ]; then
    sudo git clone https://github.com/strem5059/ranni.git $RANNI_PATH
fi

# 3. Python venv
sudo python3 -m venv $RANNI_PATH/venv
sudo $RANNI_PATH/venv/bin/pip install -r $RANNI_PATH/requirements.txt

# 4. UI
cd $RANNI_PATH/ui
sudo npm install
cd ..

# 5. launchd
sudo cp $RANNI_PATH/installer/macos/com.ranni.plist /Library/LaunchDaemons/
sudo launchctl load -w /Library/LaunchDaemons/com.ranni.plist

echo "RANNI instalado. Inicia con: sudo launchctl load /Library/LaunchDaemons/com.ranni.plist"
