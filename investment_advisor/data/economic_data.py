"""
Economic Data Fetcher

Handles fetching macroeconomic data from various sources.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

import requests
import pandas as pd

from .base import DataCache

logger = logging.getLogger(__name__)


class EconomicDataFetcher:
    """Fetcher for macroeconomic indicators."""
    
    def __init__(self, alpha_vantage_api_key: str = None, use_cache: bool = True):
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self.use_cache = use_cache
        self.cache = DataCache() if use_cache else None
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_economic_indicators(self, country: str = "USA") -> Dict[str, Any]:
        """
        Fetch comprehensive economic indicators for a country.
        
        Args:
            country: Country code (USA, KOR, etc.)
            
        Returns:
            Dictionary with economic indicators
        """
        cache_key = f"economic_indicators_{country}_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        if not self.alpha_vantage_api_key:
            logger.warning("Alpha Vantage API key not provided, using mock data")
            return self._get_mock_indicators(country)
        
        indicators = {}
        
        # Define indicator functions to fetch
        indicator_functions = [
            ("GDP", "REAL_GDP"),
            ("인플레이션", "INFLATION"),
            ("실업률", "UNEMPLOYMENT"),
            ("소매판매", "RETAIL_SALES"),
            ("산업생산", "INDUSTRIAL_PRODUCTION"),
            ("소비자신뢰지수", "CONSUMER_SENTIMENT"),
        ]
        
        # Add interest rate function (different for USA vs others)
        if country == "USA":
            indicator_functions.append(("금리", "FEDERAL_FUNDS_RATE"))
        else:
            indicator_functions.append(("금리", "INTEREST_RATE"))
        
        for indicator_name, function_name in indicator_functions:
            try:
                indicator_data = self._fetch_single_indicator(
                    function_name, country, indicator_name
                )
                indicators.update(indicator_data)
                
            except Exception as e:
                logger.error(f"Error fetching {indicator_name}: {e}")
                indicators[indicator_name] = "데이터 가져오기 실패"
        
        # Add derived indicators
        indicators.update(self._calculate_derived_indicators(indicators))
        
        # Cache the data
        if self.use_cache:
            self.cache.set(cache_key, indicators)
        
        return indicators
    
    def _fetch_single_indicator(
        self, 
        function_name: str, 
        country: str, 
        indicator_name: str
    ) -> Dict[str, Any]:
        """Fetch a single economic indicator."""
        params = {
            "function": function_name,
            "interval": "annual",
            "apikey": self.alpha_vantage_api_key
        }
        
        # Add country parameter for non-US data
        if country != "USA" and function_name != "FEDERAL_FUNDS_RATE":
            params["country"] = country
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                latest_value = float(data["data"][0]["value"])
                
                # Calculate year-over-year change if we have multiple data points
                yoy_change = None
                if len(data["data"]) > 1:
                    previous_value = float(data["data"][1]["value"])
                    if previous_value != 0:
                        yoy_change = ((latest_value - previous_value) / previous_value) * 100
                
                return {
                    indicator_name: f"{latest_value:.2f}%",
                    f"{indicator_name}_전년대비": f"{yoy_change:.2f}%" if yoy_change is not None else "N/A",
                    f"{indicator_name}_raw": latest_value
                }
            else:
                logger.warning(f"No data found for {indicator_name}")
                return {indicator_name: "데이터 없음"}
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching {indicator_name}: {e}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error for {indicator_name}: {e}")
            raise
    
    def _calculate_derived_indicators(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived economic indicators."""
        derived = {}
        
        try:
            # Economic sentiment score based on multiple indicators
            sentiment_score = 0
            sentiment_factors = 0
            
            # GDP growth (positive is good)
            if "GDP_raw" in indicators:
                gdp_growth = indicators["GDP_raw"]
                if gdp_growth > 3:
                    sentiment_score += 2
                elif gdp_growth > 1:
                    sentiment_score += 1
                elif gdp_growth < -1:
                    sentiment_score -= 2
                sentiment_factors += 1
            
            # Unemployment (lower is better)
            if "실업률_raw" in indicators:
                unemployment = indicators["실업률_raw"]
                if unemployment < 4:
                    sentiment_score += 2
                elif unemployment < 6:
                    sentiment_score += 1
                elif unemployment > 8:
                    sentiment_score -= 2
                sentiment_factors += 1
            
            # Inflation (moderate is good)
            if "인플레이션_raw" in indicators:
                inflation = indicators["인플레이션_raw"]
                if 1 < inflation < 3:
                    sentiment_score += 1
                elif inflation > 5:
                    sentiment_score -= 2
                sentiment_factors += 1
            
            if sentiment_factors > 0:
                avg_score = sentiment_score / sentiment_factors
                if avg_score > 1:
                    sentiment = "긍정적"
                elif avg_score > 0:
                    sentiment = "보통"
                elif avg_score > -1:
                    sentiment = "부정적"
                else:
                    sentiment = "매우 부정적"
                
                derived["경제상황_종합평가"] = sentiment
                derived["경제지표_점수"] = f"{avg_score:.1f}/2.0"
        
        except Exception as e:
            logger.error(f"Error calculating derived indicators: {e}")
        
        return derived
    
    def fetch_market_sentiment(self) -> Dict[str, Any]:
        """
        Fetch market sentiment indicators.
        
        Returns:
            Dictionary with sentiment indicators
        """
        cache_key = f"market_sentiment_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        sentiment_data = {}
        
        try:
            # VIX (Fear Index) - using Yahoo Finance as fallback
            import yfinance as yf
            
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            
            if not vix_data.empty:
                current_vix = vix_data["Close"].iloc[-1]
                
                if current_vix < 20:
                    vix_sentiment = "낙관적"
                elif current_vix < 30:
                    vix_sentiment = "보통"
                elif current_vix < 40:
                    vix_sentiment = "불안"
                else:
                    vix_sentiment = "공포"
                
                sentiment_data["VIX"] = f"{current_vix:.2f}"
                sentiment_data["VIX_해석"] = vix_sentiment
            
            # Dollar Index
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_data = dxy.history(period="5d")
            
            if not dxy_data.empty:
                sentiment_data["달러지수"] = f"{dxy_data['Close'].iloc[-1]:.2f}"
            
            # Gold as safe haven indicator
            gold = yf.Ticker("GC=F")
            gold_data = gold.history(period="5d")
            
            if not gold_data.empty:
                sentiment_data["금가격"] = f"${gold_data['Close'].iloc[-1]:.2f}"
                
        except Exception as e:
            logger.error(f"Error fetching market sentiment: {e}")
            sentiment_data["오류"] = "시장 심리 지표를 가져올 수 없습니다"
        
        # Cache the data
        if self.use_cache:
            self.cache.set(cache_key, sentiment_data)
        
        return sentiment_data
    
    def _get_mock_indicators(self, country: str) -> Dict[str, Any]:
        """Return mock economic indicators for testing."""
        if country == "KOR":
            return {
                "GDP": "2.5%",
                "GDP_전년대비": "0.3%",
                "인플레이션": "3.2%",
                "인플레이션_전년대비": "1.1%",
                "금리": "3.5%",
                "실업률": "2.8%",
                "실업률_전년대비": "-0.2%",
                "소매판매": "1.8%",
                "산업생산": "0.5%",
                "소비자신뢰지수": "102.3",
                "경제상황_종합평가": "보통",
            }
        else:  # USA
            return {
                "GDP": "2.8%",
                "GDP_전년대비": "0.5%",
                "인플레이션": "3.7%",
                "인플레이션_전년대비": "-0.8%",
                "금리": "5.5%",
                "실업률": "3.6%",
                "실업률_전년대비": "-0.3%",
                "소매판매": "2.2%",
                "산업생산": "1.1%",
                "소비자신뢰지수": "107.8",
                "경제상황_종합평가": "긍정적",
            }
    
    def get_currency_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get currency exchange rates.
        
        Args:
            base_currency: Base currency for rates
            
        Returns:
            Dictionary with currency rates
        """
        cache_key = f"currency_rates_{base_currency}_{datetime.now().date()}"
        
        # Check cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            # This is a placeholder - in production, use a proper FX API
            import yfinance as yf
            
            rates = {}
            currency_pairs = ["USDKRW=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X"]
            
            for pair in currency_pairs:
                try:
                    ticker = yf.Ticker(pair)
                    data = ticker.history(period="2d")
                    if not data.empty:
                        rates[pair] = data["Close"].iloc[-1]
                except Exception as e:
                    logger.error(f"Error fetching {pair}: {e}")
            
            # Cache the data
            if self.use_cache:
                self.cache.set(cache_key, rates)
            
            return rates
            
        except Exception as e:
            logger.error(f"Error fetching currency rates: {e}")
            return {}