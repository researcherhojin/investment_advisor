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
        당신은 CFA와 FRM 자격을 보유한 20년 경력의 전문 기술분석가입니다. {company} ({market})에 대한 정량적 기술분석을 수행해주세요:

        📊 **기술적 지표 현황**
        {technical_data}

        ## 📈 **1. 차트 패턴 및 추세 분석**
        
        **이동평균선 배열 분석:**
        - 현재가 vs MA20: {현재가} vs MA20 위치 판단 및 황금교차/데드크로스 여부
        - MA20/MA50/MA200 정배열/역배열 상태 및 추세 강도 측정
        - 52주 밴드 내 위치: 현재가가 52주 레인지의 상위/하위 몇 % 구간인지 명시
        
        **차트 패턴 식별:**
        - 지난 30거래일 패턴: 삼각수렴/채널/헤드앤숄더/더블탑바텀 등
        - 패턴 완성도 및 신뢰도 (0-100%)
        - **최종 추세 판단: 강력상승추세/상승추세/횡보/하락추세/강력하락추세**

        ## ⚡ **2. 모멘텀 지표 종합 분석**
        
        **RSI(14) 심층 분석:**
        - 현재 RSI 수치와 과매수/과매도 구간 판단
        - RSI 다이버전스 여부 (가격 vs RSI 방향성 불일치)
        - 50선 돌파/이탈 신호 및 강도

        **MACD 시그널 분석:**
        - MACD선과 시그널선 교차 시점 및 히스토그램 변화
        - 0선 상위/하위 위치와 모멘텀 방향성
        - **모멘텀 종합 평가: 매우강세/강세/중립/약세/매우약세**

        ## 🎯 **3. 지지/저항선 정밀 분석**
        
        **핵심 가격대 (구체적 수치 필수):**
        - **1차 지지선: $XX.XX** (최근 30일 저점 기준)
        - **2차 지지선: $XX.XX** (주요 이동평균선 또는 피보나치 레벨)
        - **1차 저항선: $XX.XX** (최근 30일 고점 기준)  
        - **2차 저항선: $XX.XX** (심리적 가격대 또는 기술적 저항)
        
        **돌파 시나리오:**
        - 저항선 돌파 시 목표가: $XX.XX (확률 XX%)
        - 지지선 이탈 시 하락목표: $XX.XX (확률 XX%)

        ## 📊 **4. 거래량 분석 & 자금 흐름**
        
        **거래량 패턴:**
        - 현재 거래량 vs 20일 평균: XXX% (증가/감소)
        - 가격 상승 시 거래량 확대/축소 패턴 분석
        - OBV(On Balance Volume) 추세와 가격 추세 일치성
        
        **투자심리 지표:**
        - **자금 유입/유출 상태: 강한유입/유입/중립/유출/강한유출**
        - 기관/개인 매매 동향 추정

        ## 🛡️ **5. 리스크 관리 전략 (구체적 수치)**
        
        **포지션 사이징:**
        - **권장 매수가: $XX.XX** (현재가 대비 -X% 할인가)
        - **1차 목표가: $XX.XX** (+X% 수익, R/R비 1:X)
        - **2차 목표가: $XX.XX** (+X% 수익, R/R비 1:X)
        - **손절매가: $XX.XX** (-X% 손실 제한)
        
        **변동성 고려사항:**
        - 일일 변동성: X% (과거 30일 기준)
        - 예상 변동 범위: $XX.XX ~ $XX.XX

        ## 🚀 **6. 트레이딩 실행 계획**
        
        **매매 신호:**
        - **현재 신호: 강력매수/매수/관망/매도/강력매도**
        - **신뢰도: XX%** (시장환경, 거래량, 패턴 종합 고려)
        
        **진입 전략:**
        - 최적 진입 타이밍: 즉시매수/리트레이스먼트 대기/패턴완성 대기
        - 분할매수 권장 구간: 1차 $XX.XX, 2차 $XX.XX, 3차 $XX.XX
        
        **모니터링 포인트:**
        1. **핵심 관찰 가격**: $XX.XX 돌파/이탈 여부
        2. **거래량 확인**: X백만주 이상 거래 시 추세 가속
        3. **기술적 확인**: RSI XX 돌파 또는 MACD 골든크로스

        ## ⚠️ **7. 위험 요인 및 제한사항**
        
        **시장 리스크:**
        - 현재 변동성 수준: 높음/보통/낮음 (VIX 또는 동등 지표 기준)
        - 섹터/시장 전체 추세와의 상관관계
        - 주요 경제지표 발표 일정에 따른 영향

        **기술적 분석 한계:**
        - **신뢰도 평가: 높음(85%+)/보통(70-84%)/낮음(70% 미만)**
        - 예상치 못한 뉴스/이벤트에 따른 기술적 패턴 무효화 가능성
        - 저유동성 구간에서의 기술적 신호 왜곡 위험

        ---
        💡 **투자 원칙 리마인더:**
        - 모든 가격은 소수점 둘째 자리까지 정확히 표기
        - 확률과 비율은 구체적 수치(%)로 제시
        - 주관적 표현 지양, 정량적 근거 기반 분석
        - 리스크 관리가 수익 추구보다 우선
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute technical analysis."""
        try:
            technical_data = self.get_technical_indicators(company, market)
            technical_data = self._convert_numpy_types(technical_data)
            
            # Store visualization data for later use
            price_history = self.get_stock_data(company, market)
            
            # Store in session state for visualization
            try:
                import streamlit as st
                st.session_state.last_technical_analysis = {
                    'indicators': technical_data,
                    'price_history': price_history,
                    'ticker': company
                }
            except Exception as e:
                logger.debug(f"Could not store technical data in session state: {e}")
            
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
            hist["EMA_12"] = ta.trend.ema_indicator(hist["Close"], window=12)
            hist["EMA_26"] = ta.trend.ema_indicator(hist["Close"], window=26)
            
            # Calculate RSI
            hist["RSI"] = ta.momentum.rsi(hist["Close"], window=14)
            
            # Calculate MACD
            hist["MACD"] = ta.trend.macd(hist["Close"])
            hist["MACD_Signal"] = ta.trend.macd_signal(hist["Close"])
            hist["MACD_Diff"] = ta.trend.macd_diff(hist["Close"])
            
            # Calculate Bollinger Bands
            hist["BB_Upper"] = ta.volatility.bollinger_hband(hist["Close"])
            hist["BB_Lower"] = ta.volatility.bollinger_lband(hist["Close"])
            hist["BB_Middle"] = ta.volatility.bollinger_mavg(hist["Close"])
            
            # Calculate additional professional indicators
            hist["Stoch_K"] = ta.momentum.stoch(hist["High"], hist["Low"], hist["Close"])
            hist["Stoch_D"] = ta.momentum.stoch_signal(hist["High"], hist["Low"], hist["Close"])
            hist["Williams_R"] = ta.momentum.williams_r(hist["High"], hist["Low"], hist["Close"])
            hist["ADX"] = ta.trend.adx(hist["High"], hist["Low"], hist["Close"])
            
            # On Balance Volume
            if "Volume" in hist.columns:
                hist["OBV"] = ta.volume.on_balance_volume(hist["Close"], hist["Volume"])
            
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
            
            # Calculate 52주 range position
            high_52w = hist["High"].tail(252).max()
            low_52w = hist["Low"].tail(252).min()
            range_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100 if high_52w != low_52w else 50
            
            # Calculate trend strength
            ma20_slope = (hist["SMA_20"].iloc[-1] - hist["SMA_20"].iloc[-10]) / hist["SMA_20"].iloc[-10] * 100
            
            # Compile technical indicators
            technical_data = {
                "현재가": current_price,
                "추천_매수가": buy_price,
                "1차_목표가": take_profit_price,
                "손절매가": stop_loss_price,
                "SMA_20": hist["SMA_20"].iloc[-1],
                "SMA_50": hist["SMA_50"].iloc[-1],
                "SMA_200": hist["SMA_200"].iloc[-1],
                "EMA_12": hist["EMA_12"].iloc[-1],
                "EMA_26": hist["EMA_26"].iloc[-1],
                "RSI": hist["RSI"].iloc[-1],
                "MACD": hist["MACD"].iloc[-1],
                "MACD_Signal": hist["MACD_Signal"].iloc[-1],
                "MACD_Histogram": hist["MACD_Diff"].iloc[-1],
                "Stochastic_K": hist["Stoch_K"].iloc[-1],
                "Stochastic_D": hist["Stoch_D"].iloc[-1],
                "Williams_R": hist["Williams_R"].iloc[-1],
                "ADX": hist["ADX"].iloc[-1],
                "볼린저_상단": hist["BB_Upper"].iloc[-1],
                "볼린저_하단": hist["BB_Lower"].iloc[-1],
                "볼린저_중간": hist["BB_Middle"].iloc[-1],
                "1차_지지선": support_level,
                "1차_저항선": resistance_level,
                "52주_최고가": high_52w,
                "52주_최저가": low_52w,
                "52주_레인지_위치": f"{range_position:.1f}%",
                "일일_변동성": f"{volatility*100:.2f}%",
                "MA20_기울기": f"{ma20_slope:.2f}%",
                "거래량": hist["Volume"].iloc[-1] if "Volume" in hist.columns else 0,
                "20일_평균거래량": (
                    hist["Volume"].rolling(window=20).mean().iloc[-1]
                    if "Volume" in hist.columns else 0
                ),
                "거래량_비율": (
                    (hist["Volume"].iloc[-1] / hist["Volume"].rolling(window=20).mean().iloc[-1] * 100)
                    if "Volume" in hist.columns and hist["Volume"].rolling(window=20).mean().iloc[-1] > 0 else 100
                ),
            }
            
            # Add OBV if available
            if "OBV" in hist.columns:
                technical_data["OBV"] = hist["OBV"].iloc[-1]
                technical_data["OBV_변화"] = ((hist["OBV"].iloc[-1] - hist["OBV"].iloc[-10]) / abs(hist["OBV"].iloc[-10]) * 100) if hist["OBV"].iloc[-10] != 0 else 0
            
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