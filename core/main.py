import asyncio
import signal
import subprocess
import sys
import yaml
from pathlib import Path

from core.audio.wake_word import WakeWordDetector
from core.audio.stt import SpeechToText
from core.audio.tts import TextToSpeech
from core.audio.vad import VoiceActivityDetector
from core.nlp.engine import LLMEngine
from core.nlp.context import ContextMemory
from core.nlp.intents import IntentParser
from core.system.executor import SystemExecutor
from core.system.automation import TaskAutomation
from core.ui_bridge.websocket_server import UIBridge
from core.ui_bridge.events import AssistantState, RanniEvent
from core.utils.logger import ranni_logger

logger = ranni_logger.bind(module="main")


class RanniAssistant:
    def __init__(self, config_path=None):
        logger.info("Inicializando RANNI Assistant...")
        self.config = self._load_config(config_path)
        self.state = AssistantState.IDLE

        # Inicializar componentes
        self.wake_word = WakeWordDetector(config=self.config.get("wake_word", {}))
        self.stt = SpeechToText(
            model_size=self.config.get("stt", {}).get("model", "tiny"),
            device=self.config.get("stt", {}).get("device", "auto")
        )
        self.tts = TextToSpeech(
            voice=self.config.get("tts", {}).get("voice", "es_ES-daveconroy-medium")
        )
        self.vad = VoiceActivityDetector()
        self.llm = LLMEngine(
            host=self.config.get("llm", {}).get("host", "http://localhost:11434"),
            model=self.config.get("llm", {}).get("model", "llama3.2")
        )
        self.memory = ContextMemory()
        self.intent_parser = IntentParser()

        permissions = self._load_permissions()
        self.executor = SystemExecutor(permissions=permissions)

        self.automation = TaskAutomation()
        self.ui_bridge = UIBridge()
        self.running = True

    def _load_config(self, config_path):
        if not config_path:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar config: {e}")
            return {}

    def _load_permissions(self):
        path = Path(__file__).parent.parent / "config" / "permissions.yaml"
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("actions", {}) if data else {}
        except Exception as e:
            logger.warning(f"No se pudieron cargar permisos: {e}")
            return {}

    async def start(self):
        logger.info("Iniciando componentes...")

        # Iniciar UI WebSocket
        asyncio.create_task(self.ui_bridge.start())
        await self.ui_bridge.send_status("initializing", "Iniciando RANNI...")

        # Iniciar wake word
        if not self.wake_word.start():
            logger.error("Fallo al iniciar wake word")
            return

        # Iniciar STT
        if not self.stt.start():
            logger.error("Fallo al iniciar STT")

        # Iniciar VAD
        self.vad.start()

        # Iniciar planificador
        self.automation.start_scheduler()

        # Verificar Ollama
        if self.llm.health_check():
            logger.info("Ollama conectado correctamente")
        else:
            logger.warning("Ollama no disponible. Inicia Ollama con: ollama serve")

        await self.ui_bridge.send_status("ready", "RANNI listo. Di 'Ranni' para activarme.")
        self.tts.speak("RANNI listo. Di mi nombre para activarme.")

        logger.info("RANNI iniciado — esperando wake word...")
        await self._main_loop()

    async def _main_loop(self):
        while self.running:
            detected = self.wake_word.listen_for_wake_word()

            if detected:
                await self._handle_wake_word()

            await asyncio.sleep(0.01)

    async def _handle_wake_word(self):
        self.state = AssistantState.LISTENING
        await self.ui_bridge.send_state("listening")
        self.tts.speak("Te escucho")
        logger.info("Wake word detectado — escuchando...")

        audio_data = self.vad.record_until_silence(
            self.wake_word.audio_stream,
            max_duration=10,
            silence_duration=1.5
        )

        if not audio_data:
            self.state = AssistantState.IDLE
            await self.ui_bridge.send_state("idle")
            return

        self.state = AssistantState.PROCESSING
        await self.ui_bridge.send_state("processing")

        text = self.stt.transcribe(audio_data)
        if not text:
            logger.info("No se detectó voz")
            self.state = AssistantState.IDLE
            await self.ui_bridge.send_state("idle")
            return

        logger.info(f"Comando: {text}")
        await self.ui_bridge.send_status("processing", f"Procesando: {text}")

        # Intentar parseo rápido primero
        quick_intent = self.intent_parser.quick_parse(text)
        if quick_intent:
            intent_data = quick_intent
        else:
            context = self.memory.get_recent_history(5)
            llm_resp = self.llm.process(text, context)
            intent_data = self.intent_parser.parse(llm_resp)

        # Ejecutar acción
        result = self.executor.execute(intent_data["intent"], intent_data["params"])

        if result.get("shutdown"):
            await self.ui_bridge.broadcast("shutdown", {})
            await self.ui_bridge.send_status("shutdown", "Apagando RANNI...")
            self.tts.speak("Apagando RANNI")
            await asyncio.sleep(2)
            self.running = False
            if sys.platform == "win32":
                subprocess.run('taskkill /f /fi "WindowTitle eq RANNI UI" 2>nul', shell=True)
            return

        response_text = result.get("message", intent_data.get("response", "Listo"))
        self.tts.speak(response_text)

        # Guardar en memoria
        self.memory.save_interaction(text, response_text, intent_data["intent"])

        self.state = AssistantState.SPEAKING
        await self.ui_bridge.send_status("speaking", response_text)

        await asyncio.sleep(1)
        self.state = AssistantState.IDLE
        await self.ui_bridge.send_state("idle")

    async def stop(self):
        logger.info("Deteniendo RANNI...")
        self.running = False
        self.wake_word.stop()
        self.automation.stop()
        await self.ui_bridge.stop()


async def main():
    assistant = RanniAssistant()

    def signal_handler():
        asyncio.create_task(assistant.stop())

    if sys.platform != "win32":
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    try:
        await assistant.start()
    except KeyboardInterrupt:
        await assistant.stop()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        await assistant.stop()


if __name__ == "__main__":
    asyncio.run(main())
