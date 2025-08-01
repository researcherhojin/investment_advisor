"""
Use Case Dependencies

Dependency injection setup for use cases and application services.
"""

from functools import lru_cache

from application.use_cases.analyze_stock import AnalyzeStockUseCase, GetAnalysisResultsUseCase
from application.services.agent_service import AgentService
from domain.services.analysis_orchestrator import AnalysisOrchestrator

# TODO: These will be replaced with actual repository implementations
# For now, we'll use mock repositories for development


class MockStockRepository:
    """Mock stock repository for development."""
    
    async def get_stock_by_ticker(self, ticker: str, market: str):
        """Mock get stock by ticker."""
        return None
    
    async def create_stock(self, stock):
        """Mock create stock."""
        return stock
    
    async def get_latest_price(self, stock_id):
        """Mock get latest price."""
        return None


class MockAnalysisSessionRepository:
    """Mock analysis session repository for development."""
    
    async def create_session(self, session):
        """Mock create session."""
        return session
    
    async def get_session_by_id(self, session_id):
        """Mock get session by ID."""
        return None
    
    async def update_session(self, session):
        """Mock update session."""
        return session


class MockAgentAnalysisRepository:
    """Mock agent analysis repository for development."""
    
    async def create_analysis(self, analysis):
        """Mock create analysis."""
        return analysis
    
    async def get_session_analyses(self, session_id):
        """Mock get session analyses."""
        return []


class MockInvestmentDecisionRepository:
    """Mock investment decision repository for development."""
    
    async def create_decision(self, decision):
        """Mock create decision."""
        return decision
    
    async def get_session_decision(self, session_id):
        """Mock get session decision."""
        return None


# Repository instances (will be replaced with real implementations)
stock_repository = MockStockRepository()
session_repository = MockAnalysisSessionRepository()
agent_analysis_repository = MockAgentAnalysisRepository()
decision_repository = MockInvestmentDecisionRepository()

# Service instances
agent_service = AgentService()
analysis_orchestrator = AnalysisOrchestrator()


@lru_cache()  
def get_analyze_stock_use_case() -> AnalyzeStockUseCase:
    """Get analyze stock use case with dependencies."""
    return AnalyzeStockUseCase(
        stock_repository=stock_repository,
        session_repository=session_repository,
        agent_analysis_repository=agent_analysis_repository,
        decision_repository=decision_repository,
        agent_service=agent_service,
        analysis_orchestrator=analysis_orchestrator
    )


@lru_cache()
def get_analysis_results_use_case() -> GetAnalysisResultsUseCase:
    """Get analysis results use case with dependencies."""
    return GetAnalysisResultsUseCase(
        session_repository=session_repository,
        agent_analysis_repository=agent_analysis_repository,
        decision_repository=decision_repository,
        stock_repository=stock_repository
    )