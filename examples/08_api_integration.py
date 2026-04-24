"""
QuotaRouter REST API Integration Example

This example demonstrates how to use the QuotaRouter REST API
from Python applications for various use cases.

Installation:
    pip install requests

Usage:
    python 08_api_integration.py
"""

import requests
import json
from typing import Generator

# API configuration
API_URL = "http://localhost:8000"


class QuotaRouterClient:
    """Simple client for QuotaRouter API."""

    def __init__(self, base_url: str = API_URL):
        """Initialize client with API base URL."""
        self.base_url = base_url

    def health_check(self) -> dict:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_status(self) -> dict:
        """Get provider status and quota information."""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 0.9,
    ) -> dict:
        """Send a completion request."""
        response = requests.post(
            f"{self.base_url}/complete",
            json={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            },
        )
        response.raise_for_status()
        return response.json()

    def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 0.9,
    ) -> Generator[dict, None, None]:
        """Stream a completion response."""
        response = requests.post(
            f"{self.base_url}/stream",
            json={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            },
            stream=True,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def generate_book(
        self,
        title: str,
        chapters: int = 3,
        chapter_length: int = 2000,
        style: str = "educational",
    ) -> dict:
        """Generate a book."""
        response = requests.post(
            f"{self.base_url}/book",
            json={
                "title": title,
                "chapters": chapters,
                "chapter_length": chapter_length,
                "style": style,
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    def get_config(self) -> dict:
        """Get API configuration."""
        response = requests.get(f"{self.base_url}/config")
        response.raise_for_status()
        return response.json()

    def reset_quotas(self, reset_all: bool = False) -> dict:
        """Reset quota counters."""
        response = requests.post(
            f"{self.base_url}/reset",
            params={"reset_all": reset_all},
        )
        response.raise_for_status()
        return response.json()


def main():
    """Run integration examples."""
    client = QuotaRouterClient()

    print("=" * 80)
    print("QuotaRouter REST API Integration Examples")
    print("=" * 80)
    print()

    # Example 1: Health check
    print("📍 Example 1: Health Check")
    print("-" * 80)
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Timestamp: {health['timestamp']}")
        print("✅ API is healthy")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Start it with: quotarouter api")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Example 2: Get configuration
    print("📍 Example 2: Get Configuration")
    print("-" * 80)
    try:
        config = client.get_config()
        print(f"Providers: {', '.join(config['configured_providers'])}")
        print(f"Storage Backend: {config['storage_backend']}")
        print(f"API Version: {config['api_version']}")
        print(f"QuotaRouter Version: {config['quotarouter_version']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Example 3: Get status
    print("📍 Example 3: Provider Status & Quota")
    print("-" * 80)
    try:
        status = client.get_status()
        print(f"Active Provider: {status['active_provider']}")
        print(f"Total Tokens Used: {status['total_tokens_used']:,}")
        print(f"Total Requests: {status['total_requests']}")
        print(f"Fallback Count: {status['fallback_count']}")
        print()
        print("Provider Details:")
        for provider in status["providers"]:
            available = "✓" if provider["available"] else "✗"
            print(
                f"  {available} {provider['name']}: "
                f"{provider['quota_percentage']:.1f}% used "
                f"({provider['tokens_used']}/{provider['token_limit'] or '∞'} tokens)"
            )
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Example 4: Single completion
    print("📍 Example 4: Single Completion")
    print("-" * 80)
    try:
        result = client.complete("Explain Python in 2 sentences")
        print(f"Provider: {result['provider']}")
        print(f"Tokens Used: {result['tokens_used']}")
        print(f"Stop Reason: {result.get('stop_reason', '—')}")
        print()
        print("Generated Text:")
        print(result["text"])
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Example 5: Streaming
    print("📍 Example 5: Streaming Response")
    print("-" * 80)
    try:
        print("Streaming response:")
        full_response = ""
        for chunk in client.stream("Write a haiku about AI"):
            if not chunk.get("is_final"):
                text = chunk["text"]
                print(text, end="", flush=True)
                full_response += text
            else:
                print()
                print()
                print(f"Provider: {chunk['provider']}")
                print(f"Total Tokens: {chunk.get('total_tokens', '—')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

    # Example 6: Book generation
    print("📍 Example 6: Book Generation (Async would be better for this)")
    print("-" * 80)
    print("Skipping live demo (takes time). Code:")
    print("""
    # Generate a 2-chapter book
    result = client.generate_book(
        title="Quick Guide to APIs",
        chapters=2,
        chapter_length=1000,
        style="technical"
    )
    
    print(f"Generated {result['chapters_generated']} chapters")
    print(f"Total words: {result['total_words']:,}")
    print(f"Tokens used: {result['tokens_used']:,}")
    print(f"Saved to: {result['filename']}")
    """)
    print()

    # Example 7: Reset quotas
    print("📍 Example 7: Reset Quotas (Testing)")
    print("-" * 80)
    print("Code to reset quotas:")
    print("""
    # Reset only exhausted providers
    result = client.reset_quotas(reset_all=False)
    
    # Reset all providers
    result = client.reset_quotas(reset_all=True)
    
    print(f"Reset {result['providers_reset']} providers")
    """)
    print()

    # Summary
    print("=" * 80)
    print("Integration Guide")
    print("=" * 80)
    print("""
Use QuotaRouter API in your applications:

1. Web Apps (Flask, Django):
   - Use the `requests` library to call endpoints
   - Run API in separate process/container
   - Configure CORS if needed

2. Streamlit Apps:
   - See examples/07_streamlit_integration.py
   - Perfect for interactive UI

3. Data Pipelines:
   - Use in Apache Airflow, Prefect, etc.
   - Add retry logic and monitoring

4. Microservices:
   - Deploy as Docker container
   - Scale with multiple workers (--workers flag)

5. CLI Tools:
   - Use in shell scripts with curl
   - Simple JSON input/output

API Documentation:
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
  - Schema: http://localhost:8000/openapi.json

See docs/API.md for complete reference
""")


if __name__ == "__main__":
    main()
