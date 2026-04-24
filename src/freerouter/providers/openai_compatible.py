"""
Provider adapters for communicating with LLM APIs.

Each adapter implements the ProviderAdapter interface for a specific API format.
Currently supports OpenAI-compatible APIs (Groq, Cerebras, Mistral, etc).
"""

from __future__ import annotations

import logging
from typing import Iterator

from ..core.types import ProviderAdapter, ProviderConfig

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Fast token estimation using character count.

    Approximate: ~4 characters per token.
    Used when actual token counts aren't available.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    return max(1, len(text) // 4)


class OpenAICompatibleAdapter(ProviderAdapter):
    """
    Adapter for OpenAI-compatible APIs.

    Works with: Groq, Cerebras, Mistral, OpenRouter, and any OpenAI-compatible endpoint.

    This adapter abstracts API communication logic and can be swapped
    for testing or alternative implementations without changing the router.
    """

    def __init__(self):
        self._client = None
        self._openai_version = None

    def _get_client(self, provider: ProviderConfig):
        """
        Lazily initialize OpenAI client.

        Args:
            provider: Provider configuration with API key and base URL

        Returns:
            Configured OpenAI client

        Raises:
            ImportError: If openai library not installed
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library required. Install with: pip install openai"
            )

        return OpenAI(api_key=provider.api_key, base_url=provider.base_url)

    def complete(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> tuple[str, int]:
        """
        Send a completion request.

        Args:
            provider: Provider configuration
            messages: OpenAI-compatible messages
            max_tokens: Maximum response tokens

        Returns:
            Tuple of (response_text, tokens_used)

        Raises:
            Various OpenAI exceptions for API errors
        """
        provider.wait_for_rpm()

        client = self._get_client(provider)

        resp = client.chat.completions.create(
            model=provider.model,
            messages=messages,
            max_tokens=max_tokens,
        )

        text = resp.choices[0].message.content or ""

        # Use actual token count if available, else estimate
        tokens = resp.usage.total_tokens if resp.usage else estimate_tokens(text)

        provider.record_request(tokens)

        logger.debug(
            f"[{provider.name}] Completion: {tokens} tokens used "
            f"({provider.tokens_remaining} remaining)"
        )

        return text, tokens

    def complete_stream(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> Iterator[str]:
        """
        Stream a completion response.

        Args:
            provider: Provider configuration
            messages: OpenAI-compatible messages
            max_tokens: Maximum response tokens

        Yields:
            Text chunks as they arrive

        Raises:
            Various OpenAI exceptions for API errors
        """
        provider.wait_for_rpm()

        client = self._get_client(provider)

        total_tokens = 0

        with client.chat.completions.create(
            model=provider.model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                total_tokens += estimate_tokens(delta)
                yield delta

        provider.record_request(total_tokens)

        logger.debug(
            f"[{provider.name}] Stream: {total_tokens} tokens used "
            f"({provider.tokens_remaining} remaining)"
        )
