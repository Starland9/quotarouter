"""
CLI commands for QuotaRouter.

Each module in this package provides a single CLI command.
"""

from .status import status_command
from .complete import complete_command
from .stream import stream_command
from .config import config_command
from .reset import reset_command
from .book import book_command
from .api import api_command

# Import qwen command if available
try:
    from .qwen_command import app as qwen_command
except ImportError:
    qwen_command = None

__all__ = [
    "status_command",
    "complete_command",
    "stream_command",
    "config_command",
    "reset_command",
    "book_command",
    "api_command",
    "qwen_command",
]
