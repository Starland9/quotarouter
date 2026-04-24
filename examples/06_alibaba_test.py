#!/usr/bin/env python3
"""
Alibaba DashScope Provider Test

Test script to verify Alibaba DashScope provider configuration and functionality.
Execute: python examples/06_alibaba_test.py
"""

import os
import json
from freerouter import FreeRouter, DEFAULT_PROVIDERS
from freerouter.config.registry import get_provider_by_id


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"🔍 {title}")
    print(f"{'=' * 60}")


def test_alibaba_config():
    """Test 1: Check Alibaba provider configuration."""
    print_section("Test 1: Provider Configuration")

    alibaba = get_provider_by_id("alibaba")

    if not alibaba:
        print("❌ FAILED: Alibaba provider not found in registry")
        return False

    print(f"✅ Provider ID: {alibaba.id}")
    print(f"✅ Provider Name: {alibaba.name}")
    print(f"✅ Model: {alibaba.model}")
    print(f"✅ Daily Token Limit: {alibaba.daily_token_limit:,}")
    print(f"✅ RPM Limit: {alibaba.rpm_limit}")
    print(f"✅ Priority: {alibaba.priority}")
    print(f"✅ Base URL: {alibaba.base_url}")
    print(f"✅ Flag: {alibaba.flag}")

    return True


def test_alibaba_api_key():
    """Test 2: Check if Alibaba API key is configured."""
    print_section("Test 2: API Key Configuration")

    alibaba = get_provider_by_id("alibaba")

    if not alibaba:
        print("❌ FAILED: Provider not found")
        return False

    api_key = os.getenv(alibaba.api_key_env)

    if not api_key:
        print(f"⚠️  WARNING: {alibaba.api_key_env} not set in environment")
        print(f"   Add your API key to .env file:")
        print(f"   {alibaba.api_key_env}=your_api_key_here")
        return False

    # Show masked API key for security
    masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 20 else "***"
    print(f"✅ API Key found: {masked_key}")
    print(f"✅ Key length: {len(api_key)} characters")

    return True


def test_router_setup():
    """Test 3: Test router with Alibaba provider."""
    print_section("Test 3: Router Setup")

    router = FreeRouter(verbose=False)

    # Check if Alibaba is in providers
    alibaba_found = False
    for p in router.providers:
        if p.id == "alibaba":
            alibaba_found = True
            print(f"✅ Alibaba provider loaded in router")
            print(f"   Priority: {p.priority}")
            print(f"   Configured: {p.is_configured}")
            print(f"   Tokens remaining: {p.tokens_remaining:,}")
            break

    if not alibaba_found:
        print("❌ FAILED: Alibaba not in router providers")
        return False

    return True


def test_alibaba_selection():
    """Test 4: Check if Alibaba would be selected."""
    print_section("Test 4: Provider Selection")

    router = FreeRouter(verbose=False)

    # List all configured providers
    configured = [p for p in router.providers if p.is_configured]
    print(f"📊 Configured providers: {len(configured)}/{len(router.providers)}")

    for p in configured:
        status = "✅" if not p.is_exhausted else "⚠️"
        print(
            f"   {status} {p.flag} P{p.priority} {p.name:<25} "
            f"({p.tokens_remaining:,} tokens left)"
        )

    if not configured:
        print("⚠️  No providers configured. Add API keys to .env")
        return False

    return True


def test_router_status():
    """Test 5: Show detailed router status."""
    print_section("Test 5: Router Status")

    router = FreeRouter(verbose=False)
    status = router.status()

    # Session stats
    print("📈 Session Stats:")
    print(f"   Requests: {status['session']['requests']}")
    print(f"   Tokens used: {status['session']['tokens']:,}")
    print(f"   Fallbacks: {status['session']['fallbacks']}")

    # Provider details
    print("\n🏢 Provider Details:")
    for provider in status["providers"]:
        if provider["id"] == "alibaba":
            print(f"\n   Alibaba DashScope:")
            print(f"   Model: {provider['model']}")
            print(f"   Configured: {'✅ Yes' if provider['configured'] else '❌ No'}")
            print(f"   Tokens used: {provider['tokens_used']:,}")
            print(f"   Tokens limit: {provider['tokens_limit']:,}")
            print(f"   Tokens remaining: {provider['tokens_remaining']:,}")
            print(f"   Usage %: {provider['pct_used']:.1f}%")
            print(f"   Exhausted: {'⚠️ Yes' if provider['exhausted'] else '✅ No'}")
            print(f"   Priority: {provider['priority']}")

    return True


def test_alibaba_completion():
    """Test 6: Test actual completion with Alibaba."""
    print_section("Test 6: Completion Test")

    alibaba = get_provider_by_id("alibaba")

    if not alibaba.is_configured:
        print("⚠️  SKIPPED: Alibaba API key not configured")
        print("   Add ALIBABA_API_KEY to .env to enable this test")
        return None

    print("🚀 Testing actual completion request...")
    print("   Sending prompt to Alibaba DashScope...")

    try:
        router = FreeRouter(verbose=False)
        response = router.complete(
            "Say 'Hello from Alibaba DashScope' and confirm you received this message.",
            max_tokens=100,
        )

        print(f"\n✅ SUCCESS! Response received:")
        print(f"   {response[:200]}..." if len(response) > 200 else f"   {response}")

        status = router.status()
        print(f"\n   Tokens used: {status['session']['tokens']:,}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🔀 FreeRouter - Alibaba DashScope Provider Test Suite")
    print("=" * 60)

    tests = [
        ("Configuration", test_alibaba_config),
        ("API Key", test_alibaba_api_key),
        ("Router Setup", test_router_setup),
        ("Provider Selection", test_alibaba_selection),
        ("Router Status", test_router_status),
        ("Completion Test", test_alibaba_completion),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)

    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"{status:<10} {test_name}")

    print(f"\n📊 Results: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0 and skipped <= 1:
        print("\n🎉 All tests passed! Alibaba provider is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check configuration and API key.")

    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
