"""
Core routing engine.

Main FreeRouter class that orchestrates provider selection,
quota management, and request routing.

Follows Single Responsibility Principle - this class focuses on routing logic
and delegates storage, API communication to specialized components.
"""

from __future__ import annotations

import logging
from typing import Iterator, Optional

from ..core.types import (
    CompletionRequest,
    ProviderAdapter,
    ProviderConfig,
    QuotaStorage,
)
from ..providers.openai_compatible import OpenAICompatibleAdapter
from ..storage.quota_manager import JSONQuotaStorage

logger = logging.getLogger(__name__)


class FreeRouter:
    """
    Quota-aware LLM routing engine.

    Automatically routes requests across multiple LLM providers,
    switching to next provider when quota is exhausted.

    Features:
        - Priority-based provider selection
        - Automatic fallback on quota exhaustion
        - Token quota tracking and persistence
        - RPM rate limiting
        - Optional verbose logging

    Example:
        >>> router = FreeRouter()
        >>> response = router.complete("Explain quantum computing")
        >>> print(response)

        >>> # With streaming
        >>> for chunk in router.complete_stream("Long text..."):
        ...     print(chunk, end="", flush=True)
    """

    def __init__(
        self,
        providers: Optional[list[ProviderConfig]] = None,
        adapter: Optional[ProviderAdapter] = None,
        storage: Optional[QuotaStorage] = None,
        verbose: bool = True,
    ):
        """
        Initialize router with providers and adapters.

        Args:
            providers: List of ProviderConfig. Uses defaults if None.
            adapter: Communication adapter. Uses OpenAICompatibleAdapter if None.
            storage: Quota storage backend. Uses JSONQuotaStorage if None.
            verbose: Whether to print status information

        Raises:
            ValueError: If no providers provided
        """
        from ..config.registry import DEFAULT_PROVIDERS

        if providers is None:
            providers = DEFAULT_PROVIDERS

        if not providers:
            raise ValueError("At least one provider must be configured")

        # Sort by priority (lower number = higher priority)
        self.providers = sorted(providers, key=lambda p: p.priority)

        self.adapter = adapter or OpenAICompatibleAdapter()
        self.storage = storage or JSONQuotaStorage()
        self.verbose = verbose

        # Statistics
        self._total_tokens = 0
        self._total_requests = 0
        self._fallback_count = 0

        # Load persisted quotas
        self._restore_quotas()

        if self.verbose:
            self._print_status()

    # ── Quota Management ─────────────────────────────────────────────

    def _restore_quotas(self) -> None:
        """Load quota data from storage into providers."""
        quotas = self.storage.load_quotas()
        for provider in self.providers:
            provider.tokens_used_today = quotas.get(provider.id, 0)

    def _persist_quotas(self) -> None:
        """Save quota data from providers to storage."""
        quotas = {p.id: p.tokens_used_today for p in self.providers}
        self.storage.save_quotas(quotas)

    # ── Provider Selection ───────────────────────────────────────────

    def _available_providers(self) -> list[ProviderConfig]:
        """Get list of available providers (configured and not exhausted)."""
        return [p for p in self.providers if p.is_configured and not p.is_exhausted]

    def _select_provider(self) -> Optional[ProviderConfig]:
        """
        Select next provider to use.

        Uses priority-based selection: returns first available provider
        ordered by priority number (ascending).

        Returns:
            ProviderConfig or None if no providers available
        """
        available = self._available_providers()
        return available[0] if available else None

    def _handle_quota_error(self, provider: ProviderConfig, error: Exception) -> bool:
        """
        Check if error is quota-related and handle it.

        Args:
            provider: Provider that had error
            error: The exception

        Returns:
            True if error is quota-related, False otherwise
        """
        error_msg = str(error).lower()
        quota_indicators = ("429", "quota", "rate", "limit", "exceeded")

        if any(k in error_msg for k in quota_indicators):
            logger.warning(f"[{provider.name}] Quota hit: {error}")
            provider.tokens_used_today = provider.daily_token_limit
            self._persist_quotas()
            self._fallback_count += 1
            return True

        return False

    # ── Public API ───────────────────────────────────────────────────

    def complete(
        self,
        prompt: str,
        system: str = "You are a helpful assistant.",
        max_tokens: int = 4096,
        history: Optional[list[dict]] = None,
    ) -> str:
        """
        Send a prompt and get response.

        Automatically falls back to next provider if quota is hit.

        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Max response tokens
            history: Previous messages for context

        Returns:
            Response text

        Raises:
            RuntimeError: If all providers exhausted
        """
        request = CompletionRequest(prompt, system, max_tokens, history)
        provider = self._select_provider()

        if not provider:
            raise RuntimeError(
                "🚫 All providers exhausted for today. "
                "Quotas reset at midnight. "
                "Add more API keys to increase available quota."
            )

        try:
            text, tokens = self.adapter.complete(
                provider,
                request.build_messages(),
                max_tokens,
            )
            self._total_tokens += tokens
            self._total_requests += 1
            self._persist_quotas()
            return text

        except Exception as e:
            if self._handle_quota_error(provider, e):
                # Retry with next provider
                return self.complete(prompt, system, max_tokens, history)
            raise

    def complete_stream(
        self,
        prompt: str,
        system: str = "You are a helpful assistant.",
        max_tokens: int = 4096,
        history: Optional[list[dict]] = None,
    ) -> Iterator[str]:
        """
        Stream a response.

        Yields text chunks. Falls back to next provider on quota hit.

        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Max response tokens
            history: Previous messages for context

        Yields:
            Response text chunks

        Raises:
            RuntimeError: If all providers exhausted
        """
        request = CompletionRequest(prompt, system, max_tokens, history)
        provider = self._select_provider()

        if not provider:
            raise RuntimeError("🚫 All providers exhausted for today.")

        try:
            total_tokens = 0
            for chunk in self.adapter.complete_stream(
                provider,
                request.build_messages(),
                max_tokens,
            ):
                total_tokens += len(chunk) // 4  # rough token estimate
                yield chunk

            self._total_tokens += total_tokens
            self._total_requests += 1
            self._persist_quotas()

        except Exception as e:
            if self._handle_quota_error(provider, e):
                # Retry with next provider
                yield from self.complete_stream(prompt, system, max_tokens, history)
            else:
                raise

    # ── Status & Reporting ───────────────────────────────────────────

    def status(self) -> dict:
        """
        Get current status of all providers.

        Returns:
            Dict with session stats and per-provider quotas
        """
        return {
            "session": {
                "requests": self._total_requests,
                "tokens": self._total_tokens,
                "fallbacks": self._fallback_count,
            },
            "providers": [
                {
                    "id": p.id,
                    "name": p.name,
                    "model": p.model,
                    "configured": p.is_configured,
                    "tokens_used": p.tokens_used_today,
                    "tokens_limit": p.daily_token_limit,
                    "tokens_remaining": p.tokens_remaining,
                    "pct_used": round(
                        p.tokens_used_today / p.daily_token_limit * 100, 1
                    ),
                    "exhausted": p.is_exhausted,
                    "priority": p.priority,
                }
                for p in self.providers
            ],
        }

    def _print_status(self) -> None:
        """Print provider status to console."""
        print("\n🔀 FreeRouter — Provider Status")
        print("─" * 52)

        configured_count = 0
        for p in self.providers:
            icon = "✅" if p.is_configured else "⚪"
            bar_fill = int(p.tokens_used_today / p.daily_token_limit * 20)
            bar = "█" * bar_fill + "░" * (20 - bar_fill)
            remaining_k = p.tokens_remaining // 1000

            print(
                f"  {icon} {p.flag} P{p.priority} {p.name:<22} [{bar}] {remaining_k}K left"
            )
            if p.is_configured:
                configured_count += 1

        print("─" * 52)
        total_remaining = sum(
            p.tokens_remaining for p in self.providers if p.is_configured
        )
        print(
            f"  🟢 {configured_count}/{len(self.providers)} configured  "
            f"|  ~{total_remaining:,} tokens available today\n"
        )

    def reset_quotas(self) -> None:
        """
        Force reset all quotas.

        Useful for testing. In production, quotas reset automatically at midnight.
        """
        for p in self.providers:
            p.reset()
        self.storage.save_quotas({})
        logger.info("✅ All quotas reset")
        if self.verbose:
            print("✅ All quotas reset")
