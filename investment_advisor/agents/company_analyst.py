"""
Company Analyst Agent

Analyzes company financials, business strategy, and market position.
"""

from typing import Dict, Any, Tuple
import logging
from datetime import datetime

import pandas as pd
from pydantic import Field
from langchain.prompts import PromptTemplate
import yfinance as yf
from pykrx import stock

from .base import InvestmentAgent

logger = logging.getLogger(__name__)


class CompanyAnalystAgent(InvestmentAgent):
    """Agent responsible for analyzing company fundamentals."""
    
    name: str = Field(default="기업분석가")
    description: str = "기업의 재무, 경영 전략, 시장 포지션을 분석합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "financials", "key_stats", "market"],
        template="""
        {market} 시장의 {company}에 대한 다음 재무 데이터와 주요 통계를 바탕으로 종합적인 기업 분석을 수행해주세요:
        
        재무 데이터: {financials}
        주요 통계: {key_stats}
        
        1. 재무 상태 분석:
           - 수익성, 성장성, 안정성 측면에서 기업의 재무 상태를 평가해주세요.
           - 주요 재무 비율(예: ROE, 부채비율 등)의 의미를 설명하고 해석해주세요.

        2. 경영 전략 분석:
            - 기업의 주요 사업 부문과 각 부문의 성과를 분석해주세요.
            - 기업의 경쟁 우위와 시장 포지셔닝을 평가해주세요.

        3. 시장 환경 분석:
            - 기업이 속한 산업의 현재 상황과 향후 전망을 제시해주세요.
            - 주요 경쟁사와의 비교 분석을 수행해주세요.

        4. 투자 관점 분석:
            - PER, PBR 등 주요 투자 지표를 해석하고, 기업의 현재 주가 수준에 대한 의견을 제시해주세요.
            - 기업의 배당 정책과 주주 가치 창출 능력을 평가해주세요.

        5. 리스크 요인:
            - 기업이 직면한 주요 리스크 요인을 식별하고 설명해주세요.

        6. 향후 전망:
            - 기업의 성장 가능성과 향후 전망을 제시해주세요.

        7. 최종 투자 의견:
            - 위의 분석을 종합하여 최종적으로 투자 의견(강력 매수, 매수, 보유, 매도, 강력 매도)을 제시하고 그 이유를 상세히 설명해주세요.

        분석은 객관적이고 데이터에 기반한 것이어야 하며, 투자자가 정보에 입각한 결정을 내릴 수 있도록 충분한 근거를 제공해야 합니다.
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute company analysis."""
        financials, key_stats = self.get_financial_data(company, market)
        
        analysis = self.llm.invoke(
            self.prompt.format(
                company=company,
                financials=str(financials),
                key_stats=str(key_stats),
                market=market
            )
        ).content
        
        return f"## 기업분석가의 의견\n\n{analysis}"
    
    def get_financial_data(
        self, company: str, market: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Fetch financial data for the company.
        
        Args:
            company: Stock ticker
            market: Market identifier
            
        Returns:
            Tuple of (financials, key_stats)
        """
        if market == "한국장":
            return self._get_korea_financial_data(company)
        else:
            return self._get_us_financial_data(company)
    
    def _get_korea_financial_data(
        self, company: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get financial data for Korean stocks."""
        today = datetime.now().strftime("%Y%m%d")
        
        try:
            financials = stock.get_market_fundamental_by_ticker(today)
            logger.info(f"Fetched financial data: {financials}")
            
            if company in financials.index:
                company_financials = financials.loc[company].to_dict()
            else:
                logger.warning(f"Company {company} not found in financial data")
                company_financials = {}
            
            key_stats = {
                "PER": company_financials.get("PER", "N/A"),
                "PBR": company_financials.get("PBR", "N/A"),
                "ROE": company_financials.get("ROE", "N/A"),
                "DIV": company_financials.get("DIV", "N/A"),
            }
            
        except Exception as e:
            logger.error(f"재무 데이터 가져오기 실패: {str(e)}")
            company_financials = {}
            key_stats = {"PER": "N/A", "PBR": "N/A", "ROE": "N/A", "DIV": "N/A"}
        
        return company_financials, key_stats
    
    def _get_us_financial_data(
        self, company: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get financial data for US stocks."""
        try:
            ticker = yf.Ticker(company)
            
            # Get financial statements
            financials = {}
            if not ticker.financials.empty:
                financials = ticker.financials.to_dict()
            
            # Get key statistics
            info = ticker.info
            key_stats = {
                "PER": info.get("trailingPE", "N/A"),
                "PBR": info.get("priceToBook", "N/A"),
                "ROE": info.get("returnOnEquity", "N/A"),
                "Dividend Yield": info.get("dividendYield", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "Beta": info.get("beta", "N/A"),
            }
            
        except Exception as e:
            logger.error(f"Error fetching US financial data: {str(e)}")
            financials = {}
            key_stats = {
                "PER": "N/A",
                "PBR": "N/A", 
                "ROE": "N/A",
                "Dividend Yield": "N/A",
                "Market Cap": "N/A",
                "Beta": "N/A",
            }
        
        return financials, key_stats