# 🔀 QuotaRouter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/Starland9/quotarouter/actions/workflows/tests.yml/badge.svg)](https://github.com/Starland9/quotarouter/actions)

**Quota-aware LLM routing engine with automatic provider fallback.**

QuotaRouter automatically routes your LLM requests across multiple free-tier providers (Cerebras, Groq, Google AI Studio, Mistral, OpenRouter), seamlessly switching to the next provider when daily token quotas are exhausted.

## ✨ Features

- 🎯 **Smart Provider Selection**: Priority-based routing with automatic fallback
- 📊 **Quota Management**: Track daily token usage per provider with persistence
- 🚀 **Streaming Support**: Stream responses from any provider
- 💰 **Multi-Provider**: 6 providers included (2.5B+ tokens/day combined)
- 🔄 **Auto-Fallback**: Seamlessly switch providers on quota exhaustion
- 📈 **RPM Rate Limiting**: Respect provider rate limits automatically
- 💾 **Quota Persistence**: Track quotas across sessions
- 🧪 **Production-Ready**: Type hints, logging, error handling

## 🚀 Quick Start

### Installation

```bash
pip install quotarouter
```

Or from source:

```bash
git clone https://github.com/Starland9/quotarouter
cd quotarouter
pip install -e ".[dev]"
```

### Setup API Keys

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Add your API keys:

| Provider | Free Tier | Get Key |
|----------|-----------|---------|
| **Cerebras** | 1M tokens/day | [console.cerebras.ai](https://console.cerebras.ai) |
| **Groq** | 500K tokens/day | [console.groq.com](https://console.groq.com) |
| **Google AI Studio** | 480K tokens/day | [aistudio.google.com](https://aistudio.google.com) |
| **Mistral** | 1B tokens/month | [console.mistral.ai](https://console.mistral.ai) |
| **OpenRouter** | 200K tokens/day | [openrouter.ai](https://openrouter.ai) |
| **Alibaba DashScope** | Custom | [dashscope.aliyun.com](https://dashscope.aliyun.com) |
router = FreeRouter()

# Simple completion
response = router.complete("Explain quantum computing in simple terms")
print(response)
```

### Streaming

```python
from quotarouter import FreeRouter

router = FreeRouter()

# Stream response
for chunk in router.complete_stream("Write a 500-word essay on AI"):
    print(chunk, end="", flush=True)
```

### Check Quota Status

```python
from quotarouter import FreeRouter

router = FreeRouter()

# Get detailed status
status = router.status()
print(status)
# Output:
# {
#   "session": {"requests": 5, "tokens": 2450, "fallbacks": 0},
#   "providers": [
#     {
#       "name": "Cerebras",
#       "tokens_remaining": 998000,
#       "tokens_limit": 1000000,
#       "pct_used": 0.2,
#       "exhausted": false,
#       ...
#     }
#   ]
# }
```

## 📚 Advanced Usage

### Custom Provider Configuration

```python
from quotarouter import FreeRouter, ProviderConfig

# Define custom providers
custom_providers = [
    ProviderConfig(
        id="my-provider",
        name="My Custom Provider",
        model="llama-2-70b",
        daily_token_limit=5_000_000,
        rpm_limit=100,
        priority=1,
        api_key_env="MY_PROVIDER_API_KEY",
        base_url="https://api.myprovider.com/v1",
        flag="🌍",
    ),
]

router = FreeRouter(providers=custom_providers)
```

### Custom Quota Storage

```python
from quotarouter import FreeRouter
from quotarouter.storage import InMemoryQuotaStorage

# Use in-memory storage (useful for testing)
storage = InMemoryQuotaStorage()
router = FreeRouter(storage=storage)
```

### Long Task Processing

Split large tasks across providers:

```python
from quotarouter import FreeRouter

router = FreeRouter()

# Break task into chunks
chunks = [
    "Summarize chapter 1 of...",
    "Summarize chapter 2 of...",
    "Summarize chapter 3 of...",
]

# Each chunk auto-routes to available provider
responses = []
for i, chunk in enumerate(chunks):
    response = router.complete(chunk)
    responses.append(response)
    print(f"[{i+1}/{len(chunks)}] ✓")
```

### System Prompts & History

```python
from quotarouter import FreeRouter

router = FreeRouter()

system = "You are a programming expert. Respond concisely in French."

history = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a high-level programming language..."},
]

response = router.complete(
    prompt="Explain decorators in Python",
    system=system,
    history=history,
    max_tokens=2048,
)
print(response)
```

## 🏗️ Architecture

### Design Principles

FreeRouter is built with **SOLID principles** for maintainability and extensibility:

```
quotarouter/
├── core/              # Router logic & type definitions
├── providers/         # API adapters (OpenAI-compatible)
├── config/            # Provider registry & configuration
└── storage/           # Quota persistence (JSON, in-memory)
```

### Class Diagram

```
┌─────────────────────┐
│   FreeRouter        │ ◄─── Main entry point
│  - complete()       │
│  - complete_stream()│
└──────────┬──────────┘
           │ uses
           ▼
┌─────────────────────────────┐
│  ProviderAdapter (ABC)       │ ◄─── Extensible interface
│  - complete()               │
│  - complete_stream()        │
└──────────┬──────────────────┘
           │ implements
           ▼
┌──────────────────────────────┐
│ OpenAICompatibleAdapter      │ ◄─── Works with all OpenAI-compatible APIs
│ - complete()                 │
│ - complete_stream()          │
└──────────────────────────────┘

┌─────────────────────┐
│ ProviderConfig      │ ◄─── Configuration value object
│ - is_exhausted      │
│ - is_configured     │
└─────────────────────┘

┌─────────────────────────────┐
│  QuotaStorage (ABC)         │ ◄─── Pluggable persistence
│  - load_quotas()            │
│  - save_quotas()            │
└──────────┬──────────────────┘
           │ implements
           ├────────────────────┬─────────────────────┐
           ▼                    ▼                     ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ JSONStorage  │    │ InMemStorage │    │  (Custom)    │
    └──────────────┘    └──────────────┘    └──────────────┘
```

## 🔌 Extending FreeRouter

### Add a New Provider

```python
from quotarouter import ProviderConfig, FreeRouter

new_provider = ProviderConfig(
    id="your-provider",
    name="Your Provider",
    model="your-model",
    daily_token_limit=1_000_000,
    rpm_limit=60,
    priority=10,
    api_key_env="YOUR_API_KEY",
    base_url="https://api.yourprovider.com/v1",
    flag="🌐",
)

router = FreeRouter(providers=[new_provider])
```

### Custom Adapter

```python
from quotarouter.core import ProviderAdapter, ProviderConfig
from typing import Iterator

class MyCustomAdapter(ProviderAdapter):
    def complete(self, provider: ProviderConfig, messages: list[dict], max_tokens: int) -> tuple[str, int]:
        # Your implementation
        pass

    def complete_stream(self, provider: ProviderConfig, messages: list[dict], max_tokens: int) -> Iterator[str]:
        # Your implementation
        pass

router = FreeRouter(adapter=MyCustomAdapter())
```

## 📊 Quota Tracking

FreeRouter automatically persists quotas to `~/.quotarouter_quotas.json`:

```json
{
  "date": "2024-04-24",
  "providers": {
    "cerebras": 50000,
    "groq": 25000,
    "google": 0,
    "mistral": 100000,
    "openrouter": 10000
  }
}
```

Quotas automatically reset each day at midnight.

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=quotarouter --cov-report=html

# Code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 🐛 Error Handling

```python
from quotarouter import FreeRouter

router = FreeRouter()

try:
    response = router.complete("Your prompt")
except RuntimeError as e:
    if "exhausted" in str(e):
        print("All providers exhausted for today")
    else:
        raise
except Exception as e:
    print(f"API error: {e}")
```

## 📖 Documentation

Full API documentation is available in [docs/](docs/):

- [API Reference](docs/api.md)
- [Configuration Guide](docs/config.md)
- [Examples](examples/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [Cerebras](https://www.cerebras.ai/) - Llama 3.1 70B
- [Groq](https://groq.com/) - Ultra-fast inference
- [Google AI Studio](https://aistudio.google.com/) - Gemini models
- [Mistral AI](https://mistral.ai/) - Open models
- [OpenRouter](https://openrouter.ai/) - Unified API
- [Alibaba DashScope](https://dashscope.aliyun.com/) - Qwen models

## 📧 Contact

Have questions or feedback? Open an [Issue](https://github.com/Starland9/quotarouter/issues) or [Discussion](https://github.com/Starland9/quotarouter/discussions).

## 🗺️ Roadmap

- [ ] Support for additional providers (Claude, GPT-4, etc.)
- [ ] Web dashboard for quota monitoring
- [ ] Advanced scheduling and load balancing
- [ ] Caching for identical prompts
- [ ] Cost tracking and analytics
- [ ] CLI tool (`quotarouter` command)

---

**Made with ❤️ for the open source community**
