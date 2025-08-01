"""
Macroeconomist Agent

Analyzes macroeconomic indicators and their impact on investments.
"""

import logging
from typing import Dict, Any
from pydantic import Field
from langchain.prompts import PromptTemplate
import requests

from .base import InvestmentAgent

logger = logging.getLogger(__name__)


class MacroeconomistAgent(InvestmentAgent):
    """Agent responsible for analyzing macroeconomic conditions."""
    
    name: str = Field(default="거시경제전문가")
    description: str = (
        "금리, 인플레이션, 경제 성장, 실업률과 같은 거시경제 지표를 분석합니다."
    )
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["economy", "indicators"],
        template="""
        {economy} 시장의 현재 거시경제 상황을 종합적으로 분석해주세요:
        
        거시경제 지표: {indicators}
        
        1. 경제 상황 개요:
           - 현재 경제 사이클 단계를 평가해주세요.
           - 전반적인 경제 건전성을 분석해주세요.
        
        2. 주요 지표 분석:
           - GDP 성장률의 의미와 향후 전망을 설명해주세요.
           - 인플레이션 수준과 그 영향을 분석해주세요.
           - 금리 정책과 향후 방향성을 예측해주세요.
           - 실업률과 고용 시장 상황을 평가해주세요.
        
        3. 금융 시장에 미치는 영향:
           - 현재 거시경제 상황이 주식 시장에 미치는 영향을 분석해주세요.
           - 섹터별 영향을 차별화하여 설명해주세요.
        
        4. 글로벌 경제 연관성:
           - 글로벌 경제 동향과의 연관성을 설명해주세요.
           - 주요 교역국의 경제 상황이 미치는 영향을 분석해주세요.
        
        5. 정책 리스크:
           - 예상되는 정책 변화와 그 영향을 평가해주세요.
           - 정치적 불확실성이 경제에 미치는 영향을 고려해주세요.
        
        6. 투자 시사점:
           - 현재 거시경제 환경에서의 투자 전략을 제시해주세요.
           - 방어적/공격적 투자 접근법을 구분하여 제안해주세요.
        """
    )
    alpha_vantage_api_key: str = Field(default=None)
    
    def __init__(self, alpha_vantage_api_key: str = None, **data):
        super().__init__(**data)
        if alpha_vantage_api_key:
            self.alpha_vantage_api_key = alpha_vantage_api_key
    
    def _run(self, economy: str, market: str) -> str:
        """Execute macroeconomic analysis."""
        indicators = self.get_economic_indicators(market)
        
        analysis = self.llm.invoke(
            self.prompt.format(economy=market, indicators=str(indicators))
        ).content
        
        indicator_text = "\n".join(
            [f"{key}: {value}" for key, value in indicators.items()]
        )
        
        return f"## 거시경제전문가의 의견\n\n{analysis}\n\n현재 거시경제 지표:\n{indicator_text}"
    
    def get_economic_indicators(self, market: str) -> Dict[str, Any]:
        """
        Fetch economic indicators for the given market.
        
        Args:
            market: Market identifier
            
        Returns:
            Dictionary with economic indicators
        """
        if not self.alpha_vantage_api_key:
            logger.warning("Alpha Vantage API key not provided, using mock data")
            return self._get_mock_indicators(market)
        
        base_url = "https://www.alphavantage.co/query"
        country = "KOR" if market == "한국장" else "USA"
        
        indicators = {}
        
        # Define indicator functions to fetch
        indicator_functions = [
            ("GDP 성장률", "REAL_GDP"),
            ("인플레이션", "INFLATION"),
            ("금리", "FEDERAL_FUNDS_RATE" if country == "USA" else "INTEREST_RATE"),
            ("실업률", "UNEMPLOYMENT")
        ]
        
        for indicator_name, function_name in indicator_functions:
            try:
                params = {
                    "function": function_name,
                    "interval": "annual",
                    "apikey": self.alpha_vantage_api_key
                }
                
                if country == "KOR" and function_name != "FEDERAL_FUNDS_RATE":
                    params["country"] = "KOR"
                
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    latest_value = float(data["data"][0]["value"])
                    indicators[indicator_name] = f"{latest_value:.2f}%"
                else:
                    indicators[indicator_name] = "데이터 없음"
                    
            except Exception as e:
                logger.error(f"Error fetching {indicator_name}: {str(e)}")
                indicators[indicator_name] = "데이터 가져오기 실패"
        
        return indicators
    
    def _get_mock_indicators(self, market: str) -> Dict[str, Any]:
        """Return mock economic indicators for testing."""
        if market == "한국장":
            return {
                "GDP 성장률": "2.5%",
                "인플레이션": "3.2%",
                "금리": "3.5%",
                "실업률": "2.8%"
            }
        else:
            return {
                "GDP 성장률": "2.8%",
                "인플레이션": "3.7%",
                "금리": "5.5%",
                "실업률": "3.6%"
            }