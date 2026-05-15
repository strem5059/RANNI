
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

## ⚠️ Estado del Proyecto

**RANNI está en desarrollo — NO es completamente funcional aún.**

Este es un proyecto personal que estoy construyendo como asistente de escritorio con interfaz holográfica 3D. Actualmente le faltan piezas para funcionar al 100% y estoy trabajando en ello.

Si llegaste aquí puedes:

- **Esperar** a que lo termine y tenga una versión estable
- **Clonar el repo y terminarlo tú mismo** — el código es completamente libre
- **Personalizarlo** a tu gusto y hacer tu propia versión

RANNI es **código abierto y de uso libre** para quien quiera terminarlo, modificarlo o usarlo como base para sus propios proyectos.

---

## ✨ Lo que busca ser

| Funcionalidad | Estado |
|---------------|--------|
| 🎤 Wake word con Porcupine | ✅ |
| 🗣️ STT local con faster-whisper | ✅ |
| 🧠 IA conversacional con Ollama | ✅ |
| 🔊 TTS local con Piper / pyttsx3 | ✅ |
| 🪟 Control de ventanas y apps | ✅ |
| 🔐 Bloqueo, apagado, reinicio | ✅ |
| 🌐 Interfaz 3D holográfica (Three.js) | ✅ |
| 🛡️ Lista blanca de permisos | ✅ |

## 🧱 Stack Tecnológico

```
Backend:    Python 3.11+ / faster-whisper / Porcupine / Piper / Ollama
Frontend:   Electron + Three.js + WebGL Shaders (GLSL)
Comms:      WebSocket (127.0.0.1:9876)
Persist:    SQLite
OS:         Windows / Linux / macOS
```

## 📦 Requisitos

- Python 3.10+
- Node.js 18+
- Ollama (`ollama pull llama3.2` / `ollama serve`)
- Micrófono funcional

## 🚀 Cómo empezar

```bash
git clone https://github.com/strem5059/ranni.git
cd ranni
pip install -r requirements.txt
cd ui && npm install && cd ..
ollama serve  # en otra terminal
python core/main.py
```

## 🤝 Contribuir

Si te interesa terminar RANNI o mejorarlo, eres bienvenido. Puedes:
- Hacer fork y mandar PR
- Reportar issues
- Usar el código para tu propio proyecto

No hay reglas — el proyecto es libre.

---

<p align="center">RANNI © 2026 — Código abierto, libre para quien quiera usarlo</p>
```
