"""
Provider registry and configuration.

Defines default providers and their quotas.
Easy to extend with additional providers.
"""

from __future__ import annotations

from ..core.types import ProviderConfig


DEFAULT_PROVIDERS: list[ProviderConfig] = [
    ProviderConfig(
        id="cerebras",
        name="Cerebras",
        model="llama3.1-70b",
        daily_token_limit=1_000_000,
        rpm_limit=30,
        priority=1,
        api_key_env="CEREBRAS_API_KEY",
        base_url="https://api.cerebras.ai/v1",
        flag="🇺🇸",
    ),
    ProviderConfig(
        id="groq",
        name="Groq",
        model="llama-3.3-70b-versatile",
        daily_token_limit=500_000,
        rpm_limit=30,
        priority=2,
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        flag="🇺🇸",
    ),
    ProviderConfig(
        id="google",
        name="Google AI Studio",
        model="gemini-2.0-flash",
        daily_token_limit=480_000,
        rpm_limit=15,
        priority=3,
        api_key_env="GOOGLE_AI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        flag="🇺🇸",
    ),
    ProviderConfig(
        id="mistral",
        name="Mistral AI",
        model="mistral-large-latest",
        daily_token_limit=33_000_000,  # 1B/month ÷ 30 days
        rpm_limit=60,
        priority=4,
        api_key_env="MISTRAL_API_KEY",
        base_url="https://api.mistral.ai/v1",
        flag="🇫🇷",
    ),
    ProviderConfig(
        id="openrouter",
        name="OpenRouter",
        model="deepseek/deepseek-r1:free",
        daily_token_limit=200_000,
        rpm_limit=20,
        priority=5,
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        flag="🇺🇸",
    ),
    ProviderConfig(
        id="alibaba",
        name="Alibaba DashScope",
        model="qwen-turbo",
        daily_token_limit=1_000_000,
        rpm_limit=60,
        priority=6,
        api_key_env="ALIBABA_API_KEY",
        base_url="https://ws-6rq790chy8pc9lkq.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
        flag="🇨🇳",
    ),
]


def get_provider_by_id(provider_id: str) -> ProviderConfig | None:
    """
    Look up a provider by ID.

    Args:
        provider_id: Provider ID (e.g., "groq", "mistral")

    Returns:
        Provider config or None if not found
    """
    for provider in DEFAULT_PROVIDERS:
        if provider.id == provider_id:
            return provider
    return None
