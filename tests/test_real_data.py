#!/usr/bin/env python
"""
Test script to verify real-time Yahoo Finance data fetching.
Compares with Google Finance values.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def test_real_tesla_data():
    """Fetch and display real Tesla data from Yahoo Finance."""

    print("="*70)
    print("TESTING REAL-TIME YAHOO FINANCE DATA FOR TESLA (TSLA)")
    print("="*70)

    # Fetch Tesla ticker
    tsla = yf.Ticker("TSLA")

    # Get current info
    info = tsla.info

    print("\n📊 CURRENT TESLA STOCK DATA:")
    print("-"*50)

    # Current price
    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    if current_price == 0:
        # Try fast_info as fallback
        current_price = tsla.fast_info.get('lastPrice', 0)

    print(f"Current Price: ${current_price:.2f}")
    print(f"Previous Close: ${info.get('previousClose', 0):.2f}")
    print(f"Day Range: ${info.get('dayLow', 0):.2f} - ${info.get('dayHigh', 0):.2f}")
    print(f"52 Week Range: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}")

    # Key metrics
    print("\n📈 KEY METRICS:")
    print("-"*50)
    print(f"Market Cap: ${info.get('marketCap', 0):,.0f}")
    print(f"P/E Ratio: {info.get('trailingPE', 0):.2f}")
    print(f"P/B Ratio: {info.get('priceToBook', 0):.2f}")
    print(f"Beta: {info.get('beta', 0):.2f}")
    print(f"Volume: {info.get('volume', 0):,}")
    print(f"Avg Volume: {info.get('averageVolume', 0):,}")

    # Company info
    print("\n🏢 COMPANY INFO:")
    print("-"*50)
    print(f"Name: {info.get('longName', 'Tesla, Inc.')}")
    print(f"Sector: {info.get('sector', 'N/A')}")
    print(f"Industry: {info.get('industry', 'N/A')}")
    print(f"Employees: {info.get('fullTimeEmployees', 0):,}")

    # Get historical data
    print("\n📉 RECENT PRICE HISTORY (Last 5 days):")
    print("-"*50)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    history = tsla.history(start=start_date, end=end_date, interval='1d')

    if not history.empty:
        for date, row in history.tail(5).iterrows():
            print(f"{date.strftime('%Y-%m-%d')}: "
                  f"Open: ${row['Open']:.2f}, "
                  f"High: ${row['High']:.2f}, "
                  f"Low: ${row['Low']:.2f}, "
                  f"Close: ${row['Close']:.2f}, "
                  f"Volume: {row['Volume']:,.0f}")

    # Year-to-date performance
    print("\n📊 YEAR-TO-DATE PERFORMANCE:")
    print("-"*50)

    ytd_start = datetime(datetime.now().year, 1, 1)
    ytd_history = tsla.history(start=ytd_start, end=end_date, interval='1d')

    if not ytd_history.empty:
        ytd_start_price = ytd_history.iloc[0]['Close']
        ytd_end_price = ytd_history.iloc[-1]['Close']
        ytd_return = ((ytd_end_price - ytd_start_price) / ytd_start_price) * 100

        print(f"YTD Start Price: ${ytd_start_price:.2f}")
        print(f"Current Price: ${ytd_end_price:.2f}")
        print(f"YTD Return: {ytd_return:+.2f}%")
        print(f"YTD High: ${ytd_history['High'].max():.2f}")
        print(f"YTD Low: ${ytd_history['Low'].min():.2f}")

    # Compare with Google Finance values
    print("\n✅ GOOGLE FINANCE COMPARISON:")
    print("-"*50)
    print("According to Google Finance (as shown):")
    print("- Current Price: $426.07")
    print("- 52 Week Range: $212.11 - $488.54")
    print("- P/E Ratio: 246.95")
    print("- Market Cap: 1.34T USD")

    print(f"\nYahoo Finance shows:")
    print(f"- Current Price: ${current_price:.2f}")
    print(f"- 52 Week Range: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}")
    print(f"- P/E Ratio: {info.get('trailingPE', 0):.2f}")
    print(f"- Market Cap: ${info.get('marketCap', 0)/1e12:.2f}T USD")

    # Check data accuracy
    print("\n🎯 DATA ACCURACY CHECK:")
    print("-"*50)

    price_diff = abs(current_price - 426.07)
    if price_diff < 10:  # Within $10 difference
        print(f"✅ Price is accurate (difference: ${price_diff:.2f})")
    else:
        print(f"⚠️ Price difference detected: ${price_diff:.2f}")

    return current_price

def test_real_samsung_data():
    """Test Samsung Electronics data from Yahoo Finance."""

    print("\n" + "="*70)
    print("TESTING SAMSUNG ELECTRONICS DATA (005930.KS)")
    print("="*70)

    # Samsung on KOSPI uses .KS suffix
    samsung = yf.Ticker("005930.KS")

    info = samsung.info

    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    if current_price == 0:
        current_price = samsung.fast_info.get('lastPrice', 0)

    print(f"\n📊 SAMSUNG CURRENT DATA:")
    print(f"Current Price: ₩{current_price:,.0f}")
    print(f"Previous Close: ₩{info.get('previousClose', 0):,.0f}")
    print(f"Market Cap: ₩{info.get('marketCap', 0):,.0f}")

    print(f"\n✅ GOOGLE FINANCE COMPARISON:")
    print(f"Google shows: ₩79,700")
    print(f"Yahoo shows: ₩{current_price:,.0f}")

    price_diff = abs(current_price - 79700)
    if price_diff < 1000:  # Within ₩1000 difference
        print(f"✅ Price is accurate (difference: ₩{price_diff:,.0f})")
    else:
        print(f"⚠️ Price difference detected: ₩{price_diff:,.0f}")

    return current_price

def main():
    """Run all tests."""
    print("\n" + "🔍 REAL-TIME STOCK DATA VERIFICATION TEST 🔍".center(70))
    print("="*70)
    print("Fetching real data from Yahoo Finance API...")
    print("Comparing with Google Finance values...")
    print("="*70)

    try:
        # Test Tesla
        tesla_price = test_real_tesla_data()

        # Test Samsung
        samsung_price = test_real_samsung_data()

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Tesla (TSLA): ${tesla_price:.2f}")
        print(f"✓ Samsung (005930.KS): ₩{samsung_price:,.0f}")
        print("\nData fetched successfully from Yahoo Finance API!")

    except Exception as e:
        print(f"\n❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
