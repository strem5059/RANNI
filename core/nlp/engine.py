import json
import requests
from core.utils.logger import ranni_logger

class LLMEngine:
    def __init__(self, host="http://localhost:11434", model="llama3.2", temperature=0.3, max_tokens=512):
        self.logger = ranni_logger.bind(module="llm")
        self.host = host
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        return """Eres RANNI, un asistente virtual de escritorio con control total del sistema.
Debes responder ÚNICAMENTE con JSON en este formato exacto:
{
  "intent": "action_name",
  "params": { ... },
  "response": "texto para hablar al usuario",
  "confidence": 0.95
}

ACCIONES DISPONIBLES:
- open_application: Abre un programa. params: {name: "chrome", path: ""}
- close_application: Cierra una app. params: {name: "chrome"}
- list_windows: Lista ventanas abiertas. params: {}
- minimize_window: Minimiza ventana. params: {title: ""}
- system_info: Información del sistema. params: {type: "cpu|ram|disk"}
- read_file: Lee un archivo. params: {path: "C:\\ruta\\archivo.txt"}
- write_file: Escribe un archivo. params: {path: "", content: ""}
- list_directory: Lista directorio. params: {path: ""}
- volume_up/subir volumen: params: {amount: 10}
- volume_down/bajar volumen: params: {amount: 10}
- time_date: Fecha y hora actual. params: {}
- screenshot: Toma captura de pantalla. params: {}
- keyboard_type: Escribe texto. params: {text: ""}
- lock_system: Bloquea la PC. params: {}
- shutdown: Apaga. params: {}
- restart: Reinicia. params: {}
- sleep: Suspende. params: {}
- conversation: Respuesta general. params: {message: "texto"}

Si no puedes realizar la acción, usa intent: "conversation".
Responde SIEMPRE en español."""

    def process(self, text, context=None):
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            if context:
                for entry in context[-5:]:
                    messages.append({"role": "user", "content": entry.get("user", "")})
                    messages.append({"role": "assistant", "content": entry.get("assistant", "")})
            messages.append({"role": "user", "content": text})

            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=30
            )
            result = response.json()
            content = result.get("message", {}).get("content", "{}")
            return self._parse_response(content)
        except requests.exceptions.ConnectionError:
            self.logger.error("No se puede conectar a Ollama. ¿Está corriendo?")
            return {"intent": "conversation", "params": {"message": ""}, "response": "No puedo conectarme a mi cerebro. ¿Ollama está encendido?", "confidence": 0.0}
        except Exception as e:
            self.logger.error(f"Error en LLM: {e}")
            return {"intent": "conversation", "params": {"message": ""}, "response": "Ocurrió un error interno.", "confidence": 0.0}

    def _parse_response(self, content):
        try:
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except json.JSONDecodeError:
            self.logger.warning(f"Respuesta no es JSON válido: {content[:100]}")
            return {"intent": "conversation", "params": {"message": content}, "response": content, "confidence": 0.5}

    def health_check(self):
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
            return r.status_code == 200
        except:
            return False
