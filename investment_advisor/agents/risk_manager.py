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
import yfinance as yf
import FinanceDataReader as fdr

from .base import InvestmentAgent
from ..data import KoreaStockDataFetcher, USStockDataFetcher

logger = logging.getLogger(__name__)


class RiskManagerAgent(InvestmentAgent):
    """Agent responsible for risk assessment and management."""
    
    name: str = Field(default="리스크관리자")
    description: str = "잠재적 리스크를 평가하고 리스크 관리 전략을 제안합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "risk_data", "market"],
        template="""
        {company}의 다음 리스크 데이터를 바탕으로 종합적인 리스크 분석을 수행해주세요:
        
        리스크 데이터: {risk_data}
        시장: {market}
        
        1. 시장 리스크:
           - 베타 값을 해석하고 시장 대비 변동성을 평가해주세요.
           - 시장 하락 시 예상되는 영향을 분석해주세요.
        
        2. 가격 리스크:
           - 52주 최고/최저가 대비 현재 위치의 리스크를 평가해주세요.
           - 가격 변동성과 그에 따른 리스크를 분석해주세요.
        
        3. 유동성 리스크:
           - 거래량 데이터를 바탕으로 유동성 리스크를 평가해주세요.
           - 대량 매도 시 예상되는 가격 영향을 분석해주세요.
        
        4. 기업 고유 리스크:
           - 해당 기업의 특수한 리스크 요인을 식별해주세요.
           - 산업 특성에 따른 리스크를 고려해주세요.
        
        5. 외부 환경 리스크:
           - 규제 변화, 정치적 리스크 등을 평가해주세요.
           - 글로벌 이벤트가 미칠 수 있는 영향을 분석해주세요.
        
        6. 리스크 관리 전략:
           - 포지션 사이즈 조절 방안을 제시해주세요.
           - 헤징 전략이나 분산 투자 방안을 제안해주세요.
           - 손절매 전략과 리스크 한도를 설정해주세요.
        
        7. 리스크 등급 평가:
           - 종합적인 리스크 등급(낮음/중간/높음/매우높음)을 부여하고 근거를 설명해주세요.
           - 리스크 대비 수익 잠재력을 평가해주세요.
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute risk analysis."""
        risk_data = self.get_risk_metrics(company, market)
        
        analysis = self.llm.invoke(
            self.prompt.format(
                company=company,
                risk_data=str(risk_data),
                market=market
            )
        ).content
        
        return f"## 리스크관리자의 의견\n\n{analysis}"
    
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
        """Calculate risk metrics for US stocks."""
        try:
            ticker = yf.Ticker(company)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return self._get_default_risk_metrics()
            
            # Calculate additional risk metrics
            volatility = hist["Close"].pct_change().std() * (252 ** 0.5)
            max_drawdown = self._calculate_max_drawdown(hist["Close"])
            
            # Volume metrics
            avg_volume = hist["Volume"].mean() if "Volume" in hist.columns else 0
            volume_volatility = hist["Volume"].std() / avg_volume if avg_volume > 0 else "N/A"
            
            return {
                "Beta": info.get("beta", "N/A"),
                "52주 최고가": info.get("fiftyTwoWeekHigh", hist["High"].max()),
                "52주 최저가": info.get("fiftyTwoWeekLow", hist["Low"].min()),
                "현재가": hist["Close"].iloc[-1],
                "연간 변동성": f"{volatility:.2%}",
                "최대 낙폭": f"{max_drawdown:.2%}",
                "평균 거래량": avg_volume,
                "거래량 변동성": volume_volatility,
                "VaR (95%)": self._calculate_var(hist["Close"], 0.95),
                "부채비율": info.get("debtToEquity", "N/A"),
                "유동비율": info.get("currentRatio", "N/A"),
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