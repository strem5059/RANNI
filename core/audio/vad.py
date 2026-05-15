import numpy as np
from core.utils.logger import ranni_logger

class VoiceActivityDetector:
    def __init__(self, threshold=0.5, sample_rate=16000, frame_duration_ms=30):
        self.logger = ranni_logger.bind(module="vad")
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self._vad_model = None

    def start(self):
        try:
            import silero_vad
            self._vad_model = silero_vad.load_silero_vad()
            self.logger.info("VAD iniciado (Silero)")
            return True
        except ImportError:
            self.logger.warning("Silero VAD no disponible, usando VAD simple")
            return True
        except Exception as e:
            self.logger.error(f"Error iniciando VAD: {e}")
            return False

    def is_speech(self, audio_data):
        if self._vad_model:
            import silero_vad
            try:
                audio_float = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                return silero_vad.get_speech_timestamps(
                    audio_float, self._vad_model,
                    threshold=self.threshold
                )
            except:
                pass
        energy = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(energy ** 2))
        return rms > 500

    def record_until_silence(self, audio_stream, max_duration=10, silence_duration=1.5):
        frames = []
        silent_chunks = 0
        silence_chunks_needed = int(silence_duration * self.sample_rate / self.frame_size)
        max_chunks = int(max_duration * self.sample_rate / self.frame_size)
        recording = False

        for _ in range(max_chunks):
            chunk = audio_stream.read(self.frame_size, exception_on_overflow=False)
            if self.is_speech(chunk):
                if not recording:
                    recording = True
                frames.append(chunk)
                silent_chunks = 0
            elif recording:
                frames.append(chunk)
                silent_chunks += 1
                if silent_chunks >= silence_chunks_needed:
                    break
            if not recording:
                continue

        return b"".join(frames) if frames else b""
