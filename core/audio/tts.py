import subprocess
import tempfile
import wave
import pyaudio
import os
import shutil
from pathlib import Path
from core.utils.logger import ranni_logger

class TextToSpeech:
    def __init__(self, voice="es_ES-daveconroy-medium", speed=1.0, volume=0.8):
        self.logger = ranni_logger.bind(module="tts")
        self.voice = voice
        self.speed = speed
        self.volume = volume
        self.piper_path = self._find_piper()
        self.pyaudio_instance = None

    def _find_piper(self):
        paths = [
            r"C:\Program Files\Piper\piper.exe",
            r"C:\Program Files (x86)\Piper\piper.exe",
            shutil.which("piper"),
            str(Path.home() / ".local" / "bin" / "piper")
        ]
        for p in paths:
            if p and os.path.exists(p):
                return p
        self.logger.warning("Piper no encontrado en PATH")
        return "piper"

    def speak(self, text):
        if not text:
            return
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav_path = f.name
            self._synthesize(text, wav_path)
            self._play_wav(wav_path)
            os.unlink(wav_path)
        except Exception as e:
            self.logger.error(f"Error en TTS: {e}")

    def _synthesize(self, text, output_path):
        import shutil
        cmd = [
            self.piper_path,
            "--model", self.voice,
            "--output_file", output_path,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.communicate(input=text.encode("utf-8"))
        if proc.returncode != 0:
            self.logger.warning(f"Piper falló, usando síntesis básica")
            self._synthesize_fallback(text, output_path)

    def _synthesize_fallback(self, text, output_path):
        import pyttsx3
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()

    def _play_wav(self, path):
        wf = wave.open(path, "rb")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.close()
        p.terminate()
        wf.close()

    def stop(self):
        pass
