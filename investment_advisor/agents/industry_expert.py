"""
Industry Expert Agent

Evaluates industry trends, technological developments, and regulatory environment.
"""

import logging
from typing import Dict, Any
from pydantic import Field
from langchain.prompts import PromptTemplate

from .base import InvestmentAgent
from ..data.simple_fetcher import SimpleStockFetcher

logger = logging.getLogger(__name__)


class IndustryExpertAgent(InvestmentAgent):
    """Agent responsible for analyzing industry trends and environment."""

    name: str = Field(default="산업전문가")
    description: str = "산업 트렌드, 기술 발전, 규제 환경을 평가합니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["industry", "market"],
        template="""
        당신은 15년 경력의 {industry} 산업 전문가입니다. 
        
        중요: Tesla(TSLA)를 분석하는 경우, 전기차(EV) 산업에 집중하세요. 일반적인 기술/소프트웨어가 아닌 전기차, 배터리, 자율주행, 에너지 저장 시스템 관련 분석을 제공하세요.
        
        {market} 시장의 {industry} 섹터에 대한 심층 분석을 제공해주세요:

        **1. 산업 사이클 및 현재 위치**
           - 현재 산업 사이클 단계: 성장기/성숙기/쇠퇴기/회복기 중 판단
           - **산업 성장률: 연평균 X% (최근 3년 vs 향후 3년 전망)**
           - 글로벌 vs 국내 시장 동향 차이점 분석
           - 계절성/주기성 특성 및 현재 타이밍

        **2. 기술 혁신 및 디지털 전환**
           - **게임체인저 기술 TOP 3** (AI, IoT, 블록체인 등)
           - 기존 플레이어 vs 신규 테크 기업 경쟁 구도
           - 기술 도입 비용 vs 효율성 개선 효과 분석
           - **디지털 전환 완료도: 초기/진행/완성 단계**

        **3. 규제 환경 및 정책 리스크**
           - 현재 규제 강도: 완화/중립/강화 트렌드
           - **2024-2025 예상 규제 변화 3가지**
           - ESG 규제가 수익성에 미치는 영향 정도
           - 정부 정책 지원/제재 가능성 평가

        **4. 밸류체인 및 경쟁 구조**
           - **시장 집중도: HHI 지수 또는 상위 5사 점유율**
           - 공급망 리스크 노출도 (원자재, 반도체 등)
           - 진입장벽 높이: 높음/보통/낮음 (자본, 기술, 규제)
           - **가격 결정력: 강함/보통/약함**

        **5. 수익성 및 마진 트렌드**
           - **산업 평균 영업이익률: X% (전년 대비 증감)**
           - 마진 압박 요인: 인건비/원자재/경쟁 심화
           - **앞으로 12개월 마진 전망: 개선/악화/유지**
           - 고마진 틈새시장 기회 영역

        **6. 투자 테마 및 수혜주 특성**
           - **핵심 투자 테마 3가지** (구체적 키워드)
           - 대장주 vs 중소형주 투자 매력도 비교
           - **선호 기업 특성: 1) 2) 3)** (규모, 기술력, 재무건전성 등)
           - 밸류에이션 적정 PER/PBR 레인지

        **7. 리스크 요인 및 모니터링 포인트**
           - **단기 리스크 (6개월): X, Y, Z**
           - **중장기 구조적 위험: A, B, C**
           - 경기침체 시 방어력: 방어적/중립/경기민감
           - **핵심 모니터링 지표 3가지** 제시

        **8. 투자 의견 및 비중 조절**
           - **섹터 투자의견: 비중확대/비중유지/비중축소**
           - **포트폴리오 적정 비중: X% (전체 대비)**
           - 투자 시계: 단기 트레이딩/중기 보유/장기 투자
           - **Best Pick 기업 특성 및 선별 기준**

        ⚠️ 모든 전망은 구체적 수치와 시기를 제시하고, 근거를 명확히 해주세요.
        """
    )

    def _run(self, industry: str, market: str) -> str:
        """Execute industry analysis."""
        try:
            analysis = self.llm.invoke(
                self.prompt.format(industry=industry, market=market)
            ).content

            # Industry analysis typically has high confidence
            confidence = "높음"

            # Validate industry analysis completeness
            if not self.validate_analysis_completeness(analysis):
                logger.warning(f"Industry analysis for {industry} may be incomplete")
                confidence = "보통"

            return self.format_response(analysis, confidence)

        except Exception as e:
            logger.error(f"Error in industry analysis for {industry}: {str(e)}")
            return self.format_response(
                f"산업 분석 중 오류가 발생했습니다: {str(e)}",
                "낮음"
            )

    def get_industry_data(self, industry: str) -> Dict[str, Any]:
        """
        Get industry-specific data (placeholder for future implementation).

        Args:
            industry: Industry name

        Returns:
            Dictionary with industry data
        """
        # This is a placeholder for future implementation
        # In a real system, this would fetch actual industry data from APIs
        return {
            "trend": "성장중",
            "tech_advancement": "AI 통합",
            "regulatory_environment": "규제 강화 중",
            "market_size": "대규모",
            "growth_rate": "연 10-15%"
        }
