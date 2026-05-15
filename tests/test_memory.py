import pytest
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.nlp.context import ContextMemory

@pytest.fixture
def memory():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    mem = ContextMemory(db_path)
    yield mem
    Path(db_path).unlink(missing_ok=True)

def test_save_and_retrieve(memory):
    memory.save_interaction("hola", "Hola, soy RANNI", "conversation")
    history = memory.get_recent_history(10)
    assert len(history) == 1
    assert history[0]["user"] == "hola"
    assert history[0]["assistant"] == "Hola, soy RANNI"

def test_stats(memory):
    memory.save_interaction("test", "respuesta", "test")
    stats = memory.get_stats()
    assert stats["total_interactions"] == 1
