#!/usr/bin/env python3
"""
Conversation example: Multi-turn conversation.

Shows how to maintain conversation history with FreeRouter.
"""

from quotarouter import FreeRouter


def main():
    router = FreeRouter(verbose=False)

    # System prompt for context
    system = "You are a helpful programming assistant. Keep responses concise."

    # Simulate a conversation
    history = []

    print("🗣️  Multi-turn Conversation Example")
    print("=" * 50)

    # Turn 1
    prompt1 = "What is Python?"
    print(f"\nUser: {prompt1}")

    response1 = router.complete(
        prompt=prompt1,
        system=system,
        history=history,
    )
    print(f"Assistant: {response1}")

    # Add to history
    history.append({"role": "user", "content": prompt1})
    history.append({"role": "assistant", "content": response1})

    # Turn 2
    prompt2 = "What are its main advantages?"
    print(f"\nUser: {prompt2}")

    response2 = router.complete(
        prompt=prompt2,
        system=system,
        history=history,
    )
    print(f"Assistant: {response2}")

    # Add to history
    history.append({"role": "user", "content": prompt2})
    history.append({"role": "assistant", "content": response2})

    # Turn 3
    prompt3 = "How do decorators work?"
    print(f"\nUser: {prompt3}")

    response3 = router.complete(
        prompt=prompt3,
        system=system,
        history=history,
    )
    print(f"Assistant: {response3}")

    # Show summary
    status = router.status()
    print(f"\n{'=' * 50}")
    print("✅ Conversation complete")
    print(f"  - Total requests: {status['session']['requests']}")
    print(f"  - Total tokens: {status['session']['tokens']}")


if __name__ == "__main__":
    main()
