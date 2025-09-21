#!/usr/bin/env python
"""
Test the application with real Yahoo Finance data integration.
"""

from investment_advisor.analysis.decision_system import InvestmentDecisionSystem
from datetime import datetime

def test_tesla_analysis():
    """Test Tesla analysis with real data."""
    print("="*70)
    print("TESTING TESLA ANALYSIS WITH REAL YAHOO FINANCE DATA")
    print("="*70)

    try:
        # Initialize decision system
        decision_system = InvestmentDecisionSystem()

        # Check which fetcher is being used
        if hasattr(decision_system, 'yahoo_fetcher') and decision_system.yahoo_fetcher:
            print("✅ Using Yahoo Finance for real-time data")
        else:
            print("⚠️ Yahoo Finance not available, using fallback")

        # Fetch Tesla data
        print("\nFetching TSLA data...")
        stock_data, price_history = decision_system._fetch_stock_data('TSLA', '미국장', 3)

        if stock_data:
            print("\n📊 TESLA DATA FROM APPLICATION:")
            print(f"Current Price: ${stock_data.get('currentPrice', 'N/A'):.2f}")
            print(f"Previous Close: ${stock_data.get('previousClose', 'N/A'):.2f}")
            print(f"P/E Ratio: {stock_data.get('PER', 'N/A')}")
            print(f"Market Cap: ${stock_data.get('marketCap', 0)/1e12:.2f}T")
            print(f"Data Source: {stock_data.get('fetcher', 'unknown')}")

            # Check price history
            if not price_history.empty:
                latest = price_history.tail(1)
                print(f"\nLatest Price History Entry:")
                print(f"Date: {latest.index[0] if hasattr(latest, 'index') else latest['Date'].iloc[0]}")
                print(f"Close: ${latest['Close'].iloc[0]:.2f}")
                print(f"Volume: {latest['Volume'].iloc[0]:,.0f}")

            # Compare with expected Google Finance value
            current = stock_data.get('currentPrice', 0)
            expected = 426.07
            diff = abs(current - expected)

            print(f"\n🎯 ACCURACY CHECK:")
            print(f"Expected (Google Finance): ${expected}")
            print(f"Actual (Our App): ${current:.2f}")
            print(f"Difference: ${diff:.2f}")

            if diff < 10:
                print("✅ Data is accurate!")
            else:
                print("⚠️ Price difference detected")

        else:
            print("❌ Failed to fetch stock data")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_samsung_analysis():
    """Test Samsung analysis with real data."""
    print("\n" + "="*70)
    print("TESTING SAMSUNG ANALYSIS WITH REAL YAHOO FINANCE DATA")
    print("="*70)

    try:
        # Initialize decision system
        decision_system = InvestmentDecisionSystem()

        # Fetch Samsung data
        print("\nFetching 005930 (Samsung) data...")
        stock_data, price_history = decision_system._fetch_stock_data('005930', '한국장', 3)

        if stock_data:
            print("\n📊 SAMSUNG DATA FROM APPLICATION:")
            print(f"Current Price: ₩{stock_data.get('currentPrice', 'N/A'):,.0f}")
            print(f"Previous Close: ₩{stock_data.get('previousClose', 'N/A'):,.0f}")
            print(f"Data Source: {stock_data.get('fetcher', 'unknown')}")

            # Compare with expected value
            current = stock_data.get('currentPrice', 0)
            expected = 79700
            diff = abs(current - expected)

            print(f"\n🎯 ACCURACY CHECK:")
            print(f"Expected (Google Finance): ₩{expected:,}")
            print(f"Actual (Our App): ₩{current:,.0f}")
            print(f"Difference: ₩{diff:,.0f}")

            if diff < 1000:
                print("✅ Data is accurate!")
            else:
                print("⚠️ Price difference detected")

        else:
            print("❌ Failed to fetch stock data")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("\n🔍 APPLICATION DATA ACCURACY TEST 🔍".center(70))
    print("Testing integration with real Yahoo Finance API...")
    print("="*70)

    test_tesla_analysis()
    test_samsung_analysis()

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
