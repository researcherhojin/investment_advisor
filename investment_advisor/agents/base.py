"""
Base Agent Class

Provides the abstract base class for all investment analysis agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

import pandas as pd
from datetime import datetime, timedelta
from pydantic import Field
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from ..core import get_settings

logger = logging.getLogger(__name__)


class InvestmentAgent(BaseTool, ABC):
    """Abstract base class for all investment analysis agents."""

    name: str = Field(...)
    description: str
    prompt: PromptTemplate
    weight: float = Field(default=1.0)
    llm: Any = Field(
        default_factory=lambda: ChatOpenAI(
            model_name="gpt-4o-mini-2024-07-18", temperature=0.1
        )
    )

    # Standard response format for consistency
    response_format: Dict[str, Any] = Field(default_factory=lambda: {
        "confidence_level": "높음/보통/낮음",
        "key_metrics": {},
        "recommendations": [],
        "risk_factors": [],
        "time_horizon": "단기/중기/장기"
    })

    def __init__(self, **data):
        super().__init__(**data)
        if "llm" not in data:
            settings = get_settings()
            self.llm = ChatOpenAI(
                model_name=settings.default_model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )

    @abstractmethod
    def _run(self, *args, **kwargs) -> str:
        """Execute the agent's analysis."""
        pass

    def get_stock_data(self, company: str, market: str) -> pd.DataFrame:
        """
        Fetch stock data for the given company and market.
        
        This method is kept for backward compatibility.
        It now delegates to the appropriate data fetcher.

        Args:
            company: Stock ticker symbol
            market: Market identifier ("한국장" or "미국장")

        Returns:
            DataFrame with stock price history
        """
        from ..data import StableFetcher
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            # Use StableFetcher for all markets
            fetcher = StableFetcher()
            df = fetcher.fetch_price_history(company, start_date, end_date)

            if df.empty:
                raise ValueError(f"주가 데이터를 가져올 수 없습니다: {company}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {company}: {str(e)}")
            raise ValueError(f"Error fetching data for {company}: {str(e)}")
    
    def format_response(self, analysis_text: str, confidence: str = "보통") -> str:
        """
        Format agent response with consistent structure.
        
        Args:
            analysis_text: Raw analysis text from the agent
            confidence: Confidence level (높음/보통/낮음)
            
        Returns:
            Formatted response with consistent structure
        """
        header = f"## {self.name}의 분석 ({confidence} 신뢰도)\n\n"
        
        # Add data quality indicator
        data_quality = "📊 **데이터 품질**: SimpleStockFetcher 기반 고품질 시뮬레이션\n\n"
        
        # Add timestamp
        timestamp = f"🕒 **분석 시점**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        footer = f"\n\n---\n*{self.name} | 신뢰도: {confidence} | AI 기반 분석*"
        
        return header + data_quality + timestamp + analysis_text + footer
    
    def validate_analysis_completeness(self, analysis: str) -> bool:
        """
        Validate that analysis contains required elements.
        
        Args:
            analysis: Analysis text to validate
            
        Returns:
            True if analysis meets minimum requirements
        """
        # More lenient validation - check for minimum length and basic content
        if len(analysis) < 100:
            return False
        
        # Check for at least 2 of these elements
        key_elements = [
            "투자", "매수", "매도", "보유",  # Investment terms
            "리스크", "위험", "안전",  # Risk terms
            "가격", "목표가", "전망",  # Price/outlook terms  
            "%", "배", "원"  # Numerical indicators
        ]
        
        found_count = sum(1 for element in key_elements if element in analysis)
        return found_count >= 2
