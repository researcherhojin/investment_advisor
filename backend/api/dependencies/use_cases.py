"""
Use Case Dependencies

Dependency injection for use cases in API routes.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from application.use_cases.analyze_stock import AnalyzeStockUseCase, GetAnalysisResultsUseCase
from application.services.agent_service import AgentService
from domain.services.analysis_orchestrator import AnalysisOrchestrator
from infrastructure.repositories.stock_repository import StockRepository
from infrastructure.repositories.analysis_repository import (
    AnalysisSessionRepository,
    AgentAnalysisRepository,
    InvestmentDecisionRepository
)
from api.dependencies.database import get_db_session
from core.config import get_settings


async def get_stock_repository(
    db: AsyncSession = Depends(get_db_session)
) -> StockRepository:
    """Get stock repository instance."""
    return StockRepository(db)


async def get_analysis_session_repository(
    db: AsyncSession = Depends(get_db_session)
) -> AnalysisSessionRepository:
    """Get analysis session repository instance."""
    return AnalysisSessionRepository(db)


async def get_agent_analysis_repository(
    db: AsyncSession = Depends(get_db_session)
) -> AgentAnalysisRepository:
    """Get agent analysis repository instance."""
    return AgentAnalysisRepository(db)


async def get_investment_decision_repository(
    db: AsyncSession = Depends(get_db_session)
) -> InvestmentDecisionRepository:
    """Get investment decision repository instance."""
    return InvestmentDecisionRepository(db)


async def get_agent_service() -> AgentService:
    """Get agent service instance."""
    return AgentService()


async def get_analysis_orchestrator() -> AnalysisOrchestrator:
    """Get analysis orchestrator instance."""
    return AnalysisOrchestrator()


async def get_analyze_stock_use_case(
    stock_repository: StockRepository = Depends(get_stock_repository),
    session_repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
    agent_analysis_repository: AgentAnalysisRepository = Depends(get_agent_analysis_repository),
    decision_repository: InvestmentDecisionRepository = Depends(get_investment_decision_repository),
    agent_service: AgentService = Depends(get_agent_service),
    analysis_orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator)
) -> AnalyzeStockUseCase:
    """Get analyze stock use case instance."""
    return AnalyzeStockUseCase(
        stock_repository=stock_repository,
        session_repository=session_repository,
        agent_analysis_repository=agent_analysis_repository,
        decision_repository=decision_repository,
        agent_service=agent_service,
        analysis_orchestrator=analysis_orchestrator
    )


async def get_analysis_results_use_case(
    session_repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
    agent_analysis_repository: AgentAnalysisRepository = Depends(get_agent_analysis_repository),
    decision_repository: InvestmentDecisionRepository = Depends(get_investment_decision_repository),
    stock_repository: StockRepository = Depends(get_stock_repository)
) -> GetAnalysisResultsUseCase:
    """Get analysis results use case instance."""
    return GetAnalysisResultsUseCase(
        session_repository=session_repository,
        agent_analysis_repository=agent_analysis_repository,
        decision_repository=decision_repository,
        stock_repository=stock_repository
    )