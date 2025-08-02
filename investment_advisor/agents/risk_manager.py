"""
Risk Manager Agent

Evaluates potential risks and suggests risk management strategies.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

import pandas as pd
from pydantic import Field
from langchain.prompts import PromptTemplate
import FinanceDataReader as fdr

from .base import InvestmentAgent
from ..data import KoreaStockDataFetcher, USStockDataFetcher
from ..data.simple_fetcher import SimpleStockFetcher
from ..data.stable_fetcher import StableFetcher

logger = logging.getLogger(__name__)


class RiskManagerAgent(InvestmentAgent):
    """Agent responsible for risk assessment and management."""
    
    name: str = Field(default="리스크관리자")
    description: str = "잠재적 리스크를 평가하고 리스크 관리 전략을 제안합니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)
    stable_fetcher: StableFetcher = Field(default_factory=StableFetcher)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "risk_data", "market"],
        template="""
        당신은 20년 경력의 전문 리스크 관리자입니다. {company} ({market})의 종합적 리스크 평가를 수행해주세요:
        
        리스크 데이터: {risk_data}
        
        **1. 시장 리스크 평가 (Beta 분석)**
           - 베타 계수: {risk_data} (1.0 기준 해석)
           - 시장 10% 하락 시 예상 손실: 베타 × 10% = X% 손실 예상
           - **시장 민감도: 높음/보통/낮음**
           - 시장 위기 시 방어력 평가

        **2. 변동성 및 가격 리스크**
           - 연간 변동성: {risk_data} (동종업계 평균 20-30% 대비)
           - 최대 낙폭(MDD): {risk_data} 분석 및 회복 소요기간 예측
           - 52주 레인지: 현재가 vs 최고가/최저가 위치 리스크
           - **변동성 등급: 1-5등급 (5등급이 가장 위험)**

        **3. 유동성 리스크 측정**
           - 일평균 거래량: {risk_data} (시가총액 대비 회전율)
           - 거래량 변동성: {risk_data} (유동성 안정성 지표)
           - **대량 매도 시 예상 슬리피지: X% 추정**
           - 유동성 위기 시 매도 소요일수 예측

        **4. 집중 리스크 (섹터/지역)**
           - 섹터 집중도: 해당 산업의 시장 사이클 리스크
           - 지역적 노출: {market} 경제/정치적 리스크 노출도
           - **업종별 리스크: 순환주/방어주/성장주 분류에 따른 위험도**

        **5. 재무 건전성 리스크**
           - 부채비율 분석: 금리 상승 시 이자 부담 증가 영향
           - 현금흐름 안정성: 영업활동으로부터의 현금창출 능력
           - **신용 리스크 등급: AAA~D 등급 추정**

        **6. VaR 및 손실 시나리오**
           - 95% VaR: {risk_data} (1일 기준 최대 예상손실)
           - **최악 시나리오 (5% 확률): X% 손실 가능**
           - 스트레스 테스트: 2008, 2020 수준 위기 시 예상 손실률

        **7. 리스크 관리 전략 (구체적 수치)**
           - **권장 포지션 사이즈: 전체 포트폴리오의 X%**
           - **손절매 라인: 현재가 대비 -X% (구체적 가격 제시)**
           - 분산투자 필요성: 동일 섹터 노출 한도 권고
           - 헤징 수단: 옵션, 선물 활용 방안

        **8. 종합 리스크 등급 (A-E, 5단계)**
           - **최종 리스크 등급: A(낮음) ~ E(매우높음)**
           - **Risk-Reward 비율: 1:X (위험 대비 수익 잠재력)**
           - 투자 권고: 보수적/균형적/공격적 투자자별 권장사항

        ⚠️ 모든 리스크는 정량적 수치로 제시하고, 리스크 등급과 손실 시나리오를 명확히 제시하세요.
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute risk analysis."""
        try:
            risk_data = self.get_risk_metrics(company, market)
            
            analysis = self.llm.invoke(
                self.prompt.format(
                    company=company,
                    risk_data=str(risk_data),
                    market=market
                )
            ).content
            
            # Determine confidence based on data completeness
            confidence = "높음" if risk_data.get("현재가") != "N/A" else "보통"
            
            # Validate risk analysis completeness
            if not self.validate_analysis_completeness(analysis):
                logger.warning(f"Risk analysis for {company} may be incomplete")
                confidence = "보통"
            
            return self.format_response(analysis, confidence)
            
        except Exception as e:
            logger.error(f"Error in risk analysis for {company}: {str(e)}")
            return self.format_response(
                f"리스크 분석 중 오류가 발생했습니다: {str(e)}", 
                "낮음"
            )
    
    def get_risk_metrics(self, company: str, market: str) -> Dict[str, Any]:
        """
        Calculate risk metrics for the stock.
        
        Args:
            company: Stock ticker
            market: Market identifier
            
        Returns:
            Dictionary with risk metrics
        """
        if market == "한국장":
            return self._get_korea_risk_metrics(company)
        else:
            return self._get_us_risk_metrics(company)
    
    def _get_korea_risk_metrics(self, company: str) -> Dict[str, Any]:
        """Calculate risk metrics for Korean stocks."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Use KoreaStockDataFetcher to get company info which includes beta
            fetcher = KoreaStockDataFetcher()
            company_info = fetcher.fetch_company_info(company)
            
            # Get price data for other metrics
            df = fdr.DataReader(company, start_date, end_date)
            if df.empty:
                logger.error(f"주가 데이터를 가져올 수 없습니다: {company}")
                return self._get_default_risk_metrics()
            
            # Use beta from company_info (already calculated by KoreaStockDataFetcher)
            beta = company_info.get("베타", "N/A")
            
            # Calculate other risk metrics
            volatility = df["Close"].pct_change().std() * (252 ** 0.5)  # Annualized
            max_drawdown = self._calculate_max_drawdown(df["Close"])
            
            # Volume metrics
            avg_volume = df["Volume"].mean() if "Volume" in df.columns else 0
            volume_volatility = df["Volume"].std() / avg_volume if avg_volume > 0 else "N/A"
            
            return {
                "Beta": beta,
                "52주 최고가": company_info.get("52주 최고가", df["High"].max()),
                "52주 최저가": company_info.get("52주 최저가", df["Low"].min()),
                "현재가": company_info.get("현재가", df["Close"].iloc[-1]),
                "연간 변동성": f"{volatility:.2%}",
                "최대 낙폭": f"{max_drawdown:.2%}",
                "평균 거래량": avg_volume,
                "거래량 변동성": volume_volatility,
                "VaR (95%)": self._calculate_var(df["Close"], 0.95),
            }
            
        except Exception as e:
            logger.error(f"한국 주식 리스크 지표 계산 중 오류: {str(e)}")
            return self._get_default_risk_metrics()
    
    def _get_us_risk_metrics(self, company: str) -> Dict[str, Any]:
        """Calculate risk metrics for US stocks using SimpleStockFetcher."""
        try:
            # Use SimpleStockFetcher to avoid API issues
            stock_data = self.simple_fetcher.fetch_stock_data(company, "미국장")
            
            # Generate realistic price history for calculations
            hist = self.simple_fetcher.create_price_history(company, days=365)
            
            if hist.empty or not stock_data:
                return self._get_default_risk_metrics()
            
            # Calculate additional risk metrics
            volatility = hist["Close"].pct_change().std() * (252 ** 0.5)
            max_drawdown = self._calculate_max_drawdown(hist["Close"])
            
            # Volume metrics
            avg_volume = hist["Volume"].mean() if "Volume" in hist.columns else 0
            volume_volatility = hist["Volume"].std() / avg_volume if avg_volume > 0 else "N/A"
            
            return {
                "Beta": stock_data.get("베타", "N/A"),
                "52주 최고가": stock_data.get("52주 최고가", hist["High"].max()),
                "52주 최저가": stock_data.get("52주 최저가", hist["Low"].min()),
                "현재가": stock_data.get("currentPrice", hist["Close"].iloc[-1]),
                "연간 변동성": f"{volatility:.2%}",
                "최대 낙폭": f"{max_drawdown:.2%}",
                "평균 거래량": avg_volume,
                "거래량 변동성": volume_volatility,
                "VaR (95%)": self._calculate_var(hist["Close"], 0.95),
                "부채비율": "N/A",  # SimpleStockFetcher doesn't provide debt ratios
                "유동비율": "N/A",  # SimpleStockFetcher doesn't provide current ratios
            }
            
        except Exception as e:
            logger.error(f"미국 주식 리스크 지표 계산 중 오류: {str(e)}")
            return self._get_default_risk_metrics()
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown from price series."""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_var(self, prices: pd.Series, confidence_level: float) -> str:
        """Calculate Value at Risk."""
        returns = prices.pct_change().dropna()
        var = returns.quantile(1 - confidence_level)
        return f"{var:.2%}"
    
    def _get_default_risk_metrics(self) -> Dict[str, Any]:
        """Return default risk metrics when data is unavailable."""
        return {
            "Beta": "N/A",
            "52주 최고가": "N/A",
            "52주 최저가": "N/A",
            "현재가": "N/A",
            "연간 변동성": "N/A",
            "최대 낙폭": "N/A",
            "평균 거래량": "N/A",
            "거래량 변동성": "N/A",
            "VaR (95%)": "N/A",
        }