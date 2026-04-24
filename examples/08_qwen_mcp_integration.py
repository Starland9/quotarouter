"""
Qwen Code MCP Integration Example

This example demonstrates how to use Qwen Code with QuotaRouter
for quota management and intelligent provider routing.

Usage:
    1. Interactive CLI:
       python -m examples.08_qwen_mcp_integration

    2. Programmatic usage:
       python examples/08_qwen_mcp_integration.py --script

    3. With routing:
       python examples/08_qwen_mcp_integration.py --with-routing
"""

import asyncio
import sys
from typing import Optional

from quotarouter.agents.qwen_agent import QwenAgent
from quotarouter.cli.qwen_integration import QwenCLI
from quotarouter.core.router import FreeRouter
from quotarouter.mcp.qwen_code_server import QwenCodeMCPServer


async def interactive_example() -> None:
    """Run interactive CLI."""
    print("🦞 Starting Qwen Code Interactive CLI...")
    cli = QwenCLI()
    await cli.run()


async def script_example() -> None:
    """Run scripted example without router."""
    print("📝 Running Qwen Code Example\n")

    # Create MCP server (no router)
    mcp = QwenCodeMCPServer()

    # Check if any providers are configured
    providers = mcp.get_available_providers()
    if not providers:
        print("❌ No providers configured!")
        print("Run interactive mode first to setup a provider: python -c 'from quotarouter.cli.qwen_integration import QwenCLI; import asyncio; asyncio.run(QwenCLI().run())'")
        return

    # List available providers
    print("Available providers:")
    for provider in providers:
        print(f"  • {provider['id']} - {provider['description']}")

    # Use first provider
    first_provider = providers[0]["id"]
    print(f"\nUsing: {first_provider}\n")

    # Example 1: Simple completion
    print("=" * 60)
    print("Example 1: Simple Completion")
    print("=" * 60)

    response = await mcp.complete(
        prompt="What is Python?",
        model=first_provider,
        max_tokens=150,
    )

    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"\n📝 Response:\n{response['text']}\n")

    # Example 2: Streaming response
    print("=" * 60)
    print("Example 2: Streaming Response")
    print("=" * 60)
    print("\n🔄 Streaming response...")

    async for chunk in mcp.stream(
        prompt="Explain async programming in Python briefly",
        model=first_provider,
        max_tokens=200,
    ):
        if not chunk.get("is_final"):
            print(chunk.get("text", ""), end="", flush=True)

    print("\n")


async def routing_example() -> None:
    """Run example with QuotaRouter integration."""
    print("🔀 Qwen Code with QuotaRouter Integration\n")

    # Create router
    router = FreeRouter()

    # Create agent with router
    agent = QwenAgent(router)

    # Get available models
    models = agent.get_available_models()
    if not models:
        print("❌ No providers configured!")
        return

    print("Available models:")
    for model in models:
        print(f"  • {model['id']} ({model['protocol']})")

    # Use first model
    first_model = models[0]["id"]
    agent.set_model(first_model)
    print(f"\nUsing: {first_model}\n")

    # Example coding task
    print("=" * 60)
    print("Example: Code Analysis with Routing")
    print("=" * 60)

    code_sample = '''
def calculate_factorial(n):
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

result = calculate_factorial(5)
print(result)
'''

    print("\nAnalyzing code with routing...")
    result = await agent.analyze_code(code_sample)
    print(f"\n📊 Analysis:\n{result}\n")

    # Show quota usage
    print("=" * 60)
    print("Quota Usage Summary")
    print("=" * 60)
    print(f"Active provider: {router.active_provider.name if router.active_provider else 'None'}")
    print(f"Total tokens used: {router.total_tokens_used}")
    print(f"Total requests: {router.total_requests}")


async def agent_example() -> None:
    """Run agent multi-turn example."""
    print("🤖 Qwen Agent Multi-turn Conversation\n")

    agent = QwenAgent()

    # Get available models
    models = agent.get_available_models()
    if not models:
        print("❌ No providers configured!")
        return

    agent.set_model(models[0]["id"])
    print(f"Using: {models[0]['id']}\n")

    # Multi-turn conversation
    conversation = [
        "What are the key differences between async and sync code in Python?",
        "Can you provide a code example showing the difference?",
        "How would you handle errors in the async version?",
    ]

    for i, message in enumerate(conversation, 1):
        print(f"\n{'=' * 60}")
        print(f"Turn {i}: User")
        print(f"{'=' * 60}")
        print(f"Message: {message}\n")

        print("Agent response:")
        response = await agent.chat(message)
        print(response)

    # Show history
    print(f"\n{'=' * 60}")
    print("Conversation History")
    print(f"{'=' * 60}")
    history = agent.get_session_history()
    for i, msg in enumerate(history, 1):
        role = "User" if msg["role"] == "user" else "Agent"
        preview = msg["content"][:100]
        if len(msg["content"]) > 100:
            preview += "..."
        print(f"{i}. {role}: {preview}")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "--script":
            asyncio.run(script_example())
        elif mode == "--with-routing":
            asyncio.run(routing_example())
        elif mode == "--agent":
            asyncio.run(agent_example())
        else:
            print(f"Unknown mode: {mode}")
            print("Supported modes: --script, --with-routing, --agent")
    else:
        # Default: interactive mode
        asyncio.run(interactive_example())


if __name__ == "__main__":
    main()
