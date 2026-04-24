#!/usr/bin/env python3
"""
Custom provider example: Use custom provider configuration.

Shows how to define and use custom providers with FreeRouter.
"""

from quotarouter import FreeRouter, ProviderConfig


def main():
    # Define custom providers
    custom_providers = [
        ProviderConfig(
            id="groq-fast",
            name="Groq (Fast Mode)",
            model="llama-3.3-70b-versatile",
            daily_token_limit=500_000,
            rpm_limit=30,
            priority=1,  # Highest priority
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            flag="🚀",
        ),
        ProviderConfig(
            id="cerebras-backup",
            name="Cerebras (Backup)",
            model="llama3.1-70b",
            daily_token_limit=1_000_000,
            rpm_limit=30,
            priority=2,  # Fallback
            api_key_env="CEREBRAS_API_KEY",
            base_url="https://api.cerebras.ai/v1",
            flag="⚡",
        ),
    ]

    # Initialize router with custom providers
    router = FreeRouter(providers=custom_providers, verbose=True)

    print("\n🎯 Using custom providers")
    print("-" * 50)

    # Make a request
    response = router.complete("What is quantum entanglement?")

    print("\n📝 Response:")
    print(response)

    # Show which providers were used
    status = router.status()
    used_providers = [p["name"] for p in status["providers"] if p["configured"]]
    print(f"\n✅ Available providers: {', '.join(used_providers)}")


if __name__ == "__main__":
    main()
