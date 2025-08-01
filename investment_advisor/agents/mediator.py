"""
Mediator Agent

Synthesizes opinions from all other agents to make final investment decisions.
"""

from typing import Dict
from pydantic import Field
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from .base import InvestmentAgent


class MediatorAgent(InvestmentAgent):
    """Agent responsible for synthesizing all analyses and making final recommendations."""
    
    name: str = Field(default="중재자")
    description: str = "다른 Agent들의 의견을 종합하여 최종 투자 결정을 내립니다."
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
        다음 전문가들의 분석을 종합하여 균형 잡힌 최종 투자 의견을 제시해주세요:
        
        기업 분석: {company_analysis}
        산업 분석: {industry_analysis}
        거시경제 분석: {macro_analysis}
        기술적 분석: {technical_analysis}
        리스크 분석: {risk_analysis}
        시장: {market}
        
        다음 사항을 포함하여 종합적인 투자 의견을 제시해주세요:
        
        1. 투자 추천 등급:
           - 강력 매수 / 매수 / 보유 / 매도 / 강력 매도 중 선택
           - 선택의 핵심 근거 3가지 제시
        
        2. 투자 시계별 전망:
           - 단기 (1-3개월): 기술적 분석 중심
           - 중기 (3-12개월): 기업 실적과 산업 동향 중심
           - 장기 (1년 이상): 거시경제와 산업 구조 변화 중심
        
        3. 핵심 투자 포인트:
           - 주요 매수 근거 (상위 3개)
           - 주요 리스크 요인 (상위 3개)
           - 모니터링 포인트
        
        4. 가격 전략:
           - 적정 매수 가격대와 근거
           - 목표 주가와 도달 시기
           - 손절 가격과 리스크 관리 방안
        
        5. 포트폴리오 전략:
           - 추천 투자 비중
           - 분산 투자 방안
           - 리밸런싱 시점
        
        6. 투자자 유형별 조언:
           - 보수적 투자자: 안정성 중심
           - 공격적 투자자: 수익률 중심
           - 중립적 투자자: 균형 잡힌 접근
        
        7. 주요 체크포인트:
           - 투자 의견 변경을 고려해야 할 상황
           - 주시해야 할 지표나 이벤트
        
        8. 종합 의견:
           - 전체적인 투자 매력도 평가
           - 다른 투자 대안과의 비교
           - 최종 추천 사항
        
        주의: 이 분석은 투자 참고 자료이며, 실제 투자 결정은 개인의 재무 상황과 투자 목표를 고려하여 신중히 내려야 함을 명시해주세요.
        """
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        if "llm" not in data:
            self.llm = ChatOpenAI(
                model_name="gpt-4o-mini-2024-07-18",
                temperature=0.1
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