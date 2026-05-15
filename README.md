
```

      ██████╗  █████╗ ███╗   ██╗███╗   ██╗██╗
      ██╔══██╗██╔══██╗████╗  ██║████╗  ██║██║
      ██████╔╝███████║██╔██╗ ██║██╔██╗ ██║██║
      ██╔══██╗██╔══██║██║╚██╗██║██║╚██╗██║██║
      ██║  ██║██║  ██║██║ ╚████║██║ ╚████║██║
      ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚═╝


```
<h1 align="center">🚀 RANNI — Asistente Virtual de Escritorio</h1>
<p align="center">
  <em>Jarvis-like AI desktop assistant with holographic 3D interface</em>
</p>

---

## ✨ Características

| Funcionalidad | Estado |
|---------------|--------|
| 🎤 Wake word ("Ranni") con Porcupine | ✅ |
| 🗣️ STT local con faster-whisper | ✅ |
| 🧠 IA conversacional con Ollama + llama3.2 | ✅ |
| 🔊 TTS local con Piper | ✅ |
| 🪟 Control de ventanas y aplicaciones | ✅ |
| 📂 Lectura/escritura de archivos | ✅ |
| 🔐 Bloqueo, apagado, reinicio del sistema | ✅ |
| 🌐 Interfaz 3D holográfica (Three.js) | ✅ |
| 💫 Esfera de bits binarios animados | ✅ |
| 🔄 Inicio automático con el sistema | ✅ |
| 🧠 Memoria contextual (SQLite) | ✅ |
| 🛡️ Lista blanca de permisos | ✅ |

## 🧱 Stack Tecnológico

```
Backend:    Python 3.11 + faster-whisper + Porcupine + Piper + Ollama
Frontend:   Electron + Three.js + WebGL Shaders (GLSL)
Comms:      WebSocket (local, 127.0.0.1:9876)
Persist:    SQLite + ChromaDB (memoria semántica)
OS:         Windows (nssm) / Linux (systemd) / macOS (launchd)
```

## 📦 Requisitos

- **Python** 3.10+
- **Node.js** 18+ (para UI)
- **Ollama** instalado y corriendo (`ollama pull llama3.2`)
- **Micrófono** funcional

## 🚀 Instalación Rápida

```bash
# 1. Clonar
git clone https://github.com/strem5059/ranni.git
cd ranni

# 2. Backend
pip install -r requirements.txt

# 3. Frontend (UI 3D)
cd ui
npm install
cd ..

# 4. Iniciar Ollama (en otra terminal)
ollama pull llama3.2
ollama serve

# 5. Ejecutar RANNI
python core/main.py
```

## 🏗️ Estructura del Proyecto

```
ranni/
├── core/                   # Backend Python
│   ├── audio/              # Wake word, STT, TTS, VAD
│   ├── nlp/                # LLM, memoria, intenciones
│   ├── system/             # Automatización del SO
│   ├── ui_bridge/          # WebSocket con UI
│   ├── utils/              # Logger, helpers
│   └── main.py             # Entry point
├── ui/                     # Frontend Electron + Three.js
│   ├── main.js             # Ventana overlay transparente
│   ├── renderer/           # HTML/CSS/JS/Shaders
│   │   ├── js/ranni-3d.js  # Esfera holográfica
│   │   ├── js/particles.js # Sistema de partículas
│   │   └── js/shaders/     # GLSL shaders
│   └── package.json
├── config/                 # Config YAML + permisos
├── installer/              # Scripts por SO
├── tests/                  # Tests unitarios
└── data/                   # Logs y base de datos
```

## 🧠 Comandos de Voz

| Comando | Acción |
|---------|--------|
| "Ranni, abre Chrome" | Abre el navegador |
| "Ranni, cierra el bloc de notas" | Cierra una app |
| "Ranni, ¿qué hora es?" | Dice la hora |
| "Ranni, sube el volumen al 50%" | Controla volumen |
| "Ranni, dime el estado del sistema" | CPU/RAM/Disco |
| "Ranni, bloquea la PC" | Bloquea sesión |
| "Ranni, toma una captura" | Screenshot |
| "Ranni, escribe en el archivo..." | Manipula archivos |

## 🔒 Seguridad

- Permisos configurables vía `config/permissions.yaml`
- Acciones destructivas requieren confirmación explícita
- El micrófono solo transmite después del wake word
- Todo corre LOCALMENTE — sin datos a la nube

## 📊 Consumo de Recursos

| Componente | CPU | RAM |
|------------|-----|-----|
| Wake word (Porcupine) | ~1% | ~10 MB |
| STT (Whisper tiny) | ~20% (bajo demanda) | ~1 GB |
| LLM (Llama 3.2 Q4) | ~40% (bajo demanda) | ~4 GB |
| UI (Electron + Three.js) | ~5% (30 FPS idle) | ~200 MB |
| TTS (Piper) | ~5% (bajo demanda) | ~100 MB |

---

<p align="center">Hecho con ❤️ para el asistente de escritorio definitivo</p>
<p align="center">RANNI © 2026</p>
```

