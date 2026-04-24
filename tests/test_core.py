"""Unit tests for FreeRouter core functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from freerouter.core.types import (
    ProviderConfig,
    CompletionRequest,
    CompletionResponse,
)
from freerouter.core.router import FreeRouter
from freerouter.storage import InMemoryQuotaStorage
from freerouter.providers import OpenAICompatibleAdapter


class TestProviderConfig:
    """Test ProviderConfig value object."""

    def test_create_provider(self):
        """Test creating a provider config."""
        provider = ProviderConfig(
            id="test",
            name="Test Provider",
            model="test-model",
            daily_token_limit=1000,
            rpm_limit=10,
            priority=1,
            api_key_env="TEST_API_KEY",
            base_url="https://api.test.com",
        )

        assert provider.id == "test"
        assert provider.name == "Test Provider"
        assert provider.tokens_remaining == 1000

    def test_tokens_remaining(self):
        """Test token remaining calculation."""
        provider = ProviderConfig(
            id="test",
            name="Test",
            model="test",
            daily_token_limit=1000,
            rpm_limit=10,
            priority=1,
            api_key_env="KEY",
            base_url="https://test.com",
        )

        provider.tokens_used_today = 300
        assert provider.tokens_remaining == 700

    def test_is_exhausted(self):
        """Test exhaustion detection."""
        provider = ProviderConfig(
            id="test",
            name="Test",
            model="test",
            daily_token_limit=1000,
            rpm_limit=10,
            priority=1,
            api_key_env="KEY",
            base_url="https://test.com",
        )

        assert not provider.is_exhausted

        provider.tokens_used_today = 1000
        assert provider.is_exhausted

    def test_reset(self):
        """Test quota reset."""
        provider = ProviderConfig(
            id="test",
            name="Test",
            model="test",
            daily_token_limit=1000,
            rpm_limit=10,
            priority=1,
            api_key_env="KEY",
            base_url="https://test.com",
        )

        provider.tokens_used_today = 500
        provider.reset()

        assert provider.tokens_used_today == 0
        assert provider.tokens_remaining == 1000


class TestCompletionRequest:
    """Test CompletionRequest."""

    def test_build_messages(self):
        """Test message building."""
        req = CompletionRequest(
            prompt="Hello",
            system="You are helpful",
        )

        messages = req.build_messages()

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_build_messages_with_history(self):
        """Test message building with history."""
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]

        req = CompletionRequest(
            prompt="How are you?",
            history=history,
        )

        messages = req.build_messages()

        assert len(messages) == 4
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hi"


class TestFreeRouter:
    """Test FreeRouter main class."""

    def create_test_providers(self):
        """Create test providers."""
        return [
            ProviderConfig(
                id="test1",
                name="Test Provider 1",
                model="test-model",
                daily_token_limit=1000,
                rpm_limit=10,
                priority=1,
                api_key_env="TEST_API_KEY_1",
                base_url="https://api.test.com",
            ),
            ProviderConfig(
                id="test2",
                name="Test Provider 2",
                model="test-model-2",
                daily_token_limit=2000,
                rpm_limit=20,
                priority=2,
                api_key_env="TEST_API_KEY_2",
                base_url="https://api.test2.com",
            ),
        ]

    def test_router_initialization(self):
        """Test router initialization."""
        providers = self.create_test_providers()
        storage = InMemoryQuotaStorage()

        router = FreeRouter(
            providers=providers,
            storage=storage,
            verbose=False,
        )

        assert len(router.providers) == 2
        assert router.providers[0].priority == 1  # Sorted by priority

    def test_available_providers(self):
        """Test provider availability filtering."""
        providers = self.create_test_providers()
        storage = InMemoryQuotaStorage()

        router = FreeRouter(
            providers=providers,
            storage=storage,
            verbose=False,
        )

        # Without API keys, providers not available
        available = router._available_providers()
        assert len(available) == 0

        # Mock as configured by setting API key
        with patch.dict("os.environ", {"TEST_API_KEY_1": "fake-key"}):
            available = router._available_providers()
            assert len(available) == 1

    def test_select_provider(self):
        """Test provider selection."""
        providers = self.create_test_providers()
        storage = InMemoryQuotaStorage()

        router = FreeRouter(
            providers=providers,
            storage=storage,
            verbose=False,
        )

        # No providers available
        selected = router._select_provider()
        assert selected is None

        # Mock first provider as available by setting API key
        with patch.dict("os.environ", {"TEST_API_KEY_1": "fake-key"}):
            selected = router._select_provider()
            assert selected is not None
            assert selected.id == "test1"

    def test_quota_exhaustion(self):
        """Test quota exhaustion detection."""
        providers = self.create_test_providers()
        storage = InMemoryQuotaStorage()

        router = FreeRouter(
            providers=providers,
            storage=storage,
            verbose=False,
        )

        # Exhaust first provider
        providers[0].tokens_used_today = 1000
        assert providers[0].is_exhausted

    def test_status(self):
        """Test status reporting."""
        providers = self.create_test_providers()
        storage = InMemoryQuotaStorage()

        router = FreeRouter(
            providers=providers,
            storage=storage,
            verbose=False,
        )

        status = router.status()

        assert "session" in status
        assert "providers" in status
        assert status["session"]["requests"] == 0
        assert status["session"]["tokens"] == 0
        assert len(status["providers"]) == 2

    def test_reset_quotas(self):
        """Test quota reset."""
        providers = self.create_test_providers()
        storage = InMemoryQuotaStorage()

        router = FreeRouter(
            providers=providers,
            storage=storage,
            verbose=False,
        )

        # Use some tokens
        providers[0].tokens_used_today = 500

        # Reset
        router.reset_quotas()

        assert providers[0].tokens_used_today == 0
        assert providers[1].tokens_used_today == 0


class TestQuotaStorage:
    """Test quota storage."""

    def test_in_memory_storage(self):
        """Test in-memory quota storage."""
        storage = InMemoryQuotaStorage()

        # Save quotas
        quotas = {"provider1": 100, "provider2": 200}
        storage.save_quotas(quotas)

        # Load quotas
        loaded = storage.load_quotas()
        assert loaded == quotas

    def test_in_memory_storage_isolation(self):
        """Test that in-memory storage doesn't persist across instances."""
        storage1 = InMemoryQuotaStorage()
        storage1.save_quotas({"provider": 100})

        storage2 = InMemoryQuotaStorage()
        loaded = storage2.load_quotas()

        # Different instances should be isolated
        assert loaded == {}


class TestOpenAICompatibleAdapter:
    """Test OpenAI-compatible adapter."""

    def test_adapter_creation(self):
        """Test adapter creation."""
        adapter = OpenAICompatibleAdapter()
        assert adapter is not None

    def test_complete(self):
        """Test completion request."""
        # Create adapter
        adapter = OpenAICompatibleAdapter()

        # Create provider
        provider = ProviderConfig(
            id="test",
            name="Test",
            model="test",
            daily_token_limit=1000,
            rpm_limit=10,
            priority=1,
            api_key_env="TEST_KEY",
            base_url="https://test.com",
        )

        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 50
        mock_client.chat.completions.create.return_value = mock_response

        # Patch OpenAI at the openai module level
        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai_class.return_value = mock_client

            # Mock API key
            with patch.dict("os.environ", {"TEST_KEY": "fake-key"}):
                text, tokens = adapter.complete(provider, [], 100)

            assert text == "Test response"
            assert tokens == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
