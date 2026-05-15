import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.nlp.intents import IntentParser

def test_quick_parse_open():
    parser = IntentParser()
    result = parser.quick_parse("abre chrome")
    assert result is not None
    assert result["intent"] == "open_application"

def test_quick_parse_close():
    parser = IntentParser()
    result = parser.quick_parse("cierra notepad")
    assert result is not None
    assert result["intent"] == "close_application"

def test_quick_parse_time():
    parser = IntentParser()
    result = parser.quick_parse("qué hora es")
    assert result is not None
    assert result["intent"] == "time_date"

def test_quick_parse_volume_up():
    parser = IntentParser()
    result = parser.quick_parse("sube el volumen")
    assert result is not None
    assert result["intent"] == "volume_up"
