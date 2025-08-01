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

    def __init__(self, **data):
        super().__init__(**data)
        if "llm" not in data:
            self.llm = ChatOpenAI(model_name="gpt-4o-mini-2024-07-18", temperature=0.1)

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
        from ..data import KoreaStockDataFetcher, USStockDataFetcher
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            if market == "한국장":
                fetcher = KoreaStockDataFetcher()
            else:
                fetcher = USStockDataFetcher()
            
            df = fetcher.fetch_price_history(company, start_date, end_date)

            if df.empty:
                raise ValueError(f"주가 데이터를 가져올 수 없습니다: {company}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {company}: {str(e)}")
            raise
