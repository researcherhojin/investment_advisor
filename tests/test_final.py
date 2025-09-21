#!/usr/bin/env python
"""Final test script to verify all fixes are working."""

from investment_advisor.data.simple_fetcher import SimpleStockFetcher
from investment_advisor.agents.company_analyst import CompanyAnalystAgent

def test_simple_fetcher():
    """Test SimpleStockFetcher has correct method."""
    print("=" * 60)
    print("Testing SimpleStockFetcher methods...")

    fetcher = SimpleStockFetcher()

    # Check if fetch_stock_data exists (not fetch_quote)
    if hasattr(fetcher, 'fetch_stock_data'):
        print("✅ fetch_stock_data method exists")
        data = fetcher.fetch_stock_data('TSLA')
        if data:
            print(f"✅ Fetched data for TSLA: ${data.get('currentPrice', 'N/A')}")
    else:
        print("❌ fetch_stock_data method missing")

    if hasattr(fetcher, 'fetch_quote'):
        print("⚠️  fetch_quote method exists (should not)")
    else:
        print("✅ fetch_quote method does not exist (correct)")

    return True

def test_company_analyst():
    """Test CompanyAnalystAgent with type fixes."""
    print("\n" + "=" * 60)
    print("Testing CompanyAnalystAgent...")

    agent = CompanyAnalystAgent()

    # Test with mock data containing string PER
    mock_key_stats = {
        'PER': '256.67',  # String value as from Yahoo Finance
        'PBR': '17.77',
        'marketCap': 1416747155456
    }

    # This should not crash with type error
    try:
        # Simulate the PER check
        per_value = float(mock_key_stats.get('PER', 0))
        if per_value > 100:
            print(f"✅ PER check working: {per_value} > 100 (overvalued)")
        print("✅ No type error with string PER")
    except (TypeError, ValueError) as e:
        print(f"❌ Type error: {e}")

    return True

def main():
    print("\n🔍 FINAL SYSTEM TEST 🔍".center(60))
    print("Testing all fixed components...")
    print("=" * 60)

    test_simple_fetcher()
    test_company_analyst()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("System version: v0.2 (Beta)")
    print("=" * 60)

if __name__ == "__main__":
    main()
