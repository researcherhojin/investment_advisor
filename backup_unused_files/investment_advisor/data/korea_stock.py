"""
Korea Stock Data Fetcher

Handles fetching data for Korean stocks using FinanceDataReader and pykrx.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import pandas as pd
import FinanceDataReader as fdr
from pykrx import stock
import requests
from bs4 import BeautifulSoup

from .base import StockDataFetcher
from ..core.mixins import RetryMixin
from ..core.exceptions import DataFetchError

logger = logging.getLogger(__name__)


class KoreaStockDataFetcher(StockDataFetcher, RetryMixin):
    """Data fetcher for Korean stock market."""
    
    def __init__(self, use_cache: bool = True):
        super().__init__(use_cache)
        self.market_code_map = {
            "KOSPI": "KS11",
            "KOSDAQ": "KQ11"
        }
    
    def fetch_price_history(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch historical price data for Korean stocks."""
        cache_key = f"kr_history_{ticker}_{start_date.date()}_{end_date.date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return pd.DataFrame(cached_data)
        
        try:
            df = fdr.DataReader(ticker, start_date, end_date)
            
            if df.empty:
                raise ValueError(f"No data found for ticker: {ticker}")
            
            # Standardize column names
            df = df.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            })
            
            # Cache the data
            if self.use_cache:
                self.cache.set(cache_key, df.to_dict())
            
            logger.info(f"Fetched {len(df)} days of data for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Korean stock data for {ticker}: {e}")
            raise
    
    def fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch company information for Korean stocks."""
        cache_key = f"kr_info_{ticker}_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            # Get current date
            today = datetime.now().strftime("%Y%m%d")
            
            # Get fundamental data
            fundamental_data = stock.get_market_fundamental_by_ticker(today)
            
            info = {}
            if ticker in fundamental_data.index:
                stock_data = fundamental_data.loc[ticker]
                
                # Get price data for 52-week high/low
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                price_df = self.fetch_price_history(ticker, start_date, end_date)
                
                # Calculate beta
                beta = self._calculate_beta(ticker, start_date, end_date)
                
                info = {
                    "현재가": price_df["Close"].iloc[-1] if not price_df.empty else None,
                    "PER": stock_data.get("PER", None),
                    "PBR": stock_data.get("PBR", None),
                    "ROE": stock_data.get("ROE", None),
                    "배당수익률": stock_data.get("DIV", None),
                    "시가총액": stock_data.get("MARCAP", None),
                    "52주 최고가": price_df["High"].max() if not price_df.empty else None,
                    "52주 최저가": price_df["Low"].min() if not price_df.empty else None,
                    "베타": beta,
                    "거래량": price_df["Volume"].iloc[-1] if not price_df.empty and "Volume" in price_df.columns else None,
                }
            
            # Clean up None values
            info = {k: v if v is not None and not pd.isna(v) else "정보 없음" 
                   for k, v in info.items()}
            
            # Cache the data
            if self.use_cache:
                self.cache.set(cache_key, info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error fetching Korean company info for {ticker}: {e}")
            return {}
    
    def fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch financial data for Korean stocks."""
        cache_key = f"kr_financial_{ticker}_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            today = datetime.now().strftime("%Y%m%d")
            fundamental_data = stock.get_market_fundamental_by_ticker(today)
            
            if ticker in fundamental_data.index:
                financial_data = fundamental_data.loc[ticker].to_dict()
                
                # Cache the data
                if self.use_cache:
                    self.cache.set(cache_key, financial_data)
                
                return financial_data
            else:
                logger.warning(f"Financial data not found for ticker: {ticker}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching Korean financial data for {ticker}: {e}")
            return {}
    
    def _calculate_beta(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """Calculate beta for Korean stock against KOSPI."""
        try:
            # Get stock returns
            stock_df = fdr.DataReader(ticker, start_date, end_date)
            if stock_df.empty:
                return None
            
            # Get KOSPI returns
            kospi_df = fdr.DataReader("KS11", start_date, end_date)
            if kospi_df.empty:
                return None
            
            # Calculate returns
            stock_returns = stock_df["Close"].pct_change().dropna()
            kospi_returns = kospi_df["Close"].pct_change().dropna()
            
            # Align data
            combined_data = pd.concat([stock_returns, kospi_returns], axis=1)
            combined_data.columns = ["Stock", "Market"]
            combined_data.dropna(inplace=True)
            
            if len(combined_data) < 30:  # Need sufficient data points
                return None
            
            # Calculate beta
            covariance = combined_data.cov().iloc[0, 1]
            market_variance = combined_data["Market"].var()
            
            if market_variance == 0:
                return None
            
            beta = round(covariance / market_variance, 2)
            return beta
            
        except Exception as e:
            logger.error(f"Error calculating beta for {ticker}: {e}")
            return None
    
    def search_ticker_by_name(self, company_name: str) -> Optional[str]:
        """
        Search for ticker by company name using Naver Finance.
        
        Args:
            company_name: Company name to search
            
        Returns:
            Ticker symbol or None if not found
        """
        try:
            search_url = f"https://finance.naver.com/search/searchList.nhn?query={company_name}"
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            first_result = soup.select_one("td.tit > a")
            
            if first_result:
                href = first_result["href"]
                ticker = href.split("code=")[1].split("&")[0]
                logger.info(f"Found ticker {ticker} for company {company_name}")
                return ticker
            
            logger.warning(f"No ticker found for company: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching ticker for {company_name}: {e}")
            return None
    
    def get_market_trading_data(self, date: str = None) -> pd.DataFrame:
        """
        Get market trading data for Korean stocks.
        
        Args:
            date: Date in YYYYMMDD format, defaults to today
            
        Returns:
            DataFrame with trading data
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        try:
            return stock.get_market_trading_value_by_ticker(date)
        except Exception as e:
            logger.error(f"Error fetching market trading data: {e}")
            return pd.DataFrame()
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """
        Get sector performance data for Korean market.
        
        Returns:
            Dictionary with sector performance data
        """
        # This is a placeholder for future implementation
        # In a real system, this would fetch actual sector data
        return {
            "기술": {"performance": "3.5%", "trend": "상승"},
            "금융": {"performance": "-1.2%", "trend": "하락"},
            "제조": {"performance": "2.1%", "trend": "상승"},
            "건설": {"performance": "0.8%", "trend": "보합"},
        }