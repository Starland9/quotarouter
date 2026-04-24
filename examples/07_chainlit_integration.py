"""
Chainlit chat application demonstrating QuotaRouter API integration.

This example shows how to use the QuotaRouter REST API
from a Chainlit chat application with real-time streaming.

Installation:
    pip install chainlit requests

Running:
    chainlit run 07_chainlit_integration.py

Then start the API server in another terminal:
    quotarouter api --port 8000

The Chainlit app will communicate with the API at http://localhost:8000
"""

import os
import json
import chainlit as cl
import requests
from typing import Optional

# API configuration
API_BASE_URL = os.getenv("QUOTAROUTER_API_URL", "http://localhost:8000")


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    cl.user_session.set("api_url", API_BASE_URL)

    # Get API status
    try:
        status_response = requests.get(f"{API_BASE_URL}/status")
        status = status_response.json()
        active_provider = status.get("active_provider", "Unknown")

        welcome_msg = f"""
🤖 **QuotaRouter Chat Assistant**

Connected to **{active_provider}** provider via QuotaRouter API.

I can help you with:
- 💬 **Text Completions** - Ask me anything
- 📊 **Provider Status** - Check available quota
- ⚡ **Real-time Streaming** - Watch responses generate live
- 📖 **Long-form Content** - Books, articles, stories

**Current Configuration:**
- 🔀 **Active Provider**: {active_provider}
- 📈 **Total Providers**: {len(status.get("providers", []))}
- 💾 **Tokens Used Today**: {status.get("total_tokens_used", 0):,}

Start by typing your question or use `/status` to see provider details.
        """

        await cl.Message(content=welcome_msg).send()
    except Exception as e:
        error_msg = f"⚠️ Could not connect to QuotaRouter API at {API_BASE_URL}\n\nError: {str(e)}"
        await cl.Message(content=error_msg).send()


@cl.command()
async def status():
    """Get current quota status from all providers."""
    api_url = cl.user_session.get("api_url")

    try:
        response = requests.get(f"{api_url}/status")
        response.raise_for_status()
        status = response.json()

        # Format provider information
        providers_info = "📊 **Provider Status**\n\n"
        for provider in status.get("providers", []):
            name = provider["name"]
            available = "✅" if provider["available"] else "❌"
            quota_pct = provider["quota_percentage"]
            tokens_used = provider["tokens_used"]
            token_limit = provider["token_limit"]

            quota_bar = "█" * int(quota_pct / 5) + "░" * (20 - int(quota_pct / 5))

            providers_info += f"{available} **{name}**\n"
            providers_info += f"   [{quota_bar}] {quota_pct:.1f}%\n"
            providers_info += f"   Tokens: {tokens_used:,} / {token_limit:,}\n\n"

        summary = f"\n📈 **Summary**\n"
        summary += f"- Active Provider: {status.get('active_provider')}\n"
        summary += f"- Total Tokens Used: {status.get('total_tokens_used', 0):,}\n"
        summary += f"- Fallback Count: {status.get('fallback_count', 0)}\n"

        await cl.Message(content=providers_info + summary).send()

    except requests.exceptions.ConnectionError:
        await cl.Message(
            content="❌ Could not connect to QuotaRouter API. Make sure the server is running:\n\n`quotarouter api`"
        ).send()
    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()


@cl.on_message
async def main(message: cl.Message):
    """
    Process user messages and stream responses from QuotaRouter API.
    """
    api_url = cl.user_session.get("api_url")

    # Check for commands
    if message.content.startswith("/"):
        if message.content == "/status":
            await status()
        return

    # Show thinking indicator
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Prepare request to API
        request_data = {
            "prompt": message.content,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        # Call streaming endpoint
        response = requests.post(
            f"{api_url}/stream",
            json=request_data,
            stream=True,
        )
        response.raise_for_status()

        # Stream response tokens
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = line.decode("utf-8").strip()
                if chunk:
                    try:
                        data = json.loads(chunk)
                        text = data.get("text", "")
                        if text:
                            full_response += text
                            msg.content = full_response
                            await msg.update()
                    except json.JSONDecodeError:
                        pass

        # Add provider info to message
        try:
            status_response = requests.get(f"{api_url}/status")
            status = status_response.json()
            active = status.get("active_provider", "Unknown")
            msg.content += f"\n\n---\n*Processed by: **{active}***"
            await msg.update()
        except:
            pass

    except requests.exceptions.ConnectionError:
        msg.content = "❌ Cannot connect to QuotaRouter API\n\nMake sure to start the server:\n```\nquotarouter api\n```"
        await msg.update()
    except requests.exceptions.HTTPError as e:
        try:
            error_data = e.response.json()
            error_msg = error_data.get("message", str(e))
        except:
            error_msg = str(e)

        msg.content = f"❌ API Error: {error_msg}"
        await msg.update()
    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()


@cl.on_logout
async def on_logout():
    """Called when user logs out."""
    cl.user_session.clear()
