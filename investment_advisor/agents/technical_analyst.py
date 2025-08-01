"""
Technical Analyst Agent

Performs technical analysis on stock price movements and patterns.
"""

import logging
from typing import Dict, Any
import numpy as np
import pandas as pd
from pydantic import Field
from langchain.prompts import PromptTemplate
import ta

from .base import InvestmentAgent

logger = logging.getLogger(__name__)


class TechnicalAnalystAgent(InvestmentAgent):
    """Agent responsible for technical analysis of stock prices."""
    
    name: str = Field(default="기술분석가")
    description: str = "주가 움직임과 패턴에 대한 기술적 분석을 수행합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "technical_data", "market"],
        template="""
        {company}의 다음 기술적 지표를 바탕으로 종합적인 기술적 분석을 수행해주세요:
        
        기술적 데이터: {technical_data}
        
        1. 현재 가격 분석:
           - 현재 가격 수준과 최근 추세를 평가해주세요.
           - 52주 최고/최저 대비 현재 위치를 분석해주세요.
        
        2. 추세 분석:
           - 단기(20일), 중기(50일), 장기(200일) 이동평균선과의 관계를 분석해주세요.
           - 현재 추세의 강도와 지속 가능성을 평가해주세요.
        
        3. 모멘텀 지표:
           - RSI 수준과 과매수/과매도 상태를 평가해주세요.
           - MACD 신호와 추세 전환 가능성을 분석해주세요.
        
        4. 지지선과 저항선:
           - 주요 지지선과 저항선을 식별해주세요.
           - 돌파 가능성과 그에 따른 시나리오를 제시해주세요.
        
        5. 거래량 분석:
           - 최근 거래량 패턴과 가격 움직임의 관계를 분석해주세요.
           - 거래량이 시사하는 바를 설명해주세요.
        
        6. 매매 전략:
           - 적정 매수 가격과 그 근거를 제시해주세요.
           - 목표 가격과 손절 가격을 설정하고 설명해주세요.
           - 단기/중기/장기 투자 전략을 구분하여 제안해주세요.
        
        7. 기술적 전망:
           - 향후 1-3개월간의 기술적 전망을 제시해주세요.
           - 주의해야 할 기술적 신호나 패턴을 설명해주세요.
        
        시장: {market}
        
        분석은 객관적이고 데이터에 기반해야 하며, 기술적 지표의 한계도 언급해주세요.
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute technical analysis."""
        technical_data = self.get_technical_indicators(company, market)
        technical_data = self._convert_numpy_types(technical_data)
        
        analysis = self.llm.invoke(
            self.prompt.format(
                company=company,
                technical_data=str(technical_data),
                market=market
            )
        ).content
        
        return f"## 기술분석가의 의견\n\n{analysis}"
    
    def get_technical_indicators(
        self, company: str, market: str
    ) -> Dict[str, Any]:
        """
        Calculate technical indicators for the stock.
        
        Args:
            company: Stock ticker
            market: Market identifier
            
        Returns:
            Dictionary with technical indicators
        """
        try:
            # Get stock data
            hist = self.get_stock_data(company, market)
            
            # Calculate moving averages
            hist["SMA_20"] = ta.trend.sma_indicator(hist["Close"], window=20)
            hist["SMA_50"] = ta.trend.sma_indicator(hist["Close"], window=50)
            hist["SMA_200"] = ta.trend.sma_indicator(hist["Close"], window=200)
            
            # Calculate RSI
            hist["RSI"] = ta.momentum.rsi(hist["Close"], window=14)
            
            # Calculate MACD
            macd = ta.trend.MACD(hist["Close"])
            hist["MACD"] = macd.macd()
            hist["MACD_Signal"] = macd.macd_signal()
            hist["MACD_Diff"] = macd.macd_diff()
            
            # Calculate Bollinger Bands
            bollinger = ta.volatility.BollingerBands(hist["Close"])
            hist["BB_Upper"] = bollinger.bollinger_hband()
            hist["BB_Lower"] = bollinger.bollinger_lband()
            hist["BB_Middle"] = bollinger.bollinger_mavg()
            
            # Get latest values
            current_price = hist["Close"].iloc[-1]
            
            # Calculate support and resistance levels
            support_level = hist["Low"].tail(30).min()
            resistance_level = hist["High"].tail(30).max()
            
            # Calculate price suggestions with volatility consideration
            volatility = hist["Close"].pct_change().std() * np.sqrt(252)
            
            # Dynamic price targets based on volatility
            if volatility < 0.2:  # Low volatility
                buy_discount = 0.03
                profit_target = 0.05
                stop_loss = 0.03
            elif volatility < 0.4:  # Medium volatility
                buy_discount = 0.05
                profit_target = 0.10
                stop_loss = 0.05
            else:  # High volatility
                buy_discount = 0.08
                profit_target = 0.15
                stop_loss = 0.08
            
            buy_price = current_price * (1 - buy_discount)
            take_profit_price = current_price * (1 + profit_target)
            stop_loss_price = current_price * (1 - stop_loss)
            
            # Compile technical indicators
            technical_data = {
                "현재가": current_price,
                "추천 구매 가격": buy_price,
                "추천 익절 가격": take_profit_price,
                "추천 손절 가격": stop_loss_price,
                "SMA_20": hist["SMA_20"].iloc[-1],
                "SMA_50": hist["SMA_50"].iloc[-1],
                "SMA_200": hist["SMA_200"].iloc[-1],
                "RSI": hist["RSI"].iloc[-1],
                "MACD": hist["MACD"].iloc[-1],
                "MACD_Signal": hist["MACD_Signal"].iloc[-1],
                "거래량": hist["Volume"].iloc[-1] if "Volume" in hist.columns else "N/A",
                "20일 평균 거래량": (
                    hist["Volume"].rolling(window=20).mean().iloc[-1]
                    if "Volume" in hist.columns else "N/A"
                ),
                "지지선": support_level,
                "저항선": resistance_level,
                "변동성": volatility,
                "52주 최고가": hist["High"].tail(252).max(),
                "52주 최저가": hist["Low"].tail(252).min(),
                "볼린저 밴드 상단": hist["BB_Upper"].iloc[-1],
                "볼린저 밴드 하단": hist["BB_Lower"].iloc[-1],
            }
            
            return technical_data
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise
    
    def _convert_numpy_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert numpy types to Python native types."""
        converted_data = {}
        
        for key, value in data.items():
            if isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                converted_data[key] = int(value)
            elif isinstance(value, (np.float64, np.float32)):
                converted_data[key] = float(value)
            elif isinstance(value, np.bool_):
                converted_data[key] = bool(value)
            elif isinstance(value, np.ndarray):
                converted_data[key] = value.tolist()
            else:
                converted_data[key] = value
        
        return converted_data