#!/usr/bin/env python3
"""
Streaming example: Stream responses.

Shows how to stream responses from FreeRouter, useful for long responses.
"""

from freerouter import FreeRouter


def main():
    router = FreeRouter(verbose=False)

    prompt = "Write a short story about a robot learning to paint"

    print("🎬 Streaming response:")
    print("-" * 50)

    # Stream the response
    for chunk in router.complete_stream(prompt):
        print(chunk, end="", flush=True)

    print("\n" + "-" * 50)

    # Show status
    status = router.status()
    print(f"\n✅ Stream completed!")
    print(f"  - Total tokens: {status['session']['tokens']}")


if __name__ == "__main__":
    main()
