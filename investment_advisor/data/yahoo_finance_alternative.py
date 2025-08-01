"""
Alternative data fetching methods when Yahoo Finance is rate limited
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import requests
import json

logger = logging.getLogger(__name__)


class AlternativeDataFetcher:
    """Alternative methods for fetching stock data when Yahoo Finance fails."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_from_financialmodelingprep(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch data from Financial Modeling Prep (free tier available).
        Note: Requires API key for production use
        """
        try:
            # This is a demo endpoint - for production, use API key
            url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    quote = data[0]
                    return {
                        "현재가": quote.get("price"),
                        "52주 최고가": quote.get("yearHigh"),
                        "52주 최저가": quote.get("yearLow"),
                        "거래량": quote.get("volume"),
                        "시가총액": quote.get("marketCap"),
                        "PER": quote.get("pe"),
                        "EPS": quote.get("eps"),
                        "회사명": quote.get("name"),
                        "거래소": quote.get("exchange"),
                    }
        except Exception as e:
            logger.error(f"Error fetching from FinancialModelingPrep: {e}")
        
        return {}
    
    def fetch_from_alphavantage(self, ticker: str, api_key: str) -> Dict[str, Any]:
        """
        Fetch data from Alpha Vantage API.
        """
        if not api_key:
            logger.warning("Alpha Vantage API key not provided")
            return {}
        
        try:
            # Global Quote endpoint
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    return {
                        "현재가": float(quote.get("05. price", 0)),
                        "거래량": int(quote.get("06. volume", 0)),
                        "최고가": float(quote.get("03. high", 0)),
                        "최저가": float(quote.get("04. low", 0)),
                        "전일종가": float(quote.get("08. previous close", 0)),
                        "변동률": quote.get("10. change percent", "0%"),
                    }
        except Exception as e:
            logger.error(f"Error fetching from Alpha Vantage: {e}")
        
        return {}
    
    def fetch_from_iex_cloud(self, ticker: str, token: str = None) -> Dict[str, Any]:
        """
        Fetch data from IEX Cloud (has free tier).
        """
        try:
            # Using sandbox for demo (replace with cloud.iexapis.com for production)
            base_url = "https://sandbox.iexapis.com/stable"
            
            # For demo purposes, using test token
            if not token:
                token = "Tpk_"  # Use actual token in production
            
            url = f"{base_url}/stock/{ticker}/quote"
            params = {"token": token}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "현재가": data.get("latestPrice"),
                    "52주 최고가": data.get("week52High"),
                    "52주 최저가": data.get("week52Low"),
                    "거래량": data.get("volume"),
                    "시가총액": data.get("marketCap"),
                    "PER": data.get("peRatio"),
                    "회사명": data.get("companyName"),
                    "섹터": data.get("sector"),
                }
        except Exception as e:
            logger.error(f"Error fetching from IEX Cloud: {e}")
        
        return {}
    
    def create_mock_data(self, ticker: str) -> Dict[str, Any]:
        """
        Create mock data for testing when all APIs fail.
        This should only be used for development/testing.
        """
        import random
        
        base_price = random.uniform(50, 500)
        
        return {
            "현재가": round(base_price, 2),
            "PER": round(random.uniform(10, 30), 2),
            "PBR": round(random.uniform(1, 5), 2),
            "ROE": round(random.uniform(5, 25), 2),
            "배당수익률": round(random.uniform(0, 5), 2),
            "시가총액": random.randint(1000000000, 1000000000000),
            "52주 최고가": round(base_price * random.uniform(1.1, 1.5), 2),
            "52주 최저가": round(base_price * random.uniform(0.5, 0.9), 2),
            "베타": round(random.uniform(0.5, 2), 2),
            "거래량": random.randint(1000000, 50000000),
            "EPS": round(random.uniform(1, 10), 2),
            "Revenue": random.randint(1000000000, 100000000000),
            "Profit Margin": round(random.uniform(5, 30), 2),
            "회사명": f"{ticker} Corp",
            "섹터": "Technology",
            "산업": "Software",
            "국가": "US",
            "직원수": random.randint(1000, 100000),
        }
    
    def create_mock_price_history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """
        Create mock price history for testing.
        """
        import numpy as np
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate random walk for prices
        base_price = 100.0
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Create OHLCV data with explicit data types
        df = pd.DataFrame(index=dates)
        df['Open'] = (prices * np.random.uniform(0.98, 1.02, days)).astype(float)
        df['High'] = (prices * np.random.uniform(1.0, 1.05, days)).astype(float)
        df['Low'] = (prices * np.random.uniform(0.95, 1.0, days)).astype(float)
        df['Close'] = prices.astype(float)
        df['Volume'] = np.random.randint(1000000, 50000000, days).astype(int)
        
        # Reset index to make it serializable
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)
        
        # Ensure consistent data types
        df['Date'] = df['Date'].dt.date  # Convert to date only
        df['Open'] = df['Open'].round(2)
        df['High'] = df['High'].round(2)
        df['Low'] = df['Low'].round(2)
        df['Close'] = df['Close'].round(2)
        
        return df