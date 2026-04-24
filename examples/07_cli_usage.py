#!/usr/bin/env python3
"""
Example: Using QuotaRouter CLI

QuotaRouter CLI provides a command-line interface for interacting with FreeRouter.

Commands:
    quotarouter status              - Show provider status
    quotarouter complete "prompt"   - Send a simple completion request
    quotarouter stream "prompt"     - Stream a response
    quotarouter reset               - Reset quota counters
    quotarouter config              - Show configuration
"""

import subprocess
import sys


def run_command(cmd: str):
    """Run a CLI command and print output."""
    print(f"\n{'=' * 60}")
    print(f"$ {cmd}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    """Demonstrate CLI commands."""
    print("🔀 QuotaRouter CLI Examples")
    print("=" * 60)

    # Show help
    print("\n1. Show help")
    run_command("quotarouter --help")

    # Show status
    print("\n2. Check provider status")
    run_command("quotarouter status")

    # Show config
    print("\n3. Show configuration")
    run_command("quotarouter config --list")

    # Show default providers
    print("\n4. Show default providers")
    run_command("quotarouter config")

    # Simple completion (requires API keys)
    print("\n5. Send a completion request (requires API keys in .env)")
    print('   $ quotarouter complete "Explain Python generators"')
    print("   (Skipping - requires configured API keys)")

    # Stream response (requires API keys)
    print("\n6. Stream a response (requires API keys in .env)")
    print('   $ quotarouter stream "Write a haiku about AI"')
    print("   (Skipping - requires configured API keys)")

    print("\n" + "=" * 60)
    print("💡 Tips:")
    print("  - Use .env file to configure API keys")
    print("  - quotarouter status shows available quota")
    print("  - quotarouter complete is for single requests")
    print("  - quotarouter stream is for long responses")
    print("  - quotarouter reset clears quota counters (testing only)")
    print("=" * 60)


if __name__ == "__main__":
    main()
