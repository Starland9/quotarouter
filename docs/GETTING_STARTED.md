# Getting Started with FreeRouter

## 🚀 5-Minute Quick Start

### 1. Install

```bash
pip install quotarouter
```

### 2. Get API Keys

Get free API keys from these providers (5 total, ~1.5B tokens/day combined):

| Provider | Time | Tokens/Day | Get Key |
|----------|------|-----------|---------|
| **Groq** | ~5 min | 500K | [console.groq.com](https://console.groq.com) |
| **Cerebras** | ~5 min | 1M | [console.cerebras.ai](https://console.cerebras.ai) |
| **Google AI** | ~2 min | 480K | [aistudio.google.com](https://aistudio.google.com) |
| **Mistral** | ~10 min | 1B/month | [console.mistral.ai](https://console.mistral.ai) |
| **OpenRouter** | ~5 min | 200K | [openrouter.ai](https://openrouter.ai) |

**Total setup time:** ~25 minutes for 5 providers!

### 3. Create .env File

```bash
# Copy template
cp .env.example .env
```

Add your API keys:

```env
GROQ_API_KEY=gsk_...
CEREBRAS_API_KEY=csk_...
GOOGLE_AI_API_KEY=AIzaSy...
MISTRAL_API_KEY=3n7p...
OPENROUTER_API_KEY=sk-or-...
```

### 4. Start Using

```python
from quotarouter import FreeRouter

router = FreeRouter()

# Simple request
response = router.complete("What is Python?")
print(response)
```

That's it! 🎉

## Common Tasks

### Check How Many Tokens You Have Left

```python
status = router.status()

for provider in status["providers"]:
    if provider["configured"]:
        print(f"{provider['name']}: {provider['tokens_remaining']} tokens left")
```

### Stream a Long Response

```python
for chunk in router.complete_stream("Write a 1000-word essay on AI"):
    print(chunk, end="", flush=True)
```

### Have a Conversation

```python
history = []

# First message
response1 = router.complete("What is Python?", history=history)
print(f"Assistant: {response1}")

# Add to history
history.append({"role": "user", "content": "What is Python?"})
history.append({"role": "assistant", "content": response1})

# Follow-up message
response2 = router.complete("What are its best features?", history=history)
print(f"Assistant: {response2}")
```

### Use Only Certain Providers

```python
from quotarouter import FreeRouter, DEFAULT_PROVIDERS

# Use only Groq and Mistral
providers = [p for p in DEFAULT_PROVIDERS if p.id in ["groq", "mistral"]]
router = FreeRouter(providers=providers)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"

The OpenAI library is required:

```bash
pip install openai
```

### "All providers exhausted for today"

You've used up daily quotas across all providers. Quotas reset at midnight.

Check what's left:
```python
status = router.status()
print(status)
```

### "RuntimeError: (401) Unauthorized"

API key is invalid or missing. Check:

```bash
# Print environment (without showing actual keys!)
python -c "import os; print([k for k in os.environ if 'API' in k])"

# Verify your .env is being loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GROQ_API_KEY', 'NOT SET'))"
```

## Next Steps

- 📚 [Full API Documentation](docs/API.md)
- 🏗️ [Architecture Deep Dive](docs/ARCHITECTURE.md)
- 💡 [5 Examples](examples/)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

## Tips & Tricks

### 1. **Start with Groq**
Groq is fastest (500K tokens/day). Great for development and testing.

### 2. **Use Mistral for Volume**
Mistral has 1B tokens/month (~33M/day). Best for heavy usage.

### 3. **Monitor Quotas Daily**
Check status before critical work:

```python
router = FreeRouter()  # Prints status automatically
```

### 4. **Cache Common Prompts**
Same prompt? Same response. Consider caching:

```python
cache = {}

def get_response(key, prompt):
    if key not in cache:
        cache[key] = router.complete(prompt)
    return cache[key]
```

### 5. **Use System Prompts**
Control response style:

```python
response = router.complete(
    "Tell me a joke",
    system="You are a professional comedian. Be funny!"
)
```

## FAQ

**Q: Do I need all 5 providers?**
No! Even 1 provider works. More providers = more quota and redundancy.

**Q: Will my data be shared?**
No! Requests go directly to provider APIs. No logging or storage beyond quota counts.

**Q: Can I use my own API?**
Yes! Create a custom `ProviderConfig` and `ProviderAdapter`.

**Q: What happens at midnight?**
All quotas reset automatically. No manual action needed.

**Q: Can I use this in production?**
Yes! FreeRouter is production-ready with error handling, logging, and type hints.

## Support

- 📖 [Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/Starland9/quotarouter/discussions)
- 🐛 [Report Issues](https://github.com/Starland9/quotarouter/issues)
- 📧 [Email](mailto:landrysimo99@gmail.com)

---

**Happy routing! 🚀**
