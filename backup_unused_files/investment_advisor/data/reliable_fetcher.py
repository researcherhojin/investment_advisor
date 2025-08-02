"""
Reliable Data Fetcher

Uses multiple data sources with fallback mechanisms to ensure data availability.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import requests
import time
import random

logger = logging.getLogger(__name__)


class ReliableDataFetcher:
    """Reliable data fetcher with multiple sources and fallbacks."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_stock_data(self, ticker: str, market: str = "미국장") -> Dict[str, Any]:
        """Fetch stock data with multiple fallbacks."""
        logger.info(f"Fetching data for {ticker} from {market}")
        
        # Try multiple sources in order (skip finnhub and polygon for now due to API key requirements)
        data_sources = [
            self._fetch_from_yahoo_alternative,
            self._create_realistic_mock_data
        ]
        
        for source_func in data_sources:
            try:
                self._rate_limit()
                data = source_func(ticker, market)
                if data and self._validate_data(data):
                    logger.info(f"Successfully fetched data for {ticker} from {source_func.__name__}")
                    return data
            except Exception as e:
                logger.warning(f"Failed to fetch from {source_func.__name__}: {e}")
                continue
        
        # If all sources fail, return mock data
        logger.warning(f"All sources failed for {ticker}, using fallback mock data")
        return self._create_realistic_mock_data(ticker, market)
    
    def _fetch_from_finnhub(self, ticker: str, market: str) -> Dict[str, Any]:
        """Fetch from Finnhub (requires API key for production)."""
        # Demo endpoint (limited functionality)
        try:
            # Basic quote endpoint
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': ticker,
                'token': 'demo'  # Use actual API key in production
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'ticker': ticker,
                    'currentPrice': data.get('c'),  # Current price
                    '52주 최고가': data.get('h'),   # High price of the day
                    '52주 최저가': data.get('l'),   # Low price of the day
                    'previousClose': data.get('pc'), # Previous close
                    'change': data.get('d'),         # Change
                    'changePercent': data.get('dp'), # Change percent
                    'timestamp': data.get('t'),      # Unix timestamp
                    '회사명': f"{ticker} Inc.",
                    'source': 'finnhub'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Finnhub fetch error: {e}")
            return None
    
    def _fetch_from_polygon(self, ticker: str, market: str) -> Dict[str, Any]:
        """Fetch from Polygon.io (requires API key)."""
        try:
            # Demo/free tier endpoint
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
            params = {
                'apikey': 'demo'  # Use actual API key in production
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    result = results[0]
                    return {
                        'ticker': ticker,
                        'currentPrice': result.get('c'),  # Close price
                        '52주 최고가': result.get('h'),   # High
                        '52주 최저가': result.get('l'),   # Low
                        'open': result.get('o'),          # Open
                        'volume': result.get('v'),        # Volume
                        'timestamp': result.get('t'),     # Timestamp
                        '회사명': f"{ticker} Corporation",
                        'source': 'polygon'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Polygon fetch error: {e}")
            return None
    
    def _fetch_from_yahoo_alternative(self, ticker: str, market: str) -> Dict[str, Any]:
        """Alternative Yahoo Finance approach with better error handling."""
        try:
            # Try multiple Yahoo endpoints
            endpoints = [
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}",
            ]
            
            for url in endpoints:
                try:
                    params = {
                        'interval': '1d',
                        'range': '5d',  # Get more data for better reliability
                        'includePrePost': 'false'
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        chart = data.get('chart', {})
                        
                        if chart.get('error'):
                            continue
                            
                        results = chart.get('result', [])
                        
                        if results:
                            result = results[0]
                            meta = result.get('meta', {})
                            
                            # Get current price from the most recent data
                            current_price = meta.get('regularMarketPrice')
                            if not current_price:
                                # Try to get from timestamp data
                                timestamp_data = result.get('timestamp', [])
                                indicators = result.get('indicators', {})
                                quote = indicators.get('quote', [{}])
                                
                                if quote and quote[0] and 'close' in quote[0]:
                                    closes = quote[0]['close']
                                    # Get the last non-null close price
                                    for close_price in reversed(closes):
                                        if close_price is not None:
                                            current_price = close_price
                                            break
                            
                            if current_price:
                                return {
                                    'ticker': ticker,
                                    'currentPrice': current_price,
                                    '현재가': current_price,
                                    '52주 최고가': meta.get('fiftyTwoWeekHigh'),
                                    '52주 최저가': meta.get('fiftyTwoWeekLow'),
                                    'previousClose': meta.get('previousClose'),
                                    'marketCap': meta.get('marketCap'),
                                    'volume': meta.get('regularMarketVolume'),
                                    '회사명': meta.get('longName', f"{ticker} Inc."),
                                    'longName': meta.get('longName', f"{ticker} Inc."),
                                    'currency': meta.get('currency', 'USD'),
                                    'source': 'yahoo_alternative'
                                }
                
                except requests.exceptions.RequestException as req_error:
                    logger.warning(f"Request failed for {url}: {req_error}")
                    continue
                except Exception as endpoint_error:
                    logger.warning(f"Endpoint {url} failed: {endpoint_error}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Yahoo alternative fetch error: {e}")
            return None
    
    def _create_realistic_mock_data(self, ticker: str, market: str) -> Dict[str, Any]:
        """Create realistic mock data based on ticker patterns."""
        logger.info(f"Creating realistic mock data for {ticker}")
        
        # Set realistic base prices based on common tickers
        base_prices = {
            'AAPL': 175.0,
            'MSFT': 350.0,
            'GOOGL': 2800.0,
            'TSLA': 800.0,
            'AMZN': 3200.0,
            'NVDA': 900.0,
            'META': 300.0,
            'NFLX': 450.0,
        }
        
        # Get base price or generate reasonable one
        if ticker in base_prices:
            base_price = base_prices[ticker]
        else:
            # Generate price based on ticker characteristics
            if len(ticker) <= 4 and ticker.isalpha():
                base_price = random.uniform(50, 500)  # US stocks
            else:
                base_price = random.uniform(10000, 100000)  # Korean stocks (in KRW)
        
        # Add some realistic variation
        current_price = base_price * random.uniform(0.95, 1.05)
        
        # Calculate other metrics
        high_52w = current_price * random.uniform(1.1, 1.8)
        low_52w = current_price * random.uniform(0.4, 0.9)
        
        # Market cap based on price range
        if current_price > 1000:
            market_cap = random.randint(50, 2000) * 1_000_000_000  # 50B - 2T
        elif current_price > 100:
            market_cap = random.randint(10, 500) * 1_000_000_000   # 10B - 500B
        else:
            market_cap = random.randint(1, 50) * 1_000_000_000     # 1B - 50B
        
        return {
            'ticker': ticker,
            'currentPrice': round(current_price, 2),
            '현재가': round(current_price, 2),
            'PER': round(random.uniform(15, 35), 1),
            'PBR': round(random.uniform(1.2, 4.5), 1),
            'ROE': round(random.uniform(8, 25), 1),
            '배당수익률': round(random.uniform(0, 4), 2),
            '시가총액': market_cap,
            'marketCap': market_cap,
            '52주 최고가': round(high_52w, 2),
            '52주 최저가': round(low_52w, 2),
            '베타': round(random.uniform(0.8, 1.8), 2),
            '거래량': random.randint(1_000_000, 100_000_000),
            'EPS': round(random.uniform(2, 15), 2),
            'Revenue': random.randint(1_000_000_000, 500_000_000_000),
            '회사명': f"{ticker} Corporation",
            '섹터': "Technology" if market == "미국장" else "기술",
            '산업': "Software" if market == "미국장" else "소프트웨어",
            '국가': "US" if market == "미국장" else "KR",
            '직원수': random.randint(1000, 200000),
            'source': 'realistic_mock',
            'data_quality': 'mock_but_realistic'  # Flag for UI
        }
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate fetched data quality."""
        if not data:
            return False
        
        # Check for essential fields
        essential_fields = ['ticker', 'currentPrice']
        
        for field in essential_fields:
            if field not in data or data[field] is None:
                return False
        
        # Check price reasonableness
        price = data.get('currentPrice')
        if isinstance(price, (int, float)):
            if price <= 0 or price > 100000:  # Reasonable price range
                return False
        
        return True
    
    def create_price_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """Create realistic price history."""
        try:
            # Get current data first
            current_data = self.fetch_stock_data(ticker)
            current_price = current_data.get('currentPrice', 100.0)
            
            # Generate dates
            end_date = datetime.now()
            dates = pd.date_range(end=end_date, periods=days, freq='D')
            
            # Generate realistic price movements
            import numpy as np
            
            # Parameters for price simulation
            daily_return_mean = 0.0005  # Small positive drift
            daily_volatility = 0.02     # 2% daily volatility
            
            # Generate returns using geometric Brownian motion
            returns = np.random.normal(daily_return_mean, daily_volatility, days)
            
            # Calculate cumulative prices
            price_ratios = np.exp(np.cumsum(returns))
            
            # Scale to end at current price
            prices = current_price * price_ratios / price_ratios[-1]
            
            # Create OHLCV data
            df = pd.DataFrame(index=dates)
            df['Close'] = prices
            df['Open'] = df['Close'].shift(1).fillna(df['Close'].iloc[0])
            df['High'] = df[['Open', 'Close']].max(axis=1) * np.random.uniform(1.0, 1.03, days)
            df['Low'] = df[['Open', 'Close']].min(axis=1) * np.random.uniform(0.97, 1.0, days)
            df['Volume'] = np.random.randint(1000000, 50000000, days)
            
            # Round prices
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].round(2)
            
            return df
            
        except Exception as e:
            logger.error(f"Error creating price history: {e}")
            
            # Return minimal dataframe
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            df = pd.DataFrame(index=dates)
            df['Close'] = 100.0
            df['Open'] = 100.0
            df['High'] = 102.0
            df['Low'] = 98.0
            df['Volume'] = 1000000
            
            return df