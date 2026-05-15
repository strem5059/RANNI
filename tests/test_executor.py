import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.system.executor import SystemExecutor

def test_executor_system_info():
    executor = SystemExecutor()
    result = executor.execute("system_info", {"type": "general"})
    assert result["success"] is True
    assert "CPU" in result["message"]

def test_executor_time_date():
    executor = SystemExecutor()
    result = executor.execute("time_date", {})
    assert result["success"] is True
    assert "Son las" in result["message"]
