"""
AI Agents Module

This module contains all investment analysis agents.
"""

from .base import InvestmentAgent
from .company_analyst import CompanyAnalystAgent
from .industry_expert import IndustryExpertAgent
from .macroeconomist import MacroeconomistAgent
from .technical_analyst import TechnicalAnalystAgent
from .risk_manager import RiskManagerAgent
from .mediator import MediatorAgent
from .sentiment_analyst import MarketSentimentAgent
from .news_analyst import NewsAnalysisAgent

__all__ = [
    'InvestmentAgent',
    'CompanyAnalystAgent',
    'IndustryExpertAgent',
    'MacroeconomistAgent',
    'TechnicalAnalystAgent',
    'RiskManagerAgent',
    'MediatorAgent',
    'MarketSentimentAgent',
    'NewsAnalysisAgent',
]