import numpy as np
from faster_whisper import WhisperModel
from core.utils.logger import ranni_logger

class SpeechToText:
    def __init__(self, model_size="tiny", device="auto", compute_type="int8"):
        self.logger = ranni_logger.bind(module="stt")
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def start(self):
        try:
            if self.device == "auto":
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            self.logger.info(f"STT iniciado: model={self.model_size}, device={self.device}")
            return True
        except Exception as e:
            self.logger.error(f"Error al iniciar STT: {e}")
            return False

    def transcribe(self, audio_data, sample_rate=16000):
        if not self.model:
            return ""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            segments, info = self.model.transcribe(audio_array, language="es", beam_size=5)
            text = " ".join(segment.text for segment in segments)
            self.logger.debug(f"Transcripción: {text}")
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error en transcripción: {e}")
            return ""

    def transcribe_file(self, filepath):
        if not self.model:
            return ""
        try:
            segments, info = self.model.transcribe(filepath, language="es")
            text = " ".join(segment.text for segment in segments)
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error al transcribir archivo: {e}")
            return ""
