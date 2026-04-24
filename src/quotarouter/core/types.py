"""
Core types and data models for FreeRouter.

Defines the fundamental data structures used throughout the application,
following clean architecture principles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Optional, Protocol
import time


@dataclass
class ProviderConfig:
    """
    Configuration for an LLM provider.

    Handles provider metadata, API credentials, and quota limits.
    This is a value object with no business logic.
    """

    id: str
    name: str
    model: str
    daily_token_limit: int  # tokens/day
    rpm_limit: int  # requests per minute
    priority: int  # lower = higher priority
    api_key_env: str  # environment variable name
    base_url: str
    flag: str = "🌐"

    # Runtime state (should be managed by quota manager, not here)
    tokens_used_today: int = field(default=0, repr=False)
    requests_this_minute: int = field(default=0, repr=False)
    last_minute_reset: float = field(default_factory=time.time, repr=False)

    @property
    def tokens_remaining(self) -> int:
        """Calculate remaining tokens for today."""
        return max(0, self.daily_token_limit - self.tokens_used_today)

    @property
    def is_exhausted(self) -> bool:
        """Check if daily quota is exhausted."""
        return self.tokens_remaining == 0

    @property
    def is_configured(self) -> bool:
        """Check if provider has API key configured."""
        import os

        return bool(os.getenv(self.api_key_env))

    @property
    def api_key(self) -> Optional[str]:
        """Get API key from environment."""
        import os

        return os.getenv(self.api_key_env)

    def check_rpm(self) -> bool:
        """
        Check if we can make a request respecting RPM limit.

        Returns True if request can proceed, False if limit reached.
        """
        now = time.time()
        if now - self.last_minute_reset >= 60:
            self.requests_this_minute = 0
            self.last_minute_reset = now
        return self.requests_this_minute < self.rpm_limit

    def record_request(self, tokens_used: int) -> None:
        """Record that a request was made with given token count."""
        self.tokens_used_today += tokens_used
        self.requests_this_minute += 1

    def wait_for_rpm(self) -> None:
        """
        Block until RPM window resets if necessary.

        This ensures we respect the requests-per-minute limit.
        """
        if not self.check_rpm():
            wait = 60 - (time.time() - self.last_minute_reset)
            time.sleep(max(0, wait + 0.5))
            self.requests_this_minute = 0
            self.last_minute_reset = time.time()

    def reset(self) -> None:
        """Reset daily token counter (called at midnight)."""
        self.tokens_used_today = 0


@dataclass
class CompletionRequest:
    """
    Request for LLM completion.

    Encapsulates all parameters needed for a completion request.
    """

    prompt: str
    system: str = "You are a helpful assistant."
    max_tokens: int = 4096
    history: Optional[list[dict]] = None

    def build_messages(self) -> list[dict]:
        """Convert request to OpenAI-compatible messages format."""
        messages = [{"role": "system", "content": self.system}]
        if self.history:
            messages.extend(self.history)
        messages.append({"role": "user", "content": self.prompt})
        return messages


@dataclass
class CompletionResponse:
    """
    Response from LLM completion.

    Encapsulates response data and metadata.
    """

    text: str
    tokens_used: int
    provider_id: str
    provider_name: str


class ProviderAdapter(ABC):
    """
    Abstract base for provider communication adapters.

    Follows Interface Segregation Principle - consumers depend on this interface,
    not on concrete implementations. This allows swapping providers without
    changing router code.
    """

    @abstractmethod
    def complete(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> tuple[str, int]:
        """
        Send completion request and return response.

        Args:
            provider: Provider configuration
            messages: OpenAI-compatible message format
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (response_text, tokens_used)

        Raises:
            Exception: For API errors, quota exceeded, etc.
        """
        ...

    @abstractmethod
    def complete_stream(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> Iterator[str]:
        """
        Stream completion response.

        Args:
            provider: Provider configuration
            messages: OpenAI-compatible message format
            max_tokens: Maximum tokens in response

        Yields:
            Text chunks as they arrive

        Raises:
            Exception: For API errors, quota exceeded, etc.
        """
        ...


class QuotaStorage(ABC):
    """
    Abstract interface for quota persistence.

    Dependency Inversion Principle: Router depends on this interface,
    not on a specific storage implementation (file, database, etc).
    """

    @abstractmethod
    def load_quotas(self) -> dict[str, int]:
        """Load persisted quota data by provider ID."""
        ...

    @abstractmethod
    def save_quotas(self, quotas: dict[str, int]) -> None:
        """Persist quota data by provider ID."""
        ...


class ProviderSelector(Protocol):
    """
    Protocol for provider selection strategies.

    Enables different strategies for selecting which provider to use
    (priority-based, round-robin, load-balancing, etc).
    """

    def select(self, providers: list[ProviderConfig]) -> Optional[ProviderConfig]:
        """
        Select a provider from available options.

        Args:
            providers: List of available providers

        Returns:
            Selected provider or None if no suitable provider found
        """
        ...
