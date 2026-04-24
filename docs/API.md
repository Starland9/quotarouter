# FreeRouter API Reference

## Core Classes

### `FreeRouter`

Main class for routing LLM requests across providers.

#### Constructor

```python
FreeRouter(
    providers: Optional[list[ProviderConfig]] = None,
    adapter: Optional[ProviderAdapter] = None,
    storage: Optional[QuotaStorage] = None,
    verbose: bool = True,
)
```

**Parameters:**
- `providers`: List of provider configurations. Defaults to `DEFAULT_PROVIDERS`
- `adapter`: Communication adapter. Defaults to `OpenAICompatibleAdapter()`
- `storage`: Quota storage backend. Defaults to `JSONQuotaStorage()`
- `verbose`: Print status information on init

**Raises:**
- `ValueError`: If no providers provided

#### Methods

##### `complete()`

Send a completion request and get response.

```python
def complete(
    prompt: str,
    system: str = "You are a helpful assistant.",
    max_tokens: int = 4096,
    history: Optional[list[dict]] = None,
) -> str
```

**Parameters:**
- `prompt`: User prompt
- `system`: System prompt for context
- `max_tokens`: Maximum response tokens
- `history`: Previous messages for multi-turn conversations

**Returns:**
- Response text as string

**Raises:**
- `RuntimeError`: If all providers exhausted

**Example:**
```python
router = FreeRouter()
response = router.complete("Explain quantum computing")
print(response)
```

##### `complete_stream()`

Stream a completion response.

```python
def complete_stream(
    prompt: str,
    system: str = "You are a helpful assistant.",
    max_tokens: int = 4096,
    history: Optional[list[dict]] = None,
) -> Iterator[str]
```

**Parameters:** Same as `complete()`

**Returns:**
- Iterator yielding text chunks

**Raises:**
- `RuntimeError`: If all providers exhausted

**Example:**
```python
for chunk in router.complete_stream("Write a story"):
    print(chunk, end="", flush=True)
```

##### `status()`

Get current quota and session status.

```python
def status() -> dict
```

**Returns:**
- Dictionary with structure:
```python
{
    "session": {
        "requests": int,
        "tokens": int,
        "fallbacks": int,
    },
    "providers": [
        {
            "id": str,
            "name": str,
            "model": str,
            "configured": bool,
            "tokens_used": int,
            "tokens_limit": int,
            "tokens_remaining": int,
            "pct_used": float,
            "exhausted": bool,
            "priority": int,
        },
        ...
    ],
}
```

**Example:**
```python
status = router.status()
print(f"Tokens used: {status['session']['tokens']}")
```

##### `reset_quotas()`

Force reset all quotas (for testing).

```python
def reset_quotas() -> None
```

**Note:** Quotas automatically reset at midnight

---

### `ProviderConfig`

Configuration for an LLM provider.

#### Constructor

```python
ProviderConfig(
    id: str,
    name: str,
    model: str,
    daily_token_limit: int,
    rpm_limit: int,
    priority: int,
    api_key_env: str,
    base_url: str,
    flag: str = "🌐",
)
```

**Parameters:**
- `id`: Unique provider identifier
- `name`: Display name
- `model`: Model name/ID
- `daily_token_limit`: Daily token quota
- `rpm_limit`: Requests per minute limit
- `priority`: Selection priority (lower = higher)
- `api_key_env`: Environment variable for API key
- `base_url`: API endpoint base URL
- `flag`: Emoji flag for display

#### Properties

##### `tokens_remaining: int`
Remaining tokens for today.

##### `is_exhausted: bool`
Whether daily quota is exhausted.

##### `is_configured: bool`
Whether API key is set in environment.

##### `api_key: Optional[str]`
Get API key from environment.

#### Methods

##### `check_rpm() -> bool`
Check if RPM limit allows next request.

##### `record_request(tokens_used: int)`
Record a completed request.

##### `wait_for_rpm()`
Block until RPM window resets if needed.

##### `reset()`
Reset daily token counter.

---

### `CompletionRequest`

Encapsulates request parameters.

#### Constructor

```python
CompletionRequest(
    prompt: str,
    system: str = "You are a helpful assistant.",
    max_tokens: int = 4096,
    history: Optional[list[dict]] = None,
)
```

#### Methods

##### `build_messages() -> list[dict]`
Convert to OpenAI-compatible message format.

---

### `CompletionResponse`

Response from LLM completion.

#### Constructor

```python
CompletionResponse(
    text: str,
    tokens_used: int,
    provider_id: str,
    provider_name: str,
)
```

---

## Abstract Base Classes

### `ProviderAdapter`

Interface for provider communication.

```python
class ProviderAdapter(ABC):
    @abstractmethod
    def complete(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> tuple[str, int]:
        """Returns (response_text, tokens_used)"""
        ...

    @abstractmethod
    def complete_stream(
        self,
        provider: ProviderConfig,
        messages: list[dict],
        max_tokens: int,
    ) -> Iterator[str]:
        """Yields text chunks"""
        ...
```

### `QuotaStorage`

Interface for quota persistence.

```python
class QuotaStorage(ABC):
    @abstractmethod
    def load_quotas(self) -> dict[str, int]:
        """Load quotas by provider ID"""
        ...

    @abstractmethod
    def save_quotas(self, quotas: dict[str, int]) -> None:
        """Save quotas by provider ID"""
        ...
```

---

## Implementations

### `OpenAICompatibleAdapter`

Adapter for OpenAI-compatible APIs.

Works with:
- Groq
- Cerebras
- Mistral
- OpenRouter
- Any OpenAI-compatible endpoint

```python
from quotarouter.providers import OpenAICompatibleAdapter

adapter = OpenAICompatibleAdapter()
router = FreeRouter(adapter=adapter)
```

### `JSONQuotaStorage`

File-based storage (default).

Stores to `~/.quotarouter_quotas.json`

```python
from quotarouter.storage import JSONQuotaStorage

storage = JSONQuotaStorage()
router = FreeRouter(storage=storage)
```

### `InMemoryQuotaStorage`

In-memory storage for testing.

```python
from quotarouter.storage import InMemoryQuotaStorage

storage = InMemoryQuotaStorage()
router = FreeRouter(storage=storage)
```

---

## Configuration

### `DEFAULT_PROVIDERS`

Pre-configured providers:

```python
from quotarouter import DEFAULT_PROVIDERS

for provider in DEFAULT_PROVIDERS:
    print(f"{provider.name}: {provider.daily_token_limit} tokens/day")
```

Providers included:
1. **Cerebras** - 1M tokens/day
2. **Groq** - 500K tokens/day
3. **Google AI** - 480K tokens/day
4. **Mistral** - 33M tokens/day (~1B/month)
5. **OpenRouter** - 200K tokens/day

### `get_provider_by_id()`

Lookup provider by ID.

```python
from quotarouter import get_provider_by_id

provider = get_provider_by_id("groq")
```

---

## Error Handling

### Common Exceptions

**`RuntimeError: All providers exhausted for today`**
- All provider daily quotas exhausted
- Quotas reset at midnight

**`ImportError: OpenAI library required`**
- Install with: `pip install openai`

**`Exception: (429) Quota exceeded`**
- Provider quota hit mid-request
- Router automatically retries with next provider

### Recommended Error Handling

```python
try:
    response = router.complete("Your prompt")
except RuntimeError as e:
    if "exhausted" in str(e):
        print("All providers exhausted for today")
        # Schedule for later or use a paid API
    else:
        raise
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

---

## Logging

FreeRouter uses Python's `logging` module.

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("quotarouter")

router = FreeRouter()
```

Log levels:
- `DEBUG`: Token counts, provider selection
- `INFO`: Quota resets, fallbacks
- `WARNING`: Quota errors, API errors
- `ERROR`: Critical failures

---

## Examples

### Simple Completion

```python
from quotarouter import FreeRouter

router = FreeRouter()
answer = router.complete("What is Python?")
print(answer)
```

### Streaming

```python
for chunk in router.complete_stream("Write a 500-word essay"):
    print(chunk, end="", flush=True)
```

### Multi-turn Conversation

```python
history = []

# Turn 1
response1 = router.complete("What is Python?", history=history)
history.append({"role": "user", "content": "What is Python?"})
history.append({"role": "assistant", "content": response1})

# Turn 2
response2 = router.complete("What are its uses?", history=history)
```

### Status Monitoring

```python
status = router.status()
for p in status["providers"]:
    print(f"{p['name']}: {p['tokens_remaining']} tokens left")
```

### Custom Configuration

```python
from quotarouter import FreeRouter, ProviderConfig

providers = [
    ProviderConfig(
        id="my-api",
        name="My LLM API",
        model="my-model",
        daily_token_limit=1_000_000,
        rpm_limit=100,
        priority=1,
        api_key_env="MY_API_KEY",
        base_url="https://api.example.com/v1",
    ),
]

router = FreeRouter(providers=providers)
```

---

## REST API

QuotaRouter provides a FastAPI-based REST API server for integration with web applications, Streamlit apps, and other services.

### Starting the Server

```bash
# Basic (localhost:8000)
quotarouter api

# Custom host and port
quotarouter api --host 0.0.0.0 --port 8080

# Development mode with auto-reload
quotarouter api --reload

# Production mode with 4 workers
quotarouter api --workers 4
```

### API Base URL
```
http://localhost:8000
```

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

### Core Endpoints

#### `POST /complete` - Single Completion

Generate a single completion.

**Request:**
```json
{
    "prompt": "Explain quantum computing",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9
}
```

**Response:**
```json
{
    "text": "Quantum computing uses quantum bits...",
    "provider": "openrouter",
    "tokens_used": 142,
    "stop_reason": "length"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello world",
    "temperature": 0.7
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/complete",
    json={"prompt": "Explain Python"}
)
data = response.json()
print(data["text"])
```

---

#### `POST /stream` - Streaming Completion

Stream responses in real-time (Server-Sent Events).

**Request:**
```json
{
    "prompt": "Write a story",
    "temperature": 0.8,
    "max_tokens": 1000
}
```

**Response:** NDJSON (newline-delimited JSON)
```json
{"text": "Once upon a time", "provider": "openrouter", "is_final": false}
{"text": ", there was", "provider": "openrouter", "is_final": false}
{"text": " a robot", "provider": "openrouter", "is_final": false}
{"text": "", "provider": "openrouter", "is_final": true, "total_tokens": 45}
```

**Python Example:**
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/stream",
    json={"prompt": "Tell a joke"},
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk["text"], end="", flush=True)
```

**Streamlit Example:**
```python
import requests
import json
import streamlit as st

response = requests.post(
    "http://localhost:8000/stream",
    json={"prompt": st.text_input("Prompt:")},
    stream=True
)

full_response = ""
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        full_response += chunk["text"]
        st.write(full_response)
```

---

#### `GET /status` - Provider Status

Get real-time status of all providers and quota information.

**Response:**
```json
{
    "providers": [
        {
            "name": "openrouter",
            "available": true,
            "tokens_used": 5000,
            "token_limit": 100000,
            "requests_used": 10,
            "request_limit": 60,
            "quota_percentage": 5.0,
            "priority": 1
        }
    ],
    "active_provider": "openrouter",
    "total_tokens_used": 5000,
    "total_requests": 10,
    "fallback_count": 0
}
```

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/status")
data = response.json()

for provider in data["providers"]:
    status = "✓" if provider["available"] else "✗"
    print(f"{status} {provider['name']}: {provider['quota_percentage']:.1f}% used")
```

---

#### `POST /book` - Generate Book

Generate entire book with automatic chapter generation and retry logic.

**Request:**
```json
{
    "title": "The Art of Python",
    "chapters": 5,
    "chapter_length": 2000,
    "style": "educational"
}
```

**Response:**
```json
{
    "title": "The Art of Python",
    "chapters_generated": 5,
    "total_chapters": 5,
    "total_words": 12500,
    "tokens_used": 125000,
    "providers_used": ["openrouter", "together"],
    "filename": "the_art_of_python.md",
    "status": "completed"
}
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/book",
    json={
        "title": "Web Scraping Guide",
        "chapters": 3,
        "chapter_length": 1500,
        "style": "technical"
    },
    timeout=300  # 5 minutes
)

data = response.json()
print(f"Generated {data['chapters_generated']} chapters")
print(f"Saved to: {data['filename']}")
```

---

#### `GET /config` - Configuration

Get current configuration and available providers.

**Response:**
```json
{
    "configured_providers": ["openrouter", "together", "mistral"],
    "storage_backend": "json",
    "verbose_mode": true,
    "api_version": "0.4.0",
    "quotarouter_version": "0.4.0"
}
```

---

#### `POST /reset` - Reset Quotas (Testing)

Reset quota counters (for testing purposes).

**Query Parameters:**
- `reset_all` (bool): Reset all providers or only exhausted ones. Default: `false`

**Response:**
```json
{
    "message": "Reset 2 provider quotas",
    "providers_reset": 2,
    "timestamp": "2024-04-24T10:30:00.000000"
}
```

---

#### `GET /health` - Health Check

Simple health check endpoint.

**Response:**
```json
{
    "status": "ok",
    "timestamp": "2024-04-24T10:30:00.000000"
}
```

---

### Streamlit Integration Example

See [examples/07_streamlit_integration.py](../examples/07_streamlit_integration.py) for a complete Streamlit dashboard.

**Quick Start:**
```bash
# Terminal 1: Start API server
quotarouter api

# Terminal 2: Start Streamlit app
pip install streamlit requests
streamlit run examples/07_streamlit_integration.py
```

Then open `http://localhost:8501` in your browser.

---

### Error Responses

All errors return a consistent JSON format:

```json
{
    "error": "quota_exhausted",
    "message": "All providers have exhausted their quota",
    "details": "Try again later"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `500` - Server error
- `503` - Service unavailable (quota exhausted)
