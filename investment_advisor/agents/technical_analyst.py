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
from ..data.simple_fetcher import SimpleStockFetcher

logger = logging.getLogger(__name__)


class TechnicalAnalystAgent(InvestmentAgent):
    """Agent responsible for technical analysis of stock prices."""
    
    name: str = Field(default="기술분석가")
    description: str = "주가 움직임과 패턴에 대한 기술적 분석을 수행합니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "technical_data", "market"],
        template="""
        당신은 15년 경력의 전문 기술분석가입니다. {company} ({market})의 차트 패턴과 기술지표를 종합 분석해주세요:
        
        기술적 데이터: {technical_data}
        
        **1. 차트 패턴 및 추세 분석**
           - 현재가 vs 이동평균: MA20({technical_data}), MA50, MA200 배열 상태 분석
           - 52주 레인지 내 위치: 현재 {technical_data} vs 최고가/최저가 상대적 위치 (%)
           - **추세 방향: 상승/하락/횡보 중 명확히 판단**
           - 추세 강도: 약함/보통/강함 (이동평균 기울기 기준)

        **2. 모멘텀 및 오실레이터 신호**
           - RSI({technical_data}): 과매수(70↑)/중립(30-70)/과매도(30↓) 구간 분석
           - MACD: 신호선 교차, 히스토그램 분석으로 모멘텀 변화 예측
           - **모멘텀 상태: 강세/약세/중립 중 하나로 결론**

        **3. 지지/저항 레벨 (구체적 가격 제시)**
           - **1차 지지선: ${technical_data} (근거: 최근 저점)**
           - **1차 저항선: ${technical_data} (근거: 최근 고점)**
           - **핵심 지지선: ${technical_data} (이탈 시 추가 하락 예상)**
           - 돌파 시나리오: 저항선 돌파 시 목표가격 및 확률

        **4. 거래량 분석 및 투자심리**
           - 최근 거래량({technical_data}) vs 20일 평균 비교
           - 가격 상승/하락 시 거래량 증감 패턴 분석
           - **거래량 신호: 매수세 강화/약화, 매도세 강화/약화**

        **5. 리스크 관리 전략**
           - **추천 매수가: ${technical_data} (현재가 대비 할인율 적용)**
           - **목표 수익가: ${technical_data} (기술적 저항선 기준)**
           - **손절가: ${technical_data} (주요 지지선 하회 시)**
           - 위험/수익 비율: 1:X 형태로 제시

        **6. 단기 트레이딩 신호 (1-4주)**
           - **매매신호: 강력매수/매수/관망/매도/강력매도**
           - 진입 타이밍: 즉시/리트레이스먼트 후/패턴 완성 후
           - **핵심 모니터링 포인트 3가지** 제시

        **7. 위험 요인 및 주의사항**
           - 현재 변동성 수준 평가 (일일 변동폭 {technical_data})
           - 시장 전체 상황이 종목에 미치는 영향
           - **기술적 분석 신뢰도: 높음/보통/낮음 (시장 환경 고려)**

        ⚠️ 모든 가격은 구체적 수치로, 확률은 %로 제시하고, 애매한 표현 금지
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute technical analysis."""
        try:
            technical_data = self.get_technical_indicators(company, market)
            technical_data = self._convert_numpy_types(technical_data)
            
            analysis = self.llm.invoke(
                self.prompt.format(
                    company=company,
                    technical_data=str(technical_data),
                    market=market
                )
            ).content
            
            # Determine confidence based on data quality
            confidence = "높음" if technical_data.get("현재가") else "보통"
            
            # Validate technical analysis completeness
            if not self.validate_analysis_completeness(analysis):
                logger.warning(f"Technical analysis for {company} may be incomplete")
                confidence = "보통"
            
            return self.format_response(analysis, confidence)
            
        except Exception as e:
            logger.error(f"Error in technical analysis for {company}: {str(e)}")
            return self.format_response(
                f"기술적 분석 중 오류가 발생했습니다: {str(e)}", 
                "낮음"
            )
    
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