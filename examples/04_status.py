#!/usr/bin/env python3
"""
Status example: Monitor quota usage.

Shows how to check quota status and monitor token usage across providers.
"""

import json
from quotarouter import FreeRouter


def main():
    router = FreeRouter(verbose=False)

    print("📊 FreeRouter Quota Status")
    print("=" * 60)

    # Get comprehensive status
    status = router.status()

    # Print session stats
    print("\n🔄 Session Statistics:")
    print(f"  Requests: {status['session']['requests']}")
    print(f"  Tokens used: {status['session']['tokens']:,}")
    print(f"  Fallbacks: {status['session']['fallbacks']}")

    # Print provider details
    print("\n🏢 Provider Status:")
    print("-" * 60)
    print(f"{'Provider':<20} {'Status':<10} {'Used':<12} {'Remaining':<12}")
    print("-" * 60)

    for provider in status["providers"]:
        status_icon = "✅" if provider["configured"] else "⚠️"
        status_text = "Ready" if provider["configured"] else "No key"

        print(
            f"{provider['name']:<20} "
            f"{status_icon} {status_text:<7} "
            f"{provider['tokens_used']:>10,} "
            f"{provider['tokens_remaining']:>10,}"
        )

    print("-" * 60)

    # Calculate total available
    total_remaining = sum(
        p["tokens_remaining"] for p in status["providers"] if p["configured"]
    )
    print(f"{'TOTAL':<20} {'':10} {'':12} {total_remaining:>10,}")

    # Print as JSON for integration
    print("\n📋 Full status (JSON):")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
