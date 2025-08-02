"""
Real-time Stock Data Fetcher

Fetches accurate real-time stock data using multiple sources.
Prioritizes actual market data over mock data.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .base import StockDataFetcher
from ..utils.advanced_cache import smart_cache
from ..core.exceptions import DataFetchError

logger = logging.getLogger(__name__)


class RealtimeStockFetcher(StockDataFetcher):
    """Real-time stock data fetcher with multiple data sources."""
    
    def __init__(self, use_cache: bool = True):
        super().__init__(use_cache)
        self.sources = ['yfinance', 'finnhub', 'twelvedata']
        self._configure_session()
        
    def _configure_session(self):
        """Configure HTTP session for API calls."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @smart_cache(ttl=60)  # 1 minute cache for real-time data
    def fetch_realtime_quote(self, ticker: str, market: str = "US") -> Dict[str, Any]:
        """
        Fetch real-time quote with multiple source fallback.
        
        Returns the most accurate available data.
        """
        # Try multiple sources in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._fetch_yfinance_quote, ticker): 'yfinance',
                executor.submit(self._fetch_finnhub_quote, ticker): 'finnhub',
                executor.submit(self._fetch_twelvedata_quote, ticker): 'twelvedata'
            }
            
            results = {}
            for future in as_completed(futures):
                source = futures[future]
                try:
                    data = future.result()
                    if data and data.get('currentPrice'):
                        results[source] = data
                        logger.info(f"Successfully fetched {ticker} from {source}")
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
            
            # Return the best available data
            if results:
                # Prefer yfinance for consistency with historical data
                if 'yfinance' in results:
                    return results['yfinance']
                return list(results.values())[0]
            
            raise DataFetchError(f"Failed to fetch real-time data for {ticker}")
    
    def _fetch_yfinance_quote(self, ticker: str) -> Dict[str, Any]:
        """Fetch quote from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get real-time price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                # Fallback to last close
                current_price = info.get('previousClose')
            
            return {
                'ticker': ticker,
                'currentPrice': current_price,
                '현재가': current_price,
                'previousClose': info.get('previousClose'),
                'dayHigh': info.get('dayHigh'),
                'dayLow': info.get('dayLow'),
                'volume': info.get('volume'),
                'marketCap': info.get('marketCap'),
                '시가총액': info.get('marketCap'),
                'PER': info.get('trailingPE'),
                'PBR': info.get('priceToBook'),
                'dividendYield': info.get('dividendYield'),
                '배당수익률': info.get('dividendYield'),
                '52주최고': info.get('fiftyTwoWeekHigh'),
                '52주최저': info.get('fiftyTwoWeekLow'),
                'beta': info.get('beta'),
                '베타': info.get('beta'),
                'longName': info.get('longName'),
                '회사명': info.get('longName'),
                'sector': info.get('sector'),
                '섹터': info.get('sector'),
                'industry': info.get('industry'),
                '산업': info.get('industry'),
                'source': 'yfinance',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance error for {ticker}: {e}")
            raise
    
    def _fetch_finnhub_quote(self, ticker: str) -> Dict[str, Any]:
        """Fetch quote from Finnhub (requires API key)."""
        # Free tier available at finnhub.io
        api_key = "YOUR_FINNHUB_API_KEY"  # Replace with actual key
        
        try:
            url = f"https://finnhub.io/api/v1/quote"
            params = {"symbol": ticker, "token": api_key}
            
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ticker': ticker,
                    'currentPrice': data.get('c'),  # Current price
                    '현재가': data.get('c'),
                    'dayHigh': data.get('h'),
                    'dayLow': data.get('l'),
                    'previousClose': data.get('pc'),
                    'source': 'finnhub',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Finnhub error for {ticker}: {e}")
            raise
    
    def _fetch_twelvedata_quote(self, ticker: str) -> Dict[str, Any]:
        """Fetch quote from Twelve Data (free tier available)."""
        api_key = "YOUR_TWELVEDATA_API_KEY"  # Replace with actual key
        
        try:
            url = "https://api.twelvedata.com/quote"
            params = {
                "symbol": ticker,
                "apikey": api_key
            }
            
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ticker': ticker,
                    'currentPrice': float(data.get('close', 0)),
                    '현재가': float(data.get('close', 0)),
                    'dayHigh': float(data.get('high', 0)),
                    'dayLow': float(data.get('low', 0)),
                    'volume': int(data.get('volume', 0)),
                    'previousClose': float(data.get('previous_close', 0)),
                    'source': 'twelvedata',
                    'timestamp': data.get('datetime')
                }
        except Exception as e:
            logger.error(f"TwelveData error for {ticker}: {e}")
            raise
    
    @smart_cache(ttl=300)  # 5 minutes cache
    def fetch_market_indices(self) -> Dict[str, Any]:
        """Fetch major market indices including VIX."""
        indices = {
            'S&P500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW': '^DJI',
            'VIX': '^VIX',  # Fear Index
            'KOSPI': '^KS11',
            'KOSDAQ': '^KQ11'
        }
        
        results = {}
        for name, symbol in indices.items():
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                history = stock.history(period='1d')
                
                if not history.empty:
                    current = history['Close'].iloc[-1]
                    prev_close = info.get('previousClose', current)
                    change = ((current - prev_close) / prev_close) * 100
                    
                    results[name] = {
                        'symbol': symbol,
                        'name': name,
                        'current': round(current, 2),
                        'change': round(change, 2),
                        'previous_close': prev_close
                    }
                    
                    # Special handling for VIX
                    if name == 'VIX':
                        results[name]['fear_level'] = self._get_fear_level(current)
                        
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
        
        return results
    
    def _get_fear_level(self, vix_value: float) -> str:
        """Interpret VIX fear level."""
        if vix_value < 12:
            return "극도의 낙관 (Extreme Greed)"
        elif vix_value < 20:
            return "낮은 변동성 (Low Volatility)"
        elif vix_value < 30:
            return "보통 변동성 (Moderate Volatility)"
        elif vix_value < 40:
            return "높은 변동성 (High Volatility)"
        else:
            return "극도의 공포 (Extreme Fear)"
    
    def fetch_price_history(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch historical price data from Yahoo Finance."""
        try:
            # Direct download for better performance
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                threads=False
            )
            
            if df.empty:
                raise DataFetchError(f"No historical data found for {ticker}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch history for {ticker}: {e}")
            raise DataFetchError(f"Historical data fetch failed: {str(e)}")
    
    def fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch company information using real-time data sources.
        
        This method uses the realtime quote as the primary source.
        """
        return self.fetch_realtime_quote(ticker)
    
    def fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch financial data for the stock.
        
        For real-time fetcher, this returns the same data as company info
        since we're focused on real-time quotes.
        """
        try:
            # Get real-time quote which includes financial metrics
            quote_data = self.fetch_realtime_quote(ticker)
            
            # Extract financial specific data
            financial_data = {
                'ticker': ticker,
                'revenue': quote_data.get('revenue'),
                'earnings': quote_data.get('earnings'),
                'eps': quote_data.get('EPS'),
                'pe_ratio': quote_data.get('PER'),
                'market_cap': quote_data.get('marketCap'),
                'dividend_yield': quote_data.get('dividendYield'),
                'profit_margin': quote_data.get('profit_margin'),
                'roe': quote_data.get('ROE'),
                'debt_to_equity': quote_data.get('debt_to_equity'),
                'current_ratio': quote_data.get('current_ratio'),
                'source': 'realtime',
                'timestamp': datetime.now().isoformat()
            }
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Failed to fetch financial data for {ticker}: {e}")
            # Return minimal financial data
            return {
                'ticker': ticker,
                'error': str(e),
                'source': 'realtime',
                'timestamp': datetime.now().isoformat()
            }