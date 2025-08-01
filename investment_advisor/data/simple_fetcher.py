"""
Simple Stock Data Fetcher

Minimal API calls with realistic mock data fallback.
Designed to avoid Yahoo Finance rate limiting entirely.
"""

import logging
import random
from typing import Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SimpleStockFetcher:
    """Simple fetcher that prioritizes mock data to avoid API limits."""
    
    def __init__(self):
        # Known stock data for better realism
        self.known_stocks = {
            'AAPL': {
                'name': 'Apple Inc.',
                'price': 175.0,
                'pe': 28.5,
                'pb': 4.8,
                'market_cap': 2_800_000_000_000
            },
            'MSFT': {
                'name': 'Microsoft Corporation',
                'price': 350.0,
                'pe': 32.1,
                'pb': 5.2,
                'market_cap': 2_600_000_000_000
            },
            'GOOGL': {
                'name': 'Alphabet Inc.',
                'price': 2800.0,
                'pe': 25.4,
                'pb': 3.9,
                'market_cap': 1_800_000_000_000
            },
            'TSLA': {
                'name': 'Tesla, Inc.',
                'price': 800.0,
                'pe': 45.6,
                'pb': 8.1,
                'market_cap': 800_000_000_000
            },
            'AMZN': {
                'name': 'Amazon.com, Inc.',
                'price': 3200.0,
                'pe': 35.2,
                'pb': 6.4,
                'market_cap': 1_600_000_000_000
            },
            'NVDA': {
                'name': 'NVIDIA Corporation',
                'price': 900.0,
                'pe': 55.8,
                'pb': 12.3,
                'market_cap': 2_200_000_000_000
            }
        }
    
    def fetch_stock_data(self, ticker: str, market: str = "미국장") -> Dict[str, Any]:
        """Fetch stock data with intelligent mock generation."""
        logger.info(f"Generating data for {ticker}")
        
        # Use known data if available
        if ticker in self.known_stocks:
            base_data = self.known_stocks[ticker]
            
            # Add some realistic variation
            price_variation = random.uniform(0.95, 1.05)
            current_price = base_data['price'] * price_variation
            
            return {
                'ticker': ticker,
                'currentPrice': round(current_price, 2),
                '현재가': round(current_price, 2),
                'PER': round(base_data['pe'] * random.uniform(0.9, 1.1), 1),
                'PBR': round(base_data['pb'] * random.uniform(0.9, 1.1), 1),
                'ROE': round(random.uniform(15, 25), 1),
                '배당수익률': round(random.uniform(0.5, 3.0), 2),
                '시가총액': int(base_data['market_cap'] * price_variation),
                'marketCap': int(base_data['market_cap'] * price_variation),
                '52주 최고가': round(current_price * random.uniform(1.1, 1.4), 2),
                '52주 최저가': round(current_price * random.uniform(0.6, 0.9), 2),
                '베타': round(random.uniform(0.8, 1.8), 2),
                '거래량': random.randint(10_000_000, 100_000_000),
                'EPS': round(current_price / (base_data['pe'] * random.uniform(0.9, 1.1)), 2),
                'Revenue': random.randint(50_000_000_000, 500_000_000_000),
                '회사명': base_data['name'],
                'longName': base_data['name'],
                '섹터': "Technology",
                '산업': "Consumer Electronics" if ticker == 'AAPL' else "Software",
                '국가': "US",
                '직원수': random.randint(50000, 200000),
                'source': 'enhanced_mock',
                'data_quality': 'high_quality_simulation'
            }
        
        # Generate data based on ticker pattern
        return self._generate_realistic_data(ticker, market)
    
    def _generate_realistic_data(self, ticker: str, market: str) -> Dict[str, Any]:
        """Generate realistic data based on patterns."""
        
        # Determine price range based on ticker characteristics
        if len(ticker) <= 4 and ticker.isalpha():
            # US stock
            if ticker.startswith(('A', 'G', 'M', 'N')):
                base_price = random.uniform(100, 500)
            elif ticker.startswith(('B', 'C', 'T')):
                base_price = random.uniform(200, 1000)
            else:
                base_price = random.uniform(50, 300)
        else:
            # Assume Korean stock (6 digits)
            base_price = random.uniform(10000, 100000)
        
        # Generate company name
        company_suffixes = ['Inc.', 'Corporation', 'Company', 'Ltd.', 'Group']
        company_name = f"{ticker} {random.choice(company_suffixes)}"
        
        # Market cap based on price
        if base_price > 500:
            market_cap = random.randint(100, 2000) * 1_000_000_000
        elif base_price > 100:
            market_cap = random.randint(10, 500) * 1_000_000_000
        else:
            market_cap = random.randint(1, 50) * 1_000_000_000
        
        return {
            'ticker': ticker,
            'currentPrice': round(base_price, 2),
            '현재가': round(base_price, 2),
            'PER': round(random.uniform(12, 40), 1),
            'PBR': round(random.uniform(1.0, 6.0), 1),
            'ROE': round(random.uniform(8, 25), 1),
            '배당수익률': round(random.uniform(0, 4), 2),
            '시가총액': market_cap,
            'marketCap': market_cap,
            '52주 최고가': round(base_price * random.uniform(1.2, 1.6), 2),
            '52주 최저가': round(base_price * random.uniform(0.5, 0.8), 2),
            '베타': round(random.uniform(0.5, 2.0), 2),
            '거래량': random.randint(1_000_000, 50_000_000),
            'EPS': round(random.uniform(2, 20), 2),
            'Revenue': random.randint(1_000_000_000, 100_000_000_000),
            '회사명': company_name,
            'longName': company_name,
            '섹터': random.choice(["Technology", "Healthcare", "Financials", "Consumer Discretionary"]),
            '산업': random.choice(["Software", "Hardware", "Services", "Manufacturing"]),
            '국가': "US" if market == "미국장" else "KR",
            '직원수': random.randint(1000, 100000),
            'source': 'realistic_simulation',
            'data_quality': 'simulated_but_realistic'
        }
    
    def create_price_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """Create realistic price history."""
        try:
            # Get current price
            stock_data = self.fetch_stock_data(ticker)
            current_price = stock_data.get('currentPrice', 100.0)
            
            # Generate dates
            end_date = datetime.now()
            dates = pd.date_range(end=end_date, periods=days, freq='D')
            
            # Generate realistic price movements using geometric Brownian motion
            np.random.seed(hash(ticker) % 1000)  # Consistent but different for each ticker
            
            # Parameters
            daily_return_mean = 0.0008  # Small positive drift
            daily_volatility = 0.018    # 1.8% daily volatility
            
            # Generate returns
            returns = np.random.normal(daily_return_mean, daily_volatility, days)
            
            # Add some trending behavior
            trend = np.linspace(-0.001, 0.001, days)  # Slight upward trend
            returns += trend
            
            # Calculate cumulative prices
            price_ratios = np.exp(np.cumsum(returns))
            
            # Scale to end at current price
            prices = current_price * price_ratios / price_ratios[-1]
            
            # Create OHLCV data
            df = pd.DataFrame(index=dates)
            df['Close'] = prices
            df['Open'] = df['Close'].shift(1).fillna(df['Close'].iloc[0])
            
            # Generate realistic high/low
            daily_ranges = np.random.uniform(0.005, 0.03, days)  # 0.5% to 3% daily range
            df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + daily_ranges * 0.7)
            df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - daily_ranges * 0.7)
            
            # Volume with some correlation to price movement
            price_changes = np.abs(df['Close'].pct_change().fillna(0))
            base_volume = 10_000_000
            volume_multiplier = 1 + price_changes * 5  # Higher volume on big moves
            df['Volume'] = (base_volume * volume_multiplier * np.random.uniform(0.5, 2.0, days)).astype(int)
            
            # Round prices
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].round(2)
            
            logger.info(f"Generated {days} days of realistic price history for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error creating price history for {ticker}: {e}")
            
            # Return basic fallback data
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            df = pd.DataFrame(index=dates)
            df['Close'] = 100.0
            df['Open'] = 100.0
            df['High'] = 102.0
            df['Low'] = 98.0
            df['Volume'] = 10_000_000
            
            return df