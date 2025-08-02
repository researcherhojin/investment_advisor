"""
US Stock Data Fetcher

Handles fetching data for US stocks using yfinance.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random

import pandas as pd
import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

from .base import StockDataFetcher
from ..utils.advanced_cache import smart_cache, get_global_cache
from .yahoo_finance_alternative import AlternativeDataFetcher
from .reliable_fetcher import ReliableDataFetcher
from .simple_fetcher import SimpleStockFetcher
from ..core.mixins import RetryMixin, CacheMixin
from ..core.exceptions import DataFetchError, RateLimitError

logger = logging.getLogger(__name__)


class USStockDataFetcher(StockDataFetcher, RetryMixin):
    """Data fetcher for US stock market."""
    
    def __init__(self, use_cache: bool = True):
        super().__init__(use_cache)
        self.market_indices = {
            "S&P500": "^GSPC",
            "NASDAQ": "^IXIC",
            "DOW": "^DJI"
        }
        # Add delay between requests to avoid rate limiting
        self.request_delay = 1.5
        # Configure session with retry strategy
        self._configure_requests_session()
        # Alternative data fetcher for when Yahoo Finance fails
        self.alternative_fetcher = AlternativeDataFetcher()
        # Reliable data fetcher with multiple sources
        self.reliable_fetcher = ReliableDataFetcher()
        # Simple fetcher with high-quality mock data (primary for demo)
        self.simple_fetcher = SimpleStockFetcher()
        # Get Alpha Vantage API key from environment
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    def _configure_requests_session(self):
        """Configure requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers to avoid detection
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    @smart_cache(ttl=900)  # 15 minutes cache
    def fetch_price_history(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch historical price data for US stocks with intelligent caching."""
        
        # For demo purposes, use simple fetcher first to avoid API limits
        try:
            days = (end_date - start_date).days
            df = self.simple_fetcher.create_price_history(ticker, days=days)
            
            # Filter to requested date range
            if not df.empty:
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                if not df.empty:
                    logger.info(f"Successfully generated {len(df)} days of realistic data for {ticker}")
                    return df
        except Exception as simple_error:
            logger.warning(f"Simple fetcher failed for {ticker}: {simple_error}")
        
        # Fallback to actual API (with rate limiting issues)
        def fetch_with_yfinance():
            # Add random delay to avoid rate limiting
            time.sleep(self.request_delay + random.uniform(0, 1))
            
            # Use yf.download which is more reliable than Ticker.history
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                threads=False
            )
            
            if df.empty:
                # Try with period parameter as fallback
                logger.warning(f"No data found for {ticker} with date range, trying with period")
                stock = yf.Ticker(ticker)
                df = stock.history(period="1y")
                
                # Filter to requested date range
                if not df.empty:
                    df = df[(df.index >= start_date) & (df.index <= end_date)]
                
            if df.empty:
                raise DataFetchError(f"No data found for ticker: {ticker}", source="yfinance", ticker=ticker)
            
            # Standardize column names (yfinance already uses standard names)
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in df.columns:
                    logger.warning(f"Column {col} not found for {ticker}")
            
            logger.info(f"Fetched {len(df)} days of real data for {ticker}")
            return df
        
        try:
            # Use retry mixin for API calls
            return self.with_retry(fetch_with_yfinance, max_retries=3)
            
        except Exception as e:
            logger.error(f"Error fetching US stock data for {ticker}: {e}")
            
            # Final fallback to alternative mock data
            logger.warning(f"Using fallback mock data for {ticker}")
            df = self.alternative_fetcher.create_mock_price_history(ticker, days=365)
            
            # Filter to requested date range
            if not df.empty:
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                return df
            
            raise DataFetchError(f"Failed to fetch data for {ticker}", source="all", ticker=ticker)
    
    @smart_cache(ttl=1800)  # 30 minutes cache for company info
    def fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch company information for US stocks with intelligent caching."""
        
        # For demo purposes, use simple fetcher first to avoid API limits
        try:
            company_data = self.simple_fetcher.fetch_stock_data(ticker, "미국장")
            if company_data and self._is_valid_company_data(company_data):
                logger.info(f"Successfully generated realistic company data for {ticker}")
                return company_data
        except Exception as simple_error:
            logger.warning(f"Simple fetcher failed for company info {ticker}: {simple_error}")
        
        # Fallback to actual API
        try:
            # Add delay to avoid rate limiting
            time.sleep(self.request_delay + random.uniform(0, 1))
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # If info is empty or has error, use price data as fallback
            if not info or len(info) < 5:
                logger.warning(f"Limited info available for {ticker}, using price data")
                # Get basic info from recent price history
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                try:
                    df = self.fetch_price_history(ticker, start_date, end_date)
                    
                    if not df.empty:
                        current_price = float(df["Close"].iloc[-1])
                        high_52w = float(df["High"].max())
                        low_52w = float(df["Low"].min())
                        volume = int(df["Volume"].iloc[-1]) if "Volume" in df else None
                        
                        company_info = {
                            "현재가": current_price,
                            "PER": "정보 없음",
                            "PBR": "정보 없음",
                            "ROE": "정보 없음",
                            "배당수익률": "정보 없음",
                            "시가총액": "정보 없음",
                            "52주 최고가": high_52w,
                            "52주 최저가": low_52w,
                            "베타": "정보 없음",
                            "거래량": volume,
                            "EPS": "정보 없음",
                            "Revenue": "정보 없음",
                            "Profit Margin": "정보 없음",
                            "회사명": ticker,
                            "섹터": "정보 없음",
                            "산업": "정보 없음",
                            "국가": "US",
                            "직원수": "정보 없음",
                        }
                    else:
                        company_info = self._get_default_company_info(ticker)
                except Exception as e:
                    logger.error(f"Failed to get price data for {ticker}: {e}")
                    company_info = self._get_default_company_info(ticker)
            else:
                # Get price history for 52-week high/low
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                try:
                    price_df = self.fetch_price_history(ticker, start_date, end_date)
                    current_price = price_df["Close"].iloc[-1] if not price_df.empty else info.get("currentPrice", info.get("regularMarketPrice"))
                    high_52w = price_df["High"].max() if not price_df.empty else info.get("fiftyTwoWeekHigh")
                    low_52w = price_df["Low"].min() if not price_df.empty else info.get("fiftyTwoWeekLow")
                    volume = price_df["Volume"].iloc[-1] if not price_df.empty and "Volume" in price_df.columns else info.get("volume", info.get("regularMarketVolume"))
                except Exception:
                    current_price = info.get("currentPrice", info.get("regularMarketPrice"))
                    high_52w = info.get("fiftyTwoWeekHigh")
                    low_52w = info.get("fiftyTwoWeekLow")
                    volume = info.get("volume", info.get("regularMarketVolume"))
                
                company_info = {
                    "현재가": current_price,
                    "PER": info.get("trailingPE"),
                    "PBR": info.get("priceToBook"),
                    "ROE": info.get("returnOnEquity"),
                    "배당수익률": info.get("dividendYield"),
                    "시가총액": info.get("marketCap"),
                    "52주 최고가": high_52w,
                    "52주 최저가": low_52w,
                    "베타": info.get("beta"),
                    "거래량": volume,
                    "EPS": info.get("trailingEps"),
                    "Revenue": info.get("totalRevenue"),
                    "Profit Margin": info.get("profitMargins"),
                    "회사명": info.get("shortName", info.get("longName", ticker)),
                    "섹터": info.get("sector"),
                    "산업": info.get("industry"),
                    "국가": info.get("country", "US"),
                    "직원수": info.get("fullTimeEmployees"),
                }
            
            # Clean up None values
            company_info = {k: v if v is not None and not pd.isna(v) else "정보 없음" 
                           for k, v in company_info.items()}
            
            return company_info
            
        except Exception as e:
            logger.error(f"Error fetching US company info for {ticker}: {e}")
            
            # Try reliable data sources
            logger.info(f"Trying reliable data sources for {ticker} company info")
            
            try:
                reliable_data = self.reliable_fetcher.fetch_stock_data(ticker, "미국장")
                if reliable_data and self._is_valid_company_data(reliable_data):
                    logger.info(f"Successfully fetched company info from reliable source for {ticker}")
                    return reliable_data
            except Exception as reliable_error:
                logger.error(f"Reliable fetcher also failed for company info {ticker}: {reliable_error}")
            
            # Try Alpha Vantage if API key is available
            if self.alpha_vantage_key:
                try:
                    av_data = self.alternative_fetcher.fetch_from_alphavantage(ticker, self.alpha_vantage_key)
                    if av_data:
                        logger.info(f"Successfully fetched data from Alpha Vantage for {ticker}")
                        # Merge with default data
                        company_info = self._get_default_company_info(ticker)
                        company_info.update({k: v for k, v in av_data.items() if v is not None})
                        return company_info
                except Exception as av_error:
                    logger.error(f"Alpha Vantage fetch failed for {ticker}: {av_error}")
            
            # Final fallback to mock data
            logger.warning(f"All sources failed, using mock data for {ticker}")
            mock_data = self.alternative_fetcher.create_mock_data(ticker)
            
            return mock_data
    
    def _is_valid_company_data(self, data: Dict[str, Any]) -> bool:
        """Validate company data quality."""
        if not data:
            return False
        
        # Check for essential fields
        essential_fields = ['ticker', 'currentPrice']
        for field in essential_fields:
            if field not in data or data[field] is None:
                return False
        
        # Check for reasonable price
        price = data.get('currentPrice')
        if isinstance(price, (int, float)) and (price <= 0 or price > 50000):
            return False
        
        return True
    
    def _get_default_company_info(self, ticker: str) -> Dict[str, Any]:
        """Return default company info when data is unavailable."""
        return {
            "현재가": "정보 없음",
            "PER": "정보 없음",
            "PBR": "정보 없음",
            "ROE": "정보 없음",
            "배당수익률": "정보 없음",
            "시가총액": "정보 없음",
            "52주 최고가": "정보 없음",
            "52주 최저가": "정보 없음",
            "베타": "정보 없음",
            "거래량": "정보 없음",
            "EPS": "정보 없음",
            "Revenue": "정보 없음",
            "Profit Margin": "정보 없음",
            "회사명": ticker,
            "섹터": "정보 없음",
            "산업": "정보 없음",
            "국가": "US",
            "직원수": "정보 없음",
        }
    
    @smart_cache(ttl=3600)  # 1 hour cache for financial data
    def fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch financial data for US stocks with intelligent caching."""
        try:
            # Add delay to avoid rate limiting
            time.sleep(self.request_delay + random.uniform(0, 1))
            
            stock = yf.Ticker(ticker)
            
            # Get financial statements
            financials = {}
            
            try:
                # Income statement
                if hasattr(stock, 'financials') and stock.financials is not None and not stock.financials.empty:
                    financials["income_statement"] = stock.financials.to_dict()
                
                # Balance sheet
                if hasattr(stock, 'balance_sheet') and stock.balance_sheet is not None and not stock.balance_sheet.empty:
                    financials["balance_sheet"] = stock.balance_sheet.to_dict()
                
                # Cash flow
                if hasattr(stock, 'cashflow') and stock.cashflow is not None and not stock.cashflow.empty:
                    financials["cash_flow"] = stock.cashflow.to_dict()
            except Exception as e:
                logger.warning(f"Could not fetch financial statements for {ticker}: {e}")
            
            # Key metrics from info
            try:
                info = stock.info
                key_metrics = {
                    "Revenue Growth": info.get("revenueGrowth"),
                    "Earnings Growth": info.get("earningsGrowth"),
                    "Gross Margins": info.get("grossMargins"),
                    "Operating Margins": info.get("operatingMargins"),
                    "Profit Margins": info.get("profitMargins"),
                    "Return on Assets": info.get("returnOnAssets"),
                    "Return on Equity": info.get("returnOnEquity"),
                    "Debt to Equity": info.get("debtToEquity"),
                    "Current Ratio": info.get("currentRatio"),
                    "Quick Ratio": info.get("quickRatio"),
                    "Free Cash Flow": info.get("freeCashflow"),
                    "Operating Cash Flow": info.get("operatingCashflow"),
                }
                
                financials["key_metrics"] = key_metrics
            except Exception as e:
                logger.warning(f"Could not fetch key metrics for {ticker}: {e}")
                financials["key_metrics"] = {}
            
            # Note: Caching is handled by @smart_cache decorator
            
            return financials
            
        except Exception as e:
            logger.error(f"Error fetching US financial data for {ticker}: {e}")
            return {}
    
    def get_analyst_recommendations(self, ticker: str) -> Dict[str, Any]:
        """
        Get analyst recommendations for US stocks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with analyst recommendations
        """
        cache_key = f"us_recommendations_{ticker}_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(self.request_delay + random.uniform(0, 1))
            
            stock = yf.Ticker(ticker)
            
            # Get recommendations
            recommendations = {}
            
            if hasattr(stock, 'recommendations') and stock.recommendations is not None:
                recommendations["recommendations"] = stock.recommendations.to_dict()
            
            # Get price targets
            info = stock.info
            recommendations["price_targets"] = {
                "Target Mean Price": info.get("targetMeanPrice"),
                "Target High Price": info.get("targetHighPrice"),
                "Target Low Price": info.get("targetLowPrice"),
                "Number of Analyst Opinions": info.get("numberOfAnalystOpinions"),
                "Recommendation Key": info.get("recommendationKey"),
                "Recommendation Mean": info.get("recommendationMean"),
            }
            
            # Note: Caching is handled by @smart_cache decorator
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching analyst recommendations for {ticker}: {e}")
            return {}
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """
        Get sector performance data for US market.
        
        Returns:
            Dictionary with sector performance data
        """
        cache_key = f"us_sector_performance_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            # Sector ETFs for performance tracking
            sector_etfs = {
                "Technology": "XLK",
                "Healthcare": "XLV",
                "Financial": "XLF",
                "Consumer Discretionary": "XLY",
                "Communication Services": "XLC",
                "Industrials": "XLI",
                "Consumer Staples": "XLP",
                "Energy": "XLE",
                "Utilities": "XLU",
                "Real Estate": "XLRE",
                "Materials": "XLB"
            }
            
            sector_performance = {}
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # 1 month performance
            
            for sector, etf in sector_etfs.items():
                try:
                    df = self.fetch_price_history(etf, start_date, end_date)
                    if not df.empty:
                        start_price = df["Close"].iloc[0]
                        end_price = df["Close"].iloc[-1]
                        performance = ((end_price - start_price) / start_price) * 100
                        
                        sector_performance[sector] = {
                            "performance": f"{performance:.2f}%",
                            "trend": "상승" if performance > 0 else "하락" if performance < 0 else "보합"
                        }
                except Exception as e:
                    logger.error(f"Error fetching performance for {sector}: {e}")
                    sector_performance[sector] = {
                        "performance": "N/A",
                        "trend": "N/A"
                    }
            
            # Note: Caching is handled by @smart_cache decorator
            
            return sector_performance
            
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return {}
    
    def search_ticker_by_name(self, company_name: str) -> Optional[str]:
        """
        Search for ticker by company name (placeholder implementation).
        
        Args:
            company_name: Company name to search
            
        Returns:
            Ticker symbol or None if not found
        """
        # This is a basic implementation
        # In a production system, you'd use a proper search API
        try:
            # Try direct lookup first (for well-known companies)
            test_ticker = company_name.upper()
            stock = yf.Ticker(test_ticker)
            info = stock.info
            
            if info and "shortName" in info:
                return test_ticker
            
            logger.warning(f"No ticker found for company: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching ticker for {company_name}: {e}")
            return None