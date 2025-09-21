"""
Mediator Agent

Synthesizes opinions from all other agents to make final investment decisions.
"""

from typing import Dict
from pydantic import Field
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from .base import InvestmentAgent
from ..data.simple_fetcher import SimpleStockFetcher


class MediatorAgent(InvestmentAgent):
    """Agent responsible for synthesizing all analyses and making final recommendations."""

    name: str = Field(default="중재자")
    description: str = "다른 Agent들의 의견을 종합하여 최종 투자 결정을 내립니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)

    def __init__(self, **data):
        super().__init__(**data)
        if "llm" not in data:
            self.llm = ChatOpenAI(
                model_name="gpt-4o-mini-2024-07-18",
                temperature=0.1
            )
    prompt: PromptTemplate = PromptTemplate(
        input_variables=[
            "company_analysis",
            "industry_analysis",
            "macro_analysis",
            "technical_analysis",
            "risk_analysis",
            "market"
        ],
        template="""
        당신은 25년 경력의 수석 투자전략가입니다. 5명의 전문가 의견을 종합하여 최종 투자 결정을 내려주세요:

        📊 **전문가 분석 리포트**
        기업분석가: {company_analysis}
        산업전문가: {industry_analysis}
        거시경제전문가: {macro_analysis}
        기술분석가: {technical_analysis}
        리스크관리자: {risk_analysis}

        **🎯 STEP 1: 전문가 의견 충돌 분석**
        - 매수/매도 의견이 엇갈리는 부분 식별
        - 가격 목표의 차이와 그 원인 분석
        - 리스크 평가의 차이점 해석
        - **최종 판단: 각 전문가 의견의 신뢰도를 1-10점으로 평가**

        **📈 STEP 2: 가중평균 의사결정**
        - 기업분석가 의견 가중치: 30% (펀더멘털)
        - 기술분석가 의견 가중치: 25% (타이밍)
        - 산업전문가 의견 가중치: 20% (섹터 트렌드)
        - 리스크관리자 의견 가중치: 15% (안전성)
        - 거시경제전문가 의견 가중치: 10% (환경)

        **🎲 STEP 3: 최종 투자 결정 (필수)**
        - **투자등급: 강력매수/매수/중립/매도/강력매도**
        - **신뢰도 점수: X/10점 (의견 일치도 기준)**
        - **목표주가: $XXX (6-12개월 기준)**
        - **매수 타이밍: 즉시/리트레이스먼트 후/패턴 완성 후**

        **💰 STEP 4: 구체적 투자 전략**
        - **포지션 사이즈: 전체 포트폴리오의 X%**
        - **분할 매수 계획: 1차 X%, 2차 X% (조건별)**
        - **손절선: 현재가 대비 -X% ($XXX)**
        - **익절 계획: 1차 익절 +X%, 최종 목표 +X%**

        **⏰ STEP 5: 시나리오 분석 (확률 기반)**
        - **Bull Case (30% 확률): 목표가 $XXX, 상승요인 3가지**
        - **Base Case (50% 확률): 목표가 $XXX, 중립요인 3가지**
        - **Bear Case (20% 확률): 목표가 $XXX, 하락요인 3가지**

        **🚨 STEP 6: 리스크 관리 체크리스트**
        - [ ] 섹터 집중도 5% 이하 유지
        - [ ] 단일 종목 10% 이하 투자
        - [ ] 손절선 준수 (기계적 실행)
        - [ ] **Exit 전략: 3가지 상황별 대응 방안**

        **📊 STEP 7: 모니터링 체크포인트**
        - **Daily**: 기술적 지지/저항선 모니터링
        - **Weekly**: 거래량 패턴과 모멘텀 변화 추적
        - **Monthly**: 펀더멘털 변화와 컨센서스 추이
        - **Quarterly**: 실적 발표와 가이던스 업데이트

        **⚖️ 최종 결론 (Executive Summary)**
        - **One-Line 투자논리**: 핵심 메시지 한 줄 요약
        - **Risk-Reward 비율**: 1:X (위험 대비 수익 기대치)
        - **투자자 유형별 권고**: 보수적/중립적/공격적 투자자 구분
        - **타이밍 점수**: X/10 (현재 진입 시점의 적절성)

        ⚠️ **면책조항**: 본 분석은 참고자료이며, 투자 손실에 대한 책임을 지지 않습니다. 개인의 위험성향과 재무상황을 고려하여 신중한 투자 결정을 하시기 바랍니다.
        """
    )

    def _run(self, inputs: Dict[str, str]) -> str:
        """
        Execute mediator analysis.

        Args:
            inputs: Dictionary containing all agent analyses

        Returns:
            Final synthesized investment recommendation
        """
        return self.llm.invoke(self.prompt.format(**inputs)).content

    def synthesize_recommendations(
        self,
        analyses: Dict[str, str],
        market: str
    ) -> str:
        """
        Synthesize recommendations from all agents.

        Args:
            analyses: Dictionary of agent analyses
            market: Market identifier

        Returns:
            Final investment recommendation
        """
        mediator_inputs = {
            "company_analysis": analyses.get("기업분석가", "분석 데이터 없음"),
            "industry_analysis": analyses.get("산업전문가", "분석 데이터 없음"),
            "macro_analysis": analyses.get("거시경제전문가", "분석 데이터 없음"),
            "technical_analysis": analyses.get("기술분석가", "분석 데이터 없음"),
            "risk_analysis": analyses.get("리스크관리자", "분석 데이터 없음"),
            "market": market
        }

        return self._run(mediator_inputs)
