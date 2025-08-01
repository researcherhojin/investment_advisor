"""
Industry Expert Agent

Evaluates industry trends, technological developments, and regulatory environment.
"""

from typing import Dict, Any
from pydantic import Field
from langchain.prompts import PromptTemplate

from .base import InvestmentAgent


class IndustryExpertAgent(InvestmentAgent):
    """Agent responsible for analyzing industry trends and environment."""
    
    name: str = Field(default="산업전문가")
    description: str = "산업 트렌드, 기술 발전, 규제 환경을 평가합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["industry", "market"],
        template="""
        {market} 시장의 {industry} 산업에 대한 종합적인 분석을 수행해주세요:
        
        1. 산업 현황 및 트렌드:
           - 현재 산업의 전반적인 상황과 최근 동향을 설명해주세요.
           - 향후 3-5년간 예상되는 주요 트렌드를 제시해주세요.
        
        2. 기술 발전 및 혁신:
           - 산업 내 진행 중인 주요 기술 혁신을 설명해주세요.
           - 이러한 기술 발전이 산업에 미칠 영향을 분석해주세요.
        
        3. 규제 환경:
           - 현재 및 예상되는 규제 변화를 설명해주세요.
           - 규제가 산업 성장에 미치는 영향을 평가해주세요.
        
        4. 경쟁 구도:
           - 산업 내 주요 경쟁자들과 시장 점유율을 분석해주세요.
           - 신규 진입자와 대체재의 위협을 평가해주세요.
        
        5. 성장 동력과 위험 요인:
           - 산업의 주요 성장 동력을 식별해주세요.
           - 잠재적 위험 요인과 도전 과제를 제시해주세요.
        
        6. 투자 기회:
           - 산업 내 유망한 투자 기회를 제시해주세요.
           - 투자 시 고려해야 할 주요 사항을 설명해주세요.
        """
    )
    
    def _run(self, industry: str, market: str) -> str:
        """Execute industry analysis."""
        analysis = self.llm.invoke(
            self.prompt.format(industry=industry, market=market)
        ).content
        
        return f"## 산업전문가의 의견\n\n{analysis}"
    
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