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

# Suppress pkg_resources deprecation warning from pykrx
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)
    from pykrx import stock

from .base import InvestmentAgent
from ..data.simple_fetcher import SimpleStockFetcher
from ..data.stable_fetcher import StableFetcher

logger = logging.getLogger(__name__)


class CompanyAnalystAgent(InvestmentAgent):
    """Agent responsible for analyzing company fundamentals."""

    name: str = Field(default="기업분석가")
    description: str = "기업의 재무, 경영 전략, 시장 포지션을 분석합니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)
    stable_fetcher: StableFetcher = Field(default_factory=StableFetcher)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "financials", "key_stats", "market"],
        template="""
        당신은 CPA와 CFA 자격을 보유한 25년 경력의 선임 기업분석가입니다. {market} 시장의 {company}에 대한 정량적 기업분석을 수행해주세요:

        📊 **재무데이터 및 통계**
        재무정보: {financials}
        핵심지표: {key_stats}

        ⚠️ **필수 분석 원칙**:
        1. 재무 데이터가 'N/A' 또는 부족한 경우, "데이터 부족으로 상세 분석 불가"를 명시
        2. 현재 주가를 기준으로 현실적인 목표주가 설정 (최대 ±30% 범위)
        3. PER > 50이면 과대평가, PER > 100이면 심각한 과대평가로 판단
        4. 실제 데이터가 없으면 가상의 숫자를 만들지 말고 분석 불가 명시

        ## 📈 **1. 재무 건전성 종합 진단**

        **수익성 지표 (Profitability Metrics)**
        - ROE(자기자본이익률): XX% vs 섹터평균 15-20% 비교분석
        - ROA(총자산이익률): XX% vs 업계벤치마크 분석
        - 영업이익률: XX% - 3년 트렌드 및 경쟁사 대비 우위성
        - 순이익률: XX% - 마진 개선/악화 요인 분석

        **성장성 지표 (Growth Metrics)**
        - 매출 CAGR(3년): XX% - 지속가능성 및 성장동력 평가
        - 순이익 CAGR(3년): XX% - 수익성 성장의 품질 분석
        - **성장성 등급: S/A/B/C/D 중 하나**

        **안정성 지표 (Stability Metrics)**
        - 부채비율: XX% (안전 임계점 200% 기준)
        - 유동비율: XX% (건전성 기준 150% 이상)
        - 이자보상배율: XX배 (안전 기준 5배 이상)
        - **재무안정성 등급: AAA/AA/A/BBB/BB/B/CCC**

        ## 💰 **2. 밸류에이션 정밀 분석**

        **상대가치 평가**
        - PER: XX배 vs 섹터 평균 XX배 (할인율 -XX% 또는 프리미엄 +XX%)
        - PBR: XX배 vs 섹터 평균 XX배 (순자산 대비 적정성)
        - EV/EBITDA: XX배 vs 글로벌 동종업계 XX배
        - PSR: XX배 - 매출 대비 기업가치 평가

        **절대가치 평가**
        - DCF 모델 기반 본질가치: $XX.XX (할인율 XX% 적용)
        - DDM 모델 목표가: $XX.XX (요구수익률 XX% 가정)
        - **현재 주가 평가: 과대평가/적정평가/저평가 (편차 -XX%~+XX%)**

        **목표주가 산정** (현재가 기준 현실적 범위)
        - **12개월 목표주가: 현재가 대비 -20% ~ +20% 범위** (근거 필수)
        - **Bull Case: 현재가 대비 최대 +30%** (낙관적 시나리오)
        - **Bear Case: 현재가 대비 최대 -30%** (비관적 시나리오)

        ## 🏆 **3. 경쟁우위 및 사업모델 분석**

        **Porter's 5 Forces 분석**
        - 업계 경쟁강도: 높음/보통/낮음 (근거 제시)
        - 신규진입 위협: 높음/보통/낮음 (진입장벽 분석)
        - 대체재 위협: 높음/보통/낮음 (기술변화 영향)
        - 공급업체 교섭력: 강함/보통/약함
        - 구매자 교섭력: 강함/보통/약함

        **지속경쟁우위 (Sustainable Competitive Advantage)**
        - **핵심 경쟁력 3가지**: 구체적 근거와 함께 제시
        - **경제적 해자(Economic Moat)**: 넓음/보통/좁음/없음
        - 시장점유율: XX% (업계 순위 X위)

        ## 🚀 **4. 성장전략 및 투자 포인트**

        **성장 동력 분석 (Growth Drivers)**
        1. **주력사업 확장**: 구체적 시장규모와 점유율 목표
        2. **신사업 진출**: 투자계획 및 예상 수익기여도
        3. **M&A 및 제휴**: 시너지 효과 및 통합 리스크

        **투자 테마 매칭**
        - ESG 투자 부합도: 높음/보통/낮음
        - 디지털 전환 수혜도: 높음/보통/낮음
        - **핵심 투자 테마**: 구체적 테마명 및 수혜 정도

        ## ⚠️ **5. 리스크 요인 및 시나리오 분석**

        **Critical Risk Factors**
        1. **운영 리스크**: 구체적 리스크와 임팩트 ($XX만 달러)
        2. **재무 리스크**: 유동성, 부채상환 등 ($XX만 달러)
        3. **시장 리스크**: 경기침체, 금리변화 등 (주가 -XX% 영향)

        **시나리오 분석** (현재가 기준 현실적 범위)
        - **기본 시나리오** (확률 60%): 현재가 대비 -10% ~ +10%
        - **상승 시나리오** (확률 25%): 현재가 대비 +10% ~ +30%
        - **하락 시나리오** (확률 15%): 현재가 대비 -10% ~ -30%

        ## 🎯 **6. 투자 결론 및 실행전략**

        **최종 투자의견** (현실적 기준)
        - **레이팅 결정 기준**:
          • PER < 30 & 성장성 양호: BUY
          • PER 30-50: HOLD
          • PER > 50: SELL/CAUTION (과대평가)
          • PER > 100: STRONG SELL (심각한 과대평가)
        - **목표주가: 현재가 대비 최대 ±20% 범위**
        - **투자시계: 중기(6-12M) 기준**
        - **신뢰도: 재무데이터 완전성에 따라 결정**

        **포트폴리오 배분 권고**
        - **권장 비중**: 포트폴리오의 X-X% (리스크 수준 고려)
        - **분할매수 전략**: 1차 XX%, 2차 XX%, 3차 XX%
        - **핵심 모니터링 지표**: 3가지 KPI 제시

        **Executive Summary (3줄 요약)**
        1. **밸류에이션**: 현재 PER XX배로 XX% 할인/프리미엄, 목표가 $XX.XX
        2. **성장성**: XX 부문 성장으로 향후 X년간 매출 XX% 성장 전망
        3. **투자논리**: XX 테마 수혜 + XX 경쟁우위로 아웃퍼폼 기대

        ---
        💡 **분석 기준점**
        - 모든 재무지표는 최근 4분기(TTM) 기준
        - 목표주가는 12개월 투자기간 기준
        - 밸류에이션은 Forward P/E 기준 (차기년도 예상 EPS 적용)
        - 리스크는 VaR 95% 신뢰구간 기준
        """
    )

    def _run(self, company: str, market: str, stock_data: Dict[str, Any] = None) -> str:
        """Execute company analysis."""
        try:
            # Use provided stock_data if available, otherwise fetch
            if stock_data:
                financials, key_stats = self._extract_financial_from_stock_data(stock_data)
            else:
                financials, key_stats = self.get_financial_data(company, market)

            # Check if PER is extremely high (Tesla case)
            try:
                per_value = float(key_stats.get('PER', 0)) if key_stats else 0
                if per_value > 100:
                    logger.warning(f"{company} has extremely high PER: {per_value} - Likely overvalued")
            except (TypeError, ValueError):
                per_value = 0  # Default if conversion fails

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

        except Exception as e:
            logger.error(f"Error in company analysis for {company}: {str(e)}")
            return f"기업 분석 중 오류가 발생했습니다: {str(e)}"

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
            # Don't log the entire DataFrame to avoid formatting issues
            logger.info(f"Fetched financial data for {len(financials) if hasattr(financials, '__len__') else 'unknown'} companies")

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
            logger.error(f"재무 데이터 가져오기 실패: {e}")
            company_financials = {}
            key_stats = {"PER": "N/A", "PBR": "N/A", "ROE": "N/A", "DIV": "N/A"}

        return company_financials, key_stats

    def _get_us_financial_data(
        self, company: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get financial data for US stocks using SimpleStockFetcher."""
        try:
            # Use SimpleStockFetcher to avoid API issues
            stock_data = self.simple_fetcher.fetch_stock_data(company)

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

    def _extract_financial_from_stock_data(self, stock_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract financial data from provided stock_data.
        
        Args:
            stock_data: Stock data from Yahoo Finance or other sources
            
        Returns:
            Tuple of (financials, key_stats)
        """
        # Extract financials
        financials = {
            "총수익": stock_data.get("Revenue", stock_data.get("totalRevenue", "N/A")),
            "EPS": stock_data.get("EPS", stock_data.get("trailingEps", "N/A")),
            "현재가": stock_data.get("currentPrice", stock_data.get("regularMarketPrice", "N/A")),
            "52주최고": stock_data.get("52주 최고가", stock_data.get("fiftyTwoWeekHigh", "N/A")),
            "52주최저": stock_data.get("52주 최저가", stock_data.get("fiftyTwoWeekLow", "N/A")),
            "거래량": stock_data.get("volume", stock_data.get("regularMarketVolume", "N/A")),
            "시가총액": stock_data.get("시가총액", stock_data.get("marketCap", "N/A")),
        }
        
        # Extract key statistics - Use actual values from Yahoo Finance
        key_stats = {
            "PER": stock_data.get("PER", stock_data.get("trailingPE", stock_data.get("forwardPE", "N/A"))),
            "PBR": stock_data.get("PBR", stock_data.get("priceToBook", "N/A")),
            "ROE": stock_data.get("ROE", stock_data.get("returnOnEquity", "N/A")),
            "배당수익률": stock_data.get("배당수익률", stock_data.get("dividendYield", "N/A")),
            "시가총액": stock_data.get("시가총액", stock_data.get("marketCap", "N/A")),
            "베타": stock_data.get("베타", stock_data.get("beta", "N/A")),
            "섹터": stock_data.get("섹터", stock_data.get("sector", "N/A")),
            "산업": stock_data.get("산업", stock_data.get("industry", "N/A")),
        }
        
        logger.info(f"Extracted financial data - PER: {key_stats.get('PER')}, PBR: {key_stats.get('PBR')}")
        
        return financials, key_stats
