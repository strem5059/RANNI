from enum import Enum

class RanniEvent:
    def __init__(self, event_type, data=None, source="system"):
        self.event_type = event_type
        self.data = data or {}
        self.source = source

    def to_dict(self):
        return {"type": self.event_type, "data": self.data, "source": self.source}


class AssistantState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class UIEvent:
    SPHERE_PULSE = "sphere_pulse"
    SPHERE_COLOR = "sphere_color"
    HUD_MESSAGE = "hud_message"
    PARTICLE_BURST = "particle_burst"
    RING_ACTIVATE = "ring_activate"
    STATE_CHANGE = "state_change"
