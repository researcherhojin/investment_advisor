#!/usr/bin/env python
"""Test script to verify all fixes are working."""

from investment_advisor.agents.risk_manager import RiskManagerAgent
from investment_advisor.data.stable_fetcher import StableFetcher
from investment_advisor.data.simple_fetcher import SimpleStockFetcher

def test_samsung_price():
    """Test Samsung stock price is correct."""
    print('Testing Samsung (005930)...')
    stable_fetcher = StableFetcher()
    samsung_data = stable_fetcher.fetch_quote('005930')
    price = samsung_data.get('currentPrice', 'N/A')
    print(f'Samsung current price: {price:,} KRW')

    # Check if price is around 79,700 (with ±2% variation)
    if 78000 < price < 81500:
        print('✅ Samsung price is correct!')
    else:
        print(f'❌ Samsung price seems wrong. Expected ~79,700, got {price}')
    return price

def test_risk_manager():
    """Test RiskManager with fixed methods."""
    print('\nTesting RiskManager...')
    risk_mgr = RiskManagerAgent()

    try:
        # Test Korean stock risk metrics
        metrics = risk_mgr._get_korea_risk_metrics('005930')
        var = metrics.get('Value at Risk', 'N/A')
        print(f'Risk metrics calculated: VaR={var}')

        # Test US stock risk metrics
        us_metrics = risk_mgr._get_us_risk_metrics('TSLA')
        us_var = us_metrics.get('Value at Risk', 'N/A')
        print(f'US Risk metrics calculated: VaR={us_var}')

        print('✅ RiskManager methods working correctly!')
        return True
    except Exception as e:
        print(f'❌ Error in risk manager: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_tesla_price():
    """Test Tesla stock price and history."""
    print('\nTesting Tesla (TSLA)...')
    stable_fetcher = StableFetcher()
    tesla_data = stable_fetcher.fetch_quote('TSLA')
    price = tesla_data.get('currentPrice', 'N/A')
    print(f'Tesla current price: ${price}')

    # Check if price is around 426 (with ±2% variation)
    if 415 < price < 435:
        print('✅ Tesla price is correct!')
    else:
        print(f'❌ Tesla price seems wrong. Expected ~426, got {price}')

    # Test price history
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    history = stable_fetcher.fetch_price_history('TSLA', start_date, end_date)
    if not history.empty:
        min_price = history['Low'].min()
        max_price = history['High'].max()
        print(f'Tesla price range (last year): ${min_price:.2f} - ${max_price:.2f}')

        # Check if the range is realistic (should have hit lows around 140-180)
        if min_price < 200 and max_price < 450:
            print('✅ Tesla price history is realistic!')
        else:
            print(f'❌ Tesla price history seems unrealistic')

    return price

def main():
    """Run all tests."""
    print('='*60)
    print('Testing Stock Analysis System Fixes')
    print('='*60)

    samsung_price = test_samsung_price()
    risk_ok = test_risk_manager()
    tesla_price = test_tesla_price()

    print('\n' + '='*60)
    print('Test Summary:')
    print(f'- Samsung price: {samsung_price:,} KRW (target: 79,700)')
    print(f'- Risk Manager: {"✅ Working" if risk_ok else "❌ Failed"}')
    print(f'- Tesla price: ${tesla_price} (target: 426)')
    print('='*60)

if __name__ == '__main__':
    main()
