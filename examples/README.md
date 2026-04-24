# FreeRouter Examples

This directory contains practical examples of how to use FreeRouter.

## Running Examples

```bash
# Install dependencies
pip install -e "..[dev]"

# Copy env file
cp ../.env.example ../.env

# Add your API keys to .env

# Run an example
python 01_basic_completion.py
```

## Examples

### 1️⃣ [01_basic_completion.py](01_basic_completion.py)
**Basic usage - single completion request**

Shows:
- Initialize FreeRouter
- Make a simple completion request
- Check quota status

```python
from freerouter import FreeRouter

router = FreeRouter()
response = router.complete("Explain machine learning")
print(response)
```

### 2️⃣ [02_streaming.py](02_streaming.py)
**Streaming responses**

Shows:
- Stream responses for long text
- Real-time output
- Better UX for large responses

```python
for chunk in router.complete_stream("Write a 500-word essay..."):
    print(chunk, end="", flush=True)
```

### 3️⃣ [03_conversation.py](03_conversation.py)
**Multi-turn conversations**

Shows:
- Maintain conversation history
- System prompts
- Context-aware responses

```python
history = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "..."},
]
response = router.complete(prompt, history=history)
```

### 4️⃣ [04_status.py](04_status.py)
**Monitor quota usage**

Shows:
- Check provider status
- View token usage
- Track remaining quotas

```python
status = router.status()
print(f"Tokens remaining: {status['providers'][0]['tokens_remaining']}")
```

### 5️⃣ [05_custom_provider.py](05_custom_provider.py)
**Custom provider configuration**

Shows:
- Define custom providers
- Override defaults
- Add new API endpoints

```python
custom = ProviderConfig(id="my-api", ...)
router = FreeRouter(providers=[custom])
```

### 6️⃣ [06_alibaba_test.py](06_alibaba_test.py)
**Alibaba DashScope Provider Test Suite**

A comprehensive test script to verify Alibaba provider setup and functionality.

Shows:
- Provider configuration validation
- API key verification
- Router integration test
- Provider selection logic
- Quota status reporting
- Live completion test (if configured)

```bash
python 06_alibaba_test.py
```

**Output includes:**
- ✅ Configuration checks (ID, model, limits, URL)
- ✅ API key validation
- ✅ Router setup verification
- ✅ Provider selection status
- ✅ Detailed quota information
- ✅ Live API test (if key is set)

## Common Patterns

### Error Handling

```python
try:
    response = router.complete("Your prompt")
except RuntimeError as e:
    if "exhausted" in str(e):
        print("All providers exhausted for today")
except Exception as e:
    print(f"API error: {e}")
```

### Testing with In-Memory Storage

```python
from freerouter import FreeRouter
from freerouter.storage import InMemoryQuotaStorage

router = FreeRouter(
    storage=InMemoryQuotaStorage(),
    verbose=False
)
```

### Custom System Prompts

```python
response = router.complete(
    prompt="Tell me a joke",
    system="You are a professional comedian. Make it funny!",
    max_tokens=200,
)
```

### Processing Multiple Tasks

```python
tasks = [
    "Summarize chapter 1",
    "Summarize chapter 2",
    "Summarize chapter 3",
]

for i, task in enumerate(tasks):
    response = router.complete(task)
    print(f"[{i+1}/{len(tasks)}] ✓")
```

## Tips

- **Add API Keys First**: Copy `.env.example` to `.env` and add your keys
- **Check Status**: Use `router.status()` to monitor quota usage
- **Stream Long Responses**: Use `complete_stream()` for better UX
- **Maintain History**: Keep conversation history for context
- **Handle Quota Errors**: Implement proper error handling for quota exhaustion
- **Test Locally**: Use `InMemoryQuotaStorage` for testing without persistence

## Need Help?

See the [main README](../README.md) for:
- Full API documentation
- Architecture details
- Contributing guidelines
