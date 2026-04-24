# QuotaRouter REST API Server

A FastAPI-based REST API server that exposes QuotaRouter's LLM routing engine for integration with web applications, Streamlit dashboards, and other services.

## Quick Start

### 1. Start the API Server

```bash
# Default (0.0.0.0:8000)
quotarouter api

# Custom port
quotarouter api --port 9000

# Development with auto-reload
quotarouter api --reload

# Production with 4 workers
quotarouter api --workers 4
```

### 2. Access Documentation

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Core Endpoints

### `POST /complete` - Single Completion

Generate a single LLM response.

```bash
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "temperature": 0.7,
    "max_tokens": 500
  }'
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

### `POST /stream` - Streaming Response

Stream responses in real-time (NDJSON format).

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/stream",
    json={"prompt": "Tell a story"},
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk["text"], end="", flush=True)
```

### `GET /status` - Provider Status

Monitor provider quota usage and availability.

```bash
curl http://localhost:8000/status | jq .
```

**Response includes:**
- Provider availability and quota percentage
- Total tokens used across all providers
- Fallback statistics
- Current active provider

### `POST /book` - Generate Books

Generate entire books with automatic chapter generation and retry logic.

```python
response = requests.post(
    "http://localhost:8000/book",
    json={
        "title": "The Art of Python",
        "chapters": 5,
        "chapter_length": 2000,
        "style": "educational"
    },
    timeout=300
)

data = response.json()
print(f"Generated: {data['chapters_generated']} chapters")
```

### `GET /config` - Configuration

Get current configuration and available providers.

```bash
curl http://localhost:8000/config
```

### `POST /reset` - Reset Quotas (Testing)

Reset quota counters for testing.

```bash
# Reset only exhausted providers
curl -X POST http://localhost:8000/reset

# Reset all providers
curl -X POST "http://localhost:8000/reset?reset_all=true"
```

### `GET /health` - Health Check

Simple health check endpoint.

```bash
curl http://localhost:8000/health
```

## Integration Examples

### Python Application

```python
import requests

class QuotaRouterAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def complete(self, prompt, **kwargs):
        response = requests.post(
            f"{self.base_url}/complete",
            json={"prompt": prompt, **kwargs}
        )
        response.raise_for_status()
        return response.json()["text"]

    def stream(self, prompt, **kwargs):
        response = requests.post(
            f"{self.base_url}/stream",
            json={"prompt": prompt, **kwargs},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk["text"]

# Usage
api = QuotaRouterAPI()
response = api.complete("What is Python?")
print(response)
```

### Streamlit Dashboard

See [examples/07_streamlit_integration.py](../examples/07_streamlit_integration.py) for a complete interactive dashboard.

**Quick start:**
```bash
# Terminal 1: Start API
quotarouter api

# Terminal 2: Run Streamlit app
streamlit run examples/07_streamlit_integration.py
```

Then open http://localhost:8501 in your browser.

### Flask Web Application

```python
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
API_URL = "http://localhost:8000"

@app.route("/ai/complete", methods=["POST"])
def complete():
    prompt = request.json.get("prompt")
    response = requests.post(
        f"{API_URL}/complete",
        json={"prompt": prompt}
    )
    return jsonify(response.json())

@app.route("/ai/status", methods=["GET"])
def status():
    response = requests.get(f"{API_URL}/status")
    return jsonify(response.json())

if __name__ == "__main__":
    app.run()
```

### Shell Script

```bash
#!/bin/bash

# Send completion request
curl -X POST http://localhost:8000/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello world",
    "max_tokens": 100
  }' | jq .text

# Check status
curl http://localhost:8000/status | jq '.active_provider'
```

## Installation Requirements

The API server requires FastAPI and Uvicorn:

```bash
# Install with optional dependencies
pip install quotarouter[api]

# Or install manually
pip install fastapi uvicorn pydantic
```

## Configuration

### Environment Variables

- `QUOTAROUTER_OPENROUTER_KEY`: OpenRouter API key
- `QUOTAROUTER_TOGETHER_KEY`: Together AI API key
- `QUOTAROUTER_MISTRAL_KEY`: Mistral API key
- (Add others as needed for your providers)

### CORS Configuration

The API allows all origins by default. For production, restrict CORS in `src/quotarouter/api/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir quotarouter[api]

ENV QUOTAROUTER_OPENROUTER_KEY=${OPENROUTER_KEY}
ENV QUOTAROUTER_TOGETHER_KEY=${TOGETHER_KEY}

EXPOSE 8000

CMD ["quotarouter", "api", "--host", "0.0.0.0", "--workers", "4"]
```

**Build & Run:**
```bash
docker build -t quotarouter-api .
docker run -p 8000:8000 -e OPENROUTER_KEY=sk-... quotarouter-api
```

### Heroku

```bash
# Create Procfile
echo 'web: quotarouter api --host 0.0.0.0 --port $PORT --workers 2' > Procfile

# Deploy
git push heroku main
```

### AWS Lambda

Use serverless framework or API Gateway + Lambda with FastAPI adapter.

## Error Handling

All errors return a consistent JSON format:

```json
{
  "error": "quota_exhausted",
  "message": "All providers have exhausted their quota",
  "details": "Try again later"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (validation error)
- `500` - Server error
- `503` - Service unavailable (all providers exhausted)

## Performance

### Load Testing

```bash
# Install load testing tool
pip install locust

# Create locustfile.py
# See examples for load test configuration

locust -f locustfile.py --host=http://localhost:8000
```

### Benchmarks

**Single completion:**
- Response time: ~2-5 seconds (depends on provider)
- Throughput: 10-20 req/sec per worker

**Streaming:**
- First chunk: ~1-2 seconds
- Total throughput: Limited by LLM provider

**Status check:**
- Response time: <100ms
- Throughput: 100+ req/sec

## Monitoring

### Health Check Script

```bash
#!/bin/bash

while true; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
  else
    echo "✗ API is down"
  fi
  sleep 30
done
```

### Log Aggregation

The API uses Python's standard logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quotarouter.api")
```

## Troubleshooting

### "Cannot connect to API"

```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
quotarouter api --reload  # Runs in foreground with logs
```

### "All providers exhausted"

Use the reset endpoint for testing:
```bash
curl -X POST "http://localhost:8000/reset?reset_all=true"
```

### Slow responses

- Check provider status: `curl http://localhost:8000/status`
- Increase workers: `quotarouter api --workers 4`
- Monitor quota usage in status endpoint

## API Reference

Full API documentation: See [docs/API.md](../docs/API.md)

## Examples

- [Python integration](../examples/08_api_integration.py)
- [Streamlit dashboard](../examples/07_streamlit_integration.py)
- [Web application](../examples) (coming soon)

## Security Considerations

1. **API Keys**: Keep API keys in environment variables, never in code
2. **Rate Limiting**: The API respects provider rate limits (RPM)
3. **Input Validation**: All inputs are validated with Pydantic
4. **CORS**: Restrict to your domain in production
5. **Authentication**: Add your own auth layer (OAuth, JWT, etc.)

Example with authentication:

```python
from fastapi import Depends, HTTPException, Header

async def verify_api_key(x_token: str = Header(...)):
    if x_token != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_token

@app.post("/complete")
async def complete(request: CompletionRequest, api_key: str = Depends(verify_api_key)):
    # ... endpoint logic
```

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] WebSocket support for real-time streaming
- [ ] Request queuing and batching
- [ ] Advanced authentication options
- [ ] Metrics/monitoring endpoints
- [ ] Caching layer
- [ ] Rate limiting per user

## License

MIT - See [LICENSE](../LICENSE)
