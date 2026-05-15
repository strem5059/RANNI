import sys
from pathlib import Path
from loguru import logger as _base_logger

_logger = _base_logger
_logger.remove()

_logger.add(
    sys.stderr,
    format="<g>{time:HH:mm:ss}</g> | <lvl>{level:<8}</lvl> | <c>{extra[module]:<12}</c> | {message}",
    level="INFO",
    colorize=True,
)

_logger.add(
    Path(__file__).parent.parent.parent / "data" / "ranni.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {extra[module]:<12} | {message}",
    level="DEBUG",
)

ranni_logger = _logger
