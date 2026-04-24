"""
FreeRouter — Quota-Aware LLM Routing Engine

Automatically routes LLM requests across free-tier providers,
switching to the next provider when quota is exhausted.

Example:
    >>> from quotarouter import FreeRouter
    >>> router = FreeRouter()
    >>> response = router.complete("Explain quantum computing")
    >>> print(response)

    >>> # Stream responses
    >>> for chunk in router.complete_stream("Tell me about black holes"):
    ...     print(chunk, end="", flush=True)
"""

from __future__ import annotations

import os
from pathlib import Path

from .core.router import FreeRouter
from .core.types import ProviderConfig, CompletionRequest, CompletionResponse
from .config.registry import DEFAULT_PROVIDERS, get_provider_by_id


def _load_dotenv_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :]

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if not key or key in os.environ:
            continue

        os.environ[key] = value


def _load_dotenv() -> None:
    _load_dotenv_file(Path.cwd() / ".env")


_load_dotenv()


__version__ = "0.7.0"
__author__ = "Landry Simo"

__all__ = [
    "FreeRouter",
    "ProviderConfig",
    "CompletionRequest",
    "CompletionResponse",
    "DEFAULT_PROVIDERS",
    "get_provider_by_id",
]
