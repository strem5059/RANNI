import pyaudio
import struct
import numpy as np
import threading
from pathlib import Path
from core.utils.logger import ranni_logger

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


class BaseDetector:
    def __init__(self):
        self.logger = ranni_logger.bind(module="wake_word")
        self.audio_stream = None
        self.pyaudio_instance = None

    def start(self):
        return True

    def listen(self):
        return False

    def stop(self):
        pass


class PorcupineDetector(BaseDetector):
    def __init__(self, access_key="demo", keyword_path=None, sensitivities=0.5):
        super().__init__()
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.sensitivities = sensitivities
        self.porcupine = None

    def start(self):
        try:
            import pvporcupine
            keywords = ["computer"] if self.access_key == "demo" else None
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=[self.keyword_path] if self.keyword_path else None,
                keywords=keywords,
                sensitivities=[self.sensitivities]
            )
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            self.logger.info(f"Porcupine iniciado (key: {self.access_key[:4]}...)")
            return True
        except ImportError:
            self.logger.warning("pvporcupine no instalado")
            return False
        except Exception as e:
            self.logger.error(f"Porcupine error: {e}")
            return False

    def listen(self):
        if not self.audio_stream or not self.porcupine:
            return False
        try:
            pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            return self.porcupine.process(pcm_unpacked) >= 0
        except:
            return False

    def stop(self):
        if self.audio_stream:
            self.audio_stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        if self.porcupine:
            self.porcupine.delete()


class OpenWakeWordDetector(BaseDetector):
    def __init__(self, model_name="ranni", threshold=0.5):
        super().__init__()
        self.model_name = model_name
        self.threshold = threshold
        self.model = None

    def start(self):
        try:
            from openwakeword import Model as OWWModel
            from openwakeword.utils import download_models
            models_dir = Path(__file__).parent.parent.parent / "models" / "wakeword"
            models_dir.mkdir(parents=True, exist_ok=True)

            self.model = OWWModel(
                wakeword_models=[self.model_name] if self.model_name == "ranni" else [],
                model_path=str(models_dir),
                inference_framework="onnx"
            )
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                rate=RATE, channels=1, format=FORMAT,
                input=True, frames_per_buffer=1280
            )
            self.logger.info(f"OpenWakeWord iniciado (modelo: {self.model_name})")
            return True
        except ImportError:
            self.logger.warning("openwakeword no instalado. Ejecuta: pip install openwakeword")
            return False
        except Exception as e:
            self.logger.error(f"OpenWakeWord error: {e}")
            return False

    def listen(self):
        if not self.audio_stream or not self.model:
            return False
        try:
            pcm = self.audio_stream.read(1280, exception_on_overflow=False)
            audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
            prediction = self.model(audio)
            score = prediction.get(self.model_name, 0)
            return score > self.threshold
        except:
            return False

    def stop(self):
        if self.audio_stream:
            self.audio_stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()


class KeyboardDetector(BaseDetector):
    def __init__(self, hotkey="ctrl+alt+r"):
        super().__init__()
        self.hotkey = hotkey
        self._pressed = False
        self._listener = None

    def start(self):
        try:
            import keyboard
            keyboard.on_press_key(self.hotkey, self._on_hotkey)
            self._listener = keyboard
            self.logger.info(f"Keyboard wake iniciado (hotkey: {self.hotkey})")
            return True
        except ImportError:
            self.logger.warning("keyboard no instalado. Ejecuta: pip install keyboard")
            return False
        except Exception as e:
            self.logger.error(f"Keyboard error: {e}")
            return False

    def _on_hotkey(self, _):
        self._pressed = True

    def listen(self):
        if self._pressed:
            self._pressed = False
            return True
        return False

    def stop(self):
        self._pressed = False


class AudioBufferDetector(BaseDetector):
    def __init__(self):
        super().__init__()

    def start(self):
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                rate=RATE, channels=1, format=FORMAT,
                input=True, frames_per_buffer=1024
            )
            self.logger.info("Audio buffer detector iniciado (siempre escuchando)")
            return True
        except Exception as e:
            self.logger.error(f"Audio buffer error: {e}")
            return False

    def read_chunk(self):
        if self.audio_stream:
            return self.audio_stream.read(1024, exception_on_overflow=False)
        return b""

    def stop(self):
        if self.audio_stream:
            self.audio_stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()


class WakeWordDetector:
    def __init__(self, config=None):
        self.logger = ranni_logger.bind(module="wake_word")
        self.config = config or {}
        self.mode = self.config.get("mode", "auto")
        self.detector = None
        self.audio_buffer = None
        self._active_detector_type = None

    def start(self):
        strategies = []

        if self.mode == "auto":
            strategies = [
                ("porcupine_demo", PorcupineDetector(access_key="demo")),
                ("openwakeword", OpenWakeWordDetector()),
                ("keyboard", KeyboardDetector()),
            ]
        elif self.mode == "porcupine":
            key = self.config.get("porcupine_key", "demo")
            strategies = [
                ("porcupine", PorcupineDetector(access_key=key)),
                ("keyboard", KeyboardDetector()),
            ]
        elif self.mode == "openwakeword":
            strategies = [
                ("openwakeword", OpenWakeWordDetector(
                    model_name=self.config.get("wake_word", "ranni"),
                    threshold=self.config.get("threshold", 0.5)
                )),
                ("keyboard", KeyboardDetector()),
            ]
        elif self.mode == "keyboard":
            strategies = [
                ("keyboard", KeyboardDetector(hotkey=self.config.get("hotkey", "ctrl+alt+r")))
            ]
        elif self.mode == "porcupine_pro":
            strategies = [
                ("porcupine_pro", PorcupineDetector(
                    access_key=self.config.get("porcupine_key", ""),
                    keyword_path=self.config.get("keyword_path")
                )),
                ("keyboard", KeyboardDetector()),
            ]

        for name, detector in strategies:
            self.logger.info(f"Intentando {name}...")
            if detector.start():
                self.detector = detector
                self._active_detector_type = name
                self.logger.info(f"Wake word activo: {name}")

                if name != "keyboard":
                    self.audio_buffer = AudioBufferDetector()
                    self.audio_buffer.start()

                return True

        self.logger.error("NINGÚN detector de wake word pudo iniciarse")
        return False

    def listen_for_wake_word(self):
        if not self.detector:
            return False
        return self.detector.listen()

    @property
    def audio_stream(self):
        if self.audio_buffer:
            return self.audio_buffer.audio_stream
        if hasattr(self.detector, "audio_stream"):
            return self.detector.audio_stream
        return None

    def stop(self):
        if self.audio_buffer:
            self.audio_buffer.stop()
        if self.detector:
            self.detector.stop()
        self.logger.info("Wake word detector detenido")
