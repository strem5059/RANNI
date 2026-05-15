from core.utils.logger import ranni_logger

class IntentParser:
    def __init__(self):
        self.logger = ranni_logger.bind(module="intents")

    def parse(self, llm_response):
        intent = llm_response.get("intent", "conversation")
        params = llm_response.get("params", {})
        response_text = llm_response.get("response", "")
        confidence = llm_response.get("confidence", 0.0)
        return {
            "intent": intent,
            "params": params,
            "response": response_text,
            "confidence": confidence,
            "raw": llm_response
        }

    # Fallbacks rápidos para intenciones comunes sin LLM
    def quick_parse(self, text):
        text_lower = text.lower().strip()
        rules = [
            (r"^(abre|abrir|inicia|lanzar|ejecutar)\s+(.+)", "open_application", "name"),
            (r"^(cierra|cerrar|matar|terminar)\s+(.+)", "close_application", "name"),
            (r"^(hora|fecha|qué hora|qué día)", "time_date", {}),
            (r"^(sube|subir|aumentar)\s+(volumen|el volumen)", "volume_up", {"amount": 10}),
            (r"^(baja|bajar|disminuir|reducir)\s+(volumen|el volumen)", "volume_down", {"amount": 10}),
            (r"^(silencio|mutear|silenciar)", "volume_mute", {}),
            (r"^(bloquear|bloquea)", "lock_system", {}),
            (r"^(apagar|apaga)", "shutdown", {}),
            (r"^(reiniciar|reinicia)", "restart", {}),
        ]
        import re
        for pattern, intent_name, param_key in rules:
            match = re.match(pattern, text_lower)
            if match:
                if isinstance(param_key, dict):
                    return {"intent": intent_name, "params": param_key, "confidence": 0.8}
                return {"intent": intent_name, "params": {param_key: match.group(2).strip()}, "confidence": 0.8}
        return None
