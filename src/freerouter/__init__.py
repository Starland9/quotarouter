"""
FreeRouter — Quota-Aware LLM Routing Engine

Automatically routes LLM requests across free-tier providers,
switching to the next provider when quota is exhausted.

Example:
    >>> from freerouter import FreeRouter
    >>> router = FreeRouter()
    >>> response = router.complete("Explain quantum computing")
    >>> print(response)

    >>> # Stream responses
    >>> for chunk in router.complete_stream("Tell me about black holes"):
    ...     print(chunk, end="", flush=True)
"""

from .core.router import FreeRouter
from .core.types import ProviderConfig, CompletionRequest, CompletionResponse
from .config.registry import DEFAULT_PROVIDERS, get_provider_by_id

__version__ = "0.1.0"
__author__ = "Landry Simo"

__all__ = [
    "FreeRouter",
    "ProviderConfig",
    "CompletionRequest",
    "CompletionResponse",
    "DEFAULT_PROVIDERS",
    "get_provider_by_id",
]
