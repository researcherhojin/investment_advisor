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
from ..data.simple_fetcher import SimpleStockFetcher
from ..core.exceptions import DataFetchError, AnalysisError

logger = logging.getLogger(__name__)


class CompanyAnalystAgent(InvestmentAgent):
    """Agent responsible for analyzing company fundamentals."""
    
    name: str = Field(default="기업분석가")
    description: str = "기업의 재무, 경영 전략, 시장 포지션을 분석합니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "financials", "key_stats", "market"],
        template="""
        당신은 20년 경력의 전문 기업분석가입니다. {market} 시장의 {company}에 대한 다음 재무 데이터를 바탕으로 심도 있는 기업 분석을 수행해주세요:
        
        재무 데이터: {financials}
        주요 통계: {key_stats}
        
        **1. 재무 건전성 종합 평가 (A-F 등급)**
           - 수익성 분석: ROE {key_stats}를 동종업계 평균(15-20%)과 비교하여 평가
           - 성장성 지표: 최근 3년간 매출 성장률 추정 및 지속가능성 분석
           - 안정성 검토: 부채비율, 유동비율 등을 통한 재무안정성 평가
           - **종합 재무등급을 A~F로 명확히 제시**

        **2. 밸류에이션 심층 분석**
           - PER {key_stats}: 동종업계 평균 대비 할인/프리미엄 정도 분석
           - PBR {key_stats}: 순자산 대비 주가의 적정성 평가  
           - **현재 주가가 과대평가/적정평가/저평가인지 명확한 결론**
           - 목표주가 산정 근거 제시 (DCF, PER 멀티플 등 활용)

        **3. 경쟁력 및 시장 포지션**
           - 해당 섹터({key_stats})에서의 경쟁우위 분석
           - 시장점유율, 브랜드파워, 기술력 등 정성적 요소 평가
           - 진입장벽과 대체재 위협 수준 분석

        **4. 성장 동력 및 리스크**
           - **3가지 핵심 성장동력** 구체적으로 제시
           - **3가지 주요 리스크 요인** 명확히 식별
           - 각 요인이 주가에 미칠 영향도를 상/중/하로 분류

        **5. 배당 및 주주환원 정책**
           - 배당수익률 {key_stats} 분석 및 지속가능성 평가
           - 자사주매입, 증배 등 주주환원 정책 평가

        **6. 투자 추천 의견 (필수)**
           - **최종 투자의견: 강력매수/매수/보유/매도/강력매도 중 하나**
           - **목표주가: 구체적 금액 제시**
           - **투자 시계: 단기(3개월)/중기(6-12개월)/장기(1-3년)**
           - **핵심 투자논리 3줄 요약**

        ⚠️ 모든 수치는 구체적으로 언급하고, 애매한 표현("양호함", "괜찮음" 등) 대신 명확한 판단을 제시하세요.
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute company analysis."""
        try:
            financials, key_stats = self.get_financial_data(company, market)
            
            analysis = self.llm.invoke(
                self.prompt.format(
                    company=company,
                    financials=str(financials),
                    key_stats=str(key_stats),
                    market=market
                )
            ).content
            
            # Determine confidence level based on data quality
            confidence = "높음" if financials and key_stats else "보통"
            
            # Validate analysis completeness
            if not self.validate_analysis_completeness(analysis):
                logger.warning(f"Analysis for {company} may be incomplete")
                confidence = "보통"
            
            return self.format_response(analysis, confidence)
            
        except (DataFetchError, AnalysisError):
            raise
        except Exception as e:
            logger.error(f"Error in company analysis for {company}: {str(e)}")
            raise AnalysisError(
                f"기업 분석 중 오류가 발생했습니다: {str(e)}",
                agent=self.name,
                stage="company_analysis"
            )
    
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
        """Get financial data for US stocks using SimpleStockFetcher."""
        try:
            # Use SimpleStockFetcher to avoid API issues
            stock_data = self.simple_fetcher.fetch_stock_data(company, "미국장")
            
            # Extract financial information
            financials = {
                "총수익": stock_data.get("Revenue", "N/A"),
                "EPS": stock_data.get("EPS", "N/A"),
                "현재가": stock_data.get("currentPrice", "N/A"),
                "52주최고": stock_data.get("52주 최고가", "N/A"),
                "52주최저": stock_data.get("52주 최저가", "N/A"),
                "거래량": stock_data.get("거래량", "N/A"),
            }
            
            # Key statistics for analysis
            key_stats = {
                "PER": stock_data.get("PER", "N/A"),
                "PBR": stock_data.get("PBR", "N/A"),
                "ROE": stock_data.get("ROE", "N/A"),
                "배당수익률": stock_data.get("배당수익률", "N/A"),
                "시가총액": stock_data.get("시가총액", "N/A"),
                "베타": stock_data.get("베타", "N/A"),
                "섹터": stock_data.get("섹터", "N/A"),
                "산업": stock_data.get("산업", "N/A"),
            }
            
            logger.info(f"Successfully generated financial data for {company} using SimpleStockFetcher")
            
        except Exception as e:
            logger.error(f"Error generating financial data for {company}: {str(e)}")
            financials = {
                "총수익": "N/A",
                "EPS": "N/A", 
                "현재가": "N/A",
                "52주최고": "N/A",
                "52주최저": "N/A",
                "거래량": "N/A",
            }
            key_stats = {
                "PER": "N/A",
                "PBR": "N/A", 
                "ROE": "N/A",
                "배당수익률": "N/A",
                "시가총액": "N/A",
                "베타": "N/A",
                "섹터": "N/A",
                "산업": "N/A",
            }
        
        return financials, key_stats