# FreeRouter Architecture & Design

## Overview

FreeRouter is built with **SOLID principles** to ensure maintainability, testability, and extensibility.

## Design Principles Applied

### 1. Single Responsibility Principle (SRP)

Each class has **one reason to change**:

- **`ProviderConfig`**: Represents provider metadata and quota state
- **`FreeRouter`**: Orchestrates routing logic and provider selection
- **`ProviderAdapter`**: Handles API communication
- **`QuotaStorage`**: Manages quota persistence
- **`CompletionRequest`**: Encapsulates request parameters

### 2. Open/Closed Principle (OCP)

The code is **open for extension, closed for modification**:

```python
# Easy to add new providers without modifying FreeRouter
custom_provider = ProviderConfig(id="new-provider", ...)
router = FreeRouter(providers=[custom_provider])

# Easy to add new adapters without modifying FreeRouter
custom_adapter = MyCustomAdapter()
router = FreeRouter(adapter=custom_adapter)
```

### 3. Liskov Substitution Principle (LSP)

**Subtypes can be substituted for base types**:

```python
class ProviderAdapter(ABC):
    @abstractmethod
    def complete(self, ...): ...

# Any implementation can be used interchangeably
adapter1 = OpenAICompatibleAdapter()
adapter2 = AzureOpenAIAdapter()  # Future
router1 = FreeRouter(adapter=adapter1)
router2 = FreeRouter(adapter=adapter2)
```

### 4. Interface Segregation Principle (ISP)

**Clients depend on focused interfaces, not bloated ones**:

```python
# Router depends on ProviderAdapter interface
# Not on implementation details of OpenAI client, HTTP requests, etc.

class ProviderAdapter(ABC):
    @abstractmethod
    def complete(self, ...): ...
    @abstractmethod
    def complete_stream(self, ...): ...
```

### 5. Dependency Inversion Principle (DIP)

**High-level modules depend on abstractions, not concrete implementations**:

```python
class FreeRouter:
    def __init__(
        self,
        adapter: ProviderAdapter = None,  # Depends on abstraction
        storage: QuotaStorage = None,     # Depends on abstraction
    ):
        # Concrete implementations injected
        self.adapter = adapter or OpenAICompatibleAdapter()
        self.storage = storage or JSONQuotaStorage()
```

## Architecture

### Layer Diagram

```
┌─────────────────────────────────┐
│      Application Layer          │
│  (Examples, CLI, Web Server)    │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│      API Layer (FreeRouter)     │
│  - Router.complete()            │
│  - Router.complete_stream()     │
└──────────────┬──────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────────┐ ┌──▼──────────────┐
│ Core Layer     │ │ Adapter Layer   │
│  - Types       │ │ - ProviderAdapter
│  - Routing     │ │ - OpenAICompat   
│  - Selection   │ └─────────────────┘
└─────┬──────────┘
      │
      └────────┬────────┐
             │        │
      ┌──────▼──┐  ┌─▼──────────┐
      │ Storage │  │ Providers  │
      │ Layer   │  │ (Config)   │
      └─────────┘  └────────────┘
```

### Module Organization

```
src/freerouter/
├── __init__.py              # Package exports
├── core/
│   ├── __init__.py
│   ├── types.py            # Data models & abstract interfaces
│   └── router.py           # Core routing logic
├── providers/
│   ├── __init__.py
│   └── openai_compatible.py # Adapter implementation
├── config/
│   ├── __init__.py
│   └── registry.py         # Provider definitions
└── storage/
    ├── __init__.py
    └── quota_manager.py    # Storage implementations
```

## Data Flow

### Completion Request Flow

```
User Code
  │
  └─> router.complete("prompt")
      │
      └─> _select_provider()
          │
          ├─> _available_providers()
          │   └─> Filter configured & not exhausted
          │
          └─> Return provider with highest priority
             │
             └─> adapter.complete(provider, messages, max_tokens)
                 │
                 ├─> provider.wait_for_rpm()
                 │
                 ├─> client.chat.completions.create(...)
                 │
                 └─> provider.record_request(tokens)
                     │
                     └─> _persist_quotas()
                         │
                         └─> storage.save_quotas(quotas)
```

### Error Handling & Fallback

```
router.complete()
  └─> adapter.complete()
      └─> (quota error)
          │
          ├─> _handle_quota_error()
          │   ├─> Mark provider as exhausted
          │   └─> _persist_quotas()
          │
          └─> Retry with next provider
              └─> router.complete() (recursive)
```

## Extension Points

### Adding a New Provider

```python
from freerouter import FreeRouter, ProviderConfig

# 1. Define provider config
provider = ProviderConfig(
    id="claude",
    name="Anthropic Claude",
    model="claude-3-opus",
    daily_token_limit=1_000_000,
    rpm_limit=50,
    priority=5,
    api_key_env="ANTHROPIC_API_KEY",
    base_url="https://api.anthropic.com",
)

# 2. Create router with new provider
router = FreeRouter(providers=[provider])

# 3. Done! No changes to FreeRouter needed
```

### Implementing a Custom Adapter

```python
from freerouter.core.types import ProviderAdapter, ProviderConfig
from typing import Iterator

class AnthropicAdapter(ProviderAdapter):
    def complete(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> tuple[str, int]:
        # Your implementation using Anthropic SDK
        pass

    def complete_stream(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> Iterator[str]:
        # Your streaming implementation
        pass

# Use with router
router = FreeRouter(adapter=AnthropicAdapter())
```

### Custom Quota Storage

```python
from freerouter.core.types import QuotaStorage

class RedisQuotaStorage(QuotaStorage):
    def __init__(self, redis_client):
        self.redis = redis_client

    def load_quotas(self) -> dict[str, int]:
        # Load from Redis
        pass

    def save_quotas(self, quotas: dict[str, int]) -> None:
        # Save to Redis
        pass

router = FreeRouter(storage=RedisQuotaStorage(redis_client))
```

## Testing Strategy

### Unit Tests

```python
# Tests focus on isolated units with mocks
def test_provider_selection():
    router = FreeRouter(providers=[...])
    with patch.object(provider, 'is_configured', True):
        selected = router._select_provider()
        assert selected == provider
```

### Integration Tests

```python
# Tests with real components (but mocked API)
def test_complete_with_fallback():
    router = FreeRouter(providers=[...])
    # Mock API but test real routing logic
    with patch('openai.OpenAI'):
        response = router.complete("test")
```

### Test Isolation

- Use `InMemoryQuotaStorage` for tests (no file I/O)
- Mock external API calls
- Reset state between tests
- Use fixtures for common setup

## Performance Considerations

### Token Estimation

```python
# Fast approximate: ~4 chars per token
# Used when actual token count unavailable
estimate = len(text) // 4
```

### Quota Caching

```python
# Quotas loaded once at startup
# Updated in-memory on each request
# Persisted to disk after each request
```

### RPM Compliance

```python
# Requests-per-minute tracked per provider
# Automatic sleep if limit exceeded
# No need for external rate-limiter
```

## Security Considerations

### API Key Management

```python
# Keys stored in environment variables
# Never logged or printed
# Passed directly to OpenAI client
```

### Quota File Permissions

```python
# ~/.freerouter_quotas.json contains no sensitive data
# Only stores token counts
# Safe to commit to version control (in .gitignore)
```

## Future Enhancements

1. **Advanced Load Balancing**
   - Round-robin provider selection
   - Weighted selection based on provider speed
   - Cost-aware routing

2. **Analytics & Monitoring**
   - Request latency tracking
   - Provider performance metrics
   - Cost breakdown by provider

3. **Caching Layer**
   - Cache identical requests
   - Reduce quota usage
   - Improve response time

4. **More Adapters**
   - Azure OpenAI
   - Anthropic Claude
   - Custom providers

5. **Web Dashboard**
   - Visualize quota usage
   - Monitor providers in real-time
   - Manage configuration
