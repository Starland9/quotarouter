#!/usr/bin/env python3
"""
Simple example: Basic completion.

Shows how to use FreeRouter for a single completion request.
"""

from quotarouter import FreeRouter


def main():
    # Initialize router (loads configuration and quota status)
    router = FreeRouter(verbose=True)

    # Make a simple request
    prompt = "Explain the concept of machine learning in 100 words"
    response = router.complete(prompt)

    print("\n📝 Response:")
    print(response)

    # Check quota status
    status = router.status()
    print("\n✅ Session stats:")
    print(f"  - Requests: {status['session']['requests']}")
    print(f"  - Tokens used: {status['session']['tokens']}")
    print(f"  - Fallbacks: {status['session']['fallbacks']}")


if __name__ == "__main__":
    main()
