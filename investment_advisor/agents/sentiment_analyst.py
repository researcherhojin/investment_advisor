"""
Market Sentiment Analyst Agent

Analyzes market sentiment, investor psychology, and behavioral indicators.
"""

from typing import Any, Dict
import logging
from datetime import datetime, timedelta

import pandas as pd
from langchain.prompts import PromptTemplate
from pydantic import Field

from .base import InvestmentAgent
from ..data import StableFetcher
# Remove unused imports - modules were cleaned up

logger = logging.getLogger(__name__)


class MarketSentimentAgent(InvestmentAgent):
    """Agent specialized in market sentiment and investor psychology analysis."""
    
    name: str = "시장심리분석가"
    description: str = "시장 심리, 투자자 센티먼트, 거래량 패턴을 분석하는 전문가"
    
    # Data fetchers
    stable_fetcher: StableFetcher = Field(default_factory=StableFetcher)
    
    # Prompt template for sentiment analysis
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["ticker", "market", "sentiment_data"],
        template="""당신은 시장 심리와 투자자 행동을 분석하는 전문가입니다.

종목: {ticker}
시장: {market}

시장 심리 데이터:
{sentiment_data}

다음 관점에서 분석해주세요:

1. **투자자 심리 지표**
   - Fear & Greed Index (또는 유사 지표)
   - 거래량 패턴과 투자자 관심도
   - 매수/매도 압력 분석

2. **시장 포지셔닝**
   - 기관/외국인/개인 투자자 동향
   - 공매도 비율 및 변화
   - 옵션 시장 포지셔닝 (Put/Call ratio)

3. **모멘텀 및 센티먼트**
   - 가격 모멘텀과 심리적 저항선/지지선
   - 뉴스 센티먼트 점수
   - 소셜 미디어 언급량 및 감성

4. **행동재무학적 관점**
   - 과매수/과매도 신호
   - 군중심리 지표
   - 시장 사이클 위치

5. **투자 심리 기반 전망**
   - 단기 심리 전환 가능성
   - 센티먼트 기반 리스크
   - 투자자 행동 패턴 예측

투자 결정에 도움이 되는 구체적이고 실행 가능한 인사이트를 제공해주세요.
"""
    )
    
    def _run(self, ticker: str, market: str) -> str:
        """
        Run sentiment analysis for the given ticker.
        
        Args:
            ticker: Stock ticker symbol
            market: Market identifier (한국장/미국장)
            
        Returns:
            Sentiment analysis report
        """
        try:
            logger.info(f"Starting sentiment analysis for {ticker} in {market}")
            
            # Collect sentiment data
            sentiment_data = self._collect_sentiment_data(ticker, market)
            
            # Prepare context for analysis
            context = {
                "ticker": ticker,
                "market": market,
                "sentiment_data": self._format_sentiment_data(sentiment_data)
            }
            
            # Generate analysis using LLM
            analysis = self.llm.predict(self.prompt.format(**context))
            
            # Add metadata
            analysis += f"\n\n---\n📊 분석 시점: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            analysis += f"\n🎯 신뢰도: {self._calculate_confidence(sentiment_data)}"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            raise AnalysisError(f"시장 심리 분석 실패: {str(e)}")
    
    def _collect_sentiment_data(self, ticker: str, market: str) -> Dict[str, Any]:
        """Collect sentiment-related data."""
        sentiment_data = {}
        
        try:
            # Select appropriate fetcher
            fetcher = self.korea_fetcher if market == "한국장" else self.us_fetcher
            
            # Get price and volume data for sentiment analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # 3 months for sentiment
            
            price_history = fetcher.fetch_price_history(ticker, start_date, end_date)
            
            if not price_history.empty:
                # Calculate sentiment indicators
                sentiment_data['volume_analysis'] = self._analyze_volume_patterns(price_history)
                sentiment_data['price_momentum'] = self._analyze_price_momentum(price_history)
                sentiment_data['volatility_regime'] = self._analyze_volatility_regime(price_history)
                
                # Market-specific sentiment data
                if market == "한국장":
                    sentiment_data['investor_trends'] = self._get_korea_investor_trends(ticker, fetcher)
                else:
                    sentiment_data['market_breadth'] = self._get_us_market_breadth(fetcher)
                
                # Calculate Fear & Greed proxy
                sentiment_data['fear_greed_score'] = self._calculate_fear_greed_proxy(
                    price_history, sentiment_data
                )
                
        except Exception as e:
            logger.warning(f"Error collecting sentiment data: {e}")
            sentiment_data['error'] = str(e)
        
        return sentiment_data
    
    def _analyze_volume_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns for sentiment signals."""
        volume_data = {}
        
        try:
            # Volume trend
            volume_ma20 = df['Volume'].rolling(20).mean()
            volume_ma50 = df['Volume'].rolling(50).mean()
            
            current_volume = df['Volume'].iloc[-1]
            avg_volume_20 = volume_ma20.iloc[-1]
            avg_volume_50 = volume_ma50.iloc[-1]
            
            volume_data['current_vs_avg20'] = (current_volume / avg_volume_20 - 1) * 100
            volume_data['current_vs_avg50'] = (current_volume / avg_volume_50 - 1) * 100
            
            # Volume spike detection
            volume_zscore = (df['Volume'] - volume_ma20) / df['Volume'].rolling(20).std()
            volume_spikes = (volume_zscore > 2).sum()
            volume_data['volume_spikes_20d'] = int(volume_spikes.tail(20).sum())
            
            # On-Balance Volume trend
            obv = ((df['Close'] > df['Close'].shift(1)) * df['Volume']).cumsum()
            obv_slope = (obv.iloc[-1] - obv.iloc[-20]) / 20
            volume_data['obv_trend'] = 'positive' if obv_slope > 0 else 'negative'
            
            # Accumulation/Distribution
            money_flow_mult = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
            money_flow_volume = money_flow_mult * df['Volume']
            ad_line = money_flow_volume.cumsum()
            ad_slope = (ad_line.iloc[-1] - ad_line.iloc[-20]) / 20
            volume_data['accumulation_distribution'] = 'accumulation' if ad_slope > 0 else 'distribution'
            
        except Exception as e:
            logger.warning(f"Error in volume analysis: {e}")
            
        return volume_data
    
    def _analyze_price_momentum(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price momentum for sentiment."""
        momentum_data = {}
        
        try:
            close_prices = df['Close']
            
            # Short-term momentum (5-day)
            momentum_data['return_5d'] = ((close_prices.iloc[-1] / close_prices.iloc[-6]) - 1) * 100
            
            # Medium-term momentum (20-day)
            momentum_data['return_20d'] = ((close_prices.iloc[-1] / close_prices.iloc[-21]) - 1) * 100
            
            # Long-term momentum (60-day)
            momentum_data['return_60d'] = ((close_prices.iloc[-1] / close_prices.iloc[-61]) - 1) * 100
            
            # Momentum acceleration
            recent_momentum = momentum_data['return_5d']
            older_momentum = ((close_prices.iloc[-6] / close_prices.iloc[-11]) - 1) * 100
            momentum_data['momentum_acceleration'] = recent_momentum - older_momentum
            
            # Distance from highs/lows
            high_52w = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
            low_52w = df['Low'].tail(252).min() if len(df) >= 252 else df['Low'].min()
            current_price = close_prices.iloc[-1]
            
            momentum_data['pct_from_52w_high'] = ((current_price / high_52w) - 1) * 100
            momentum_data['pct_from_52w_low'] = ((current_price / low_52w) - 1) * 100
            
            # Trend strength (ADX would be better but keeping it simple)
            sma_20 = close_prices.rolling(20).mean()
            sma_50 = close_prices.rolling(50).mean()
            
            if sma_20.iloc[-1] > sma_50.iloc[-1] and current_price > sma_20.iloc[-1]:
                momentum_data['trend_strength'] = 'strong_uptrend'
            elif sma_20.iloc[-1] < sma_50.iloc[-1] and current_price < sma_20.iloc[-1]:
                momentum_data['trend_strength'] = 'strong_downtrend'
            else:
                momentum_data['trend_strength'] = 'weak_trend'
                
        except Exception as e:
            logger.warning(f"Error in momentum analysis: {e}")
            
        return momentum_data
    
    def _analyze_volatility_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volatility regime for sentiment."""
        volatility_data = {}
        
        try:
            # Calculate returns
            returns = df['Close'].pct_change().dropna()
            
            # Historical volatility (annualized)
            volatility_20d = returns.tail(20).std() * (252 ** 0.5) * 100
            volatility_60d = returns.tail(60).std() * (252 ** 0.5) * 100
            
            volatility_data['volatility_20d'] = volatility_20d
            volatility_data['volatility_60d'] = volatility_60d
            volatility_data['volatility_trend'] = 'increasing' if volatility_20d > volatility_60d else 'decreasing'
            
            # Volatility regime
            if volatility_20d < 15:
                volatility_data['regime'] = 'low_volatility'
            elif volatility_20d < 25:
                volatility_data['regime'] = 'normal_volatility'
            elif volatility_20d < 40:
                volatility_data['regime'] = 'high_volatility'
            else:
                volatility_data['regime'] = 'extreme_volatility'
                
            # Average True Range (ATR) as % of price
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift(1))
            low_close = abs(df['Low'] - df['Close'].shift(1))
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean()
            atr_pct = (atr / df['Close']) * 100
            volatility_data['atr_pct'] = atr_pct.iloc[-1]
            
        except Exception as e:
            logger.warning(f"Error in volatility analysis: {e}")
            
        return volatility_data
    
    def _get_korea_investor_trends(self, ticker: str, fetcher: StableFetcher) -> Dict[str, Any]:
        """Get Korean market investor trends."""
        investor_data = {}
        
        try:
            # This would typically fetch real investor trading data
            # For now, using mock data structure
            investor_data['foreign_net_buy'] = "데이터 준비중"
            investor_data['institutional_net_buy'] = "데이터 준비중"
            investor_data['retail_net_buy'] = "데이터 준비중"
            
        except Exception as e:
            logger.warning(f"Error getting investor trends: {e}")
            
        return investor_data
    
    def _get_us_market_breadth(self, fetcher: StableFetcher) -> Dict[str, Any]:
        """Get US market breadth indicators."""
        breadth_data = {}
        
        try:
            # This would typically fetch market breadth data
            # For now, using mock data structure
            breadth_data['advance_decline_ratio'] = "데이터 준비중"
            breadth_data['new_highs_lows'] = "데이터 준비중"
            breadth_data['percent_above_ma'] = "데이터 준비중"
            
        except Exception as e:
            logger.warning(f"Error getting market breadth: {e}")
            
        return breadth_data
    
    def _calculate_fear_greed_proxy(self, df: pd.DataFrame, sentiment_data: Dict[str, Any]) -> int:
        """Calculate a Fear & Greed proxy score (0-100)."""
        score = 50  # Neutral starting point
        
        try:
            # Price momentum component
            momentum = sentiment_data.get('price_momentum', {})
            if momentum.get('return_20d', 0) > 10:
                score += 15
            elif momentum.get('return_20d', 0) > 5:
                score += 10
            elif momentum.get('return_20d', 0) < -10:
                score -= 15
            elif momentum.get('return_20d', 0) < -5:
                score -= 10
                
            # Volatility component (inverse - high vol = fear)
            volatility = sentiment_data.get('volatility_regime', {})
            if volatility.get('regime') == 'low_volatility':
                score += 10
            elif volatility.get('regime') == 'high_volatility':
                score -= 10
            elif volatility.get('regime') == 'extreme_volatility':
                score -= 20
                
            # Volume component
            volume = sentiment_data.get('volume_analysis', {})
            if volume.get('obv_trend') == 'positive':
                score += 10
            else:
                score -= 10
                
            # Distance from highs component
            if momentum.get('pct_from_52w_high', -100) > -5:
                score += 15  # Near highs = greed
            elif momentum.get('pct_from_52w_low', 0) < 10:
                score -= 15  # Near lows = fear
                
        except Exception as e:
            logger.warning(f"Error calculating fear/greed score: {e}")
            
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _format_sentiment_data(self, data: Dict[str, Any]) -> str:
        """Format sentiment data for prompt."""
        formatted = []
        
        # Fear & Greed Score
        fear_greed = data.get('fear_greed_score', 50)
        sentiment = "공포" if fear_greed < 30 else "탐욕" if fear_greed > 70 else "중립"
        formatted.append(f"시장 심리 점수: {fear_greed}/100 ({sentiment})")
        formatted.append("")
        
        # Volume Analysis
        if 'volume_analysis' in data:
            formatted.append("거래량 분석:")
            vol = data['volume_analysis']
            formatted.append(f"- 20일 평균 대비: {vol.get('current_vs_avg20', 0):+.1f}%")
            formatted.append(f"- OBV 추세: {vol.get('obv_trend', 'N/A')}")
            formatted.append(f"- 자금 흐름: {vol.get('accumulation_distribution', 'N/A')}")
            formatted.append("")
        
        # Price Momentum
        if 'price_momentum' in data:
            formatted.append("가격 모멘텀:")
            mom = data['price_momentum']
            formatted.append(f"- 5일 수익률: {mom.get('return_5d', 0):+.1f}%")
            formatted.append(f"- 20일 수익률: {mom.get('return_20d', 0):+.1f}%")
            formatted.append(f"- 52주 최고가 대비: {mom.get('pct_from_52w_high', 0):+.1f}%")
            formatted.append(f"- 추세 강도: {mom.get('trend_strength', 'N/A')}")
            formatted.append("")
        
        # Volatility Regime
        if 'volatility_regime' in data:
            formatted.append("변동성 분석:")
            vol = data['volatility_regime']
            formatted.append(f"- 현재 변동성: {vol.get('volatility_20d', 0):.1f}%")
            formatted.append(f"- 변동성 추세: {vol.get('volatility_trend', 'N/A')}")
            formatted.append(f"- 변동성 regime: {vol.get('regime', 'N/A')}")
            formatted.append("")
        
        # Market-specific data
        if 'investor_trends' in data:
            formatted.append("투자자별 동향:")
            inv = data['investor_trends']
            for key, value in inv.items():
                formatted.append(f"- {key}: {value}")
            formatted.append("")
        
        if 'market_breadth' in data:
            formatted.append("시장 광도 지표:")
            breadth = data['market_breadth']
            for key, value in breadth.items():
                formatted.append(f"- {key}: {value}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> str:
        """Calculate confidence level based on data quality."""
        if 'error' in data:
            return "낮음"
        
        # Check data completeness
        complete_sections = sum([
            'volume_analysis' in data,
            'price_momentum' in data,
            'volatility_regime' in data,
            any(k in data for k in ['investor_trends', 'market_breadth'])
        ])
        
        if complete_sections >= 3:
            return "높음"
        elif complete_sections >= 2:
            return "보통"
        else:
            return "낮음"