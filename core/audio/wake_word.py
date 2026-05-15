import pvporcupine
import pyaudio
import struct
import numpy as np
from core.utils.logger import ranni_logger

class WakeWordDetector:
    def __init__(self, access_key, keyword_path=None, sensitivities=0.5):
        self.logger = ranni_logger.bind(module="wake_word")
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.sensitivities = sensitivities
        self.porcupine = None
        self.audio_stream = None
        self.pyaudio_instance = None

    def start(self):
        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=[self.keyword_path] if self.keyword_path else None,
                keywords=["ranni"] if not self.keyword_path else None,
                sensitivities=[self.sensitivities]
            )
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
                stream_callback=None
            )
            self.logger.info("Wake word detector iniciado")
            return True
        except Exception as e:
            self.logger.error(f"Error al iniciar wake word: {e}")
            return False

    def listen_for_wake_word(self):
        if not self.audio_stream or not self.porcupine:
            return False
        try:
            pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            keyword_index = self.porcupine.process(pcm_unpacked)
            return keyword_index >= 0
        except Exception as e:
            self.logger.error(f"Error en listen_for_wake_word: {e}")
            return False

    def stop(self):
        if self.audio_stream:
            self.audio_stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        if self.porcupine:
            self.porcupine.delete()
