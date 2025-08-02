"""
Unit Tests for Repository Implementations

Test repository database operations.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.domain.entities.stock import Stock
from backend.domain.entities.analysis import (
    AnalysisSession, AnalysisStatus, AgentType,
    InvestmentDecisionType, RiskLevel
)
from backend.infrastructure.repositories.stock_repository import StockRepository
from backend.infrastructure.repositories.analysis_session_repository import AnalysisSessionRepository
from backend.infrastructure.repositories.agent_analysis_repository import AgentAnalysisRepository
from backend.infrastructure.repositories.investment_decision_repository import InvestmentDecisionRepository


@pytest.mark.asyncio
class TestStockRepository:
    """Test StockRepository operations."""
    
    async def test_create_stock(self, db_session):
        """Test creating a stock."""
        repo = StockRepository(db_session)
        
        stock = Stock(
            ticker="AAPL",
            name="Apple Inc.",
            market="US",
            sector="Technology",
            industry="Consumer Electronics"
        )
        
        saved_stock = await repo.create_stock(stock)
        
        assert saved_stock.id is not None
        assert saved_stock.ticker == "AAPL"
        assert saved_stock.created_at is not None
    
    async def test_get_stock_by_ticker(self, db_session, create_test_stock):
        """Test retrieving stock by ticker."""
        repo = StockRepository(db_session)
        
        # Create test stock
        stock = await create_test_stock(ticker="MSFT", name="Microsoft", market="US")
        
        # Retrieve by ticker
        found_stock = await repo.get_stock_by_ticker("MSFT", "US")
        
        assert found_stock is not None
        assert found_stock.id == stock.id
        assert found_stock.ticker == "MSFT"
    
    async def test_search_stocks(self, db_session, create_test_stock):
        """Test searching stocks."""
        repo = StockRepository(db_session)
        
        # Create test stocks
        await create_test_stock(ticker="AAPL", name="Apple Inc.", market="US")
        await create_test_stock(ticker="GOOGL", name="Alphabet Inc.", market="US")
        await create_test_stock(ticker="005930", name="Samsung Electronics", market="KR")
        
        # Search by partial name
        results = await repo.search_stocks("Apple", limit=10)
        assert len(results) == 1
        assert results[0].ticker == "AAPL"
        
        # Search with market filter
        results = await repo.search_stocks("", market="KR", limit=10)
        assert len(results) == 1
        assert results[0].ticker == "005930"
    
    async def test_update_stock(self, db_session, create_test_stock):
        """Test updating stock information."""
        repo = StockRepository(db_session)
        
        # Create test stock
        stock = await create_test_stock(ticker="TSLA", name="Tesla Inc.")
        
        # Update stock
        updated = await repo.update_stock(
            stock.id,
            sector="Automotive",
            industry="Electric Vehicles"
        )
        
        assert updated.sector == "Automotive"
        assert updated.industry == "Electric Vehicles"


@pytest.mark.asyncio
class TestAnalysisSessionRepository:
    """Test AnalysisSessionRepository operations."""
    
    async def test_create_session(self, db_session):
        """Test creating an analysis session."""
        repo = AnalysisSessionRepository(db_session)
        
        session = AnalysisSession(
            user_id=uuid4(),
            stock_id=uuid4(),
            analysis_period=12
        )
        
        saved_session = await repo.create_session(session)
        
        assert saved_session.id is not None
        assert saved_session.status == AnalysisStatus.PENDING
    
    async def test_update_session_status(self, db_session):
        """Test updating session status."""
        repo = AnalysisSessionRepository(db_session)
        
        # Create session
        session = AnalysisSession(
            user_id=uuid4(),
            stock_id=uuid4()
        )
        saved_session = await repo.create_session(session)
        
        # Start analysis
        saved_session.start_analysis()
        updated = await repo.update_session(saved_session)
        
        assert updated.status == AnalysisStatus.RUNNING
        assert updated.started_at is not None
    
    async def test_get_user_sessions(self, db_session, create_test_user):
        """Test retrieving user sessions."""
        repo = AnalysisSessionRepository(db_session)
        user = await create_test_user()
        
        # Create multiple sessions
        for i in range(3):
            session = AnalysisSession(
                user_id=user.id,
                stock_id=uuid4()
            )
            await repo.create_session(session)
        
        # Get user sessions
        sessions = await repo.get_user_sessions(user.id)
        
        assert len(sessions) == 3
        assert all(s.user_id == user.id for s in sessions)
    
    async def test_cleanup_stale_sessions(self, db_session):
        """Test cleaning up stale sessions."""
        repo = AnalysisSessionRepository(db_session)
        
        # Create old running session
        session = AnalysisSession(
            user_id=uuid4(),
            stock_id=uuid4()
        )
        session.start_analysis()
        saved = await repo.create_session(session)
        
        # Manually set started_at to old time
        from backend.infrastructure.database.models import AnalysisSession as SessionModel
        stmt = f"UPDATE analysis_sessions SET started_at = :started_at WHERE id = :id"
        await db_session.execute(
            stmt,
            {"started_at": datetime.utcnow() - timedelta(hours=25), "id": saved.id}
        )
        await db_session.commit()
        
        # Cleanup stale sessions
        cleaned = await repo.cleanup_stale_sessions(timeout_hours=24)
        
        assert cleaned > 0


@pytest.mark.asyncio
class TestAgentAnalysisRepository:
    """Test AgentAnalysisRepository operations."""
    
    async def test_create_agent_analysis(self, db_session):
        """Test creating agent analysis."""
        from backend.domain.entities.analysis import AgentAnalysis
        repo = AgentAnalysisRepository(db_session)
        
        analysis = AgentAnalysis(
            session_id=uuid4(),
            agent_type=AgentType.COMPANY_ANALYST,
            analysis_result="Test analysis result",
            confidence_score=0.85,
            execution_time_ms=1200
        )
        
        saved = await repo.create_analysis(analysis)
        
        assert saved.id is not None
        assert saved.agent_type == AgentType.COMPANY_ANALYST
        assert saved.confidence_score == 0.85
    
    async def test_get_session_analyses(self, db_session):
        """Test retrieving analyses for a session."""
        from backend.domain.entities.analysis import AgentAnalysis
        repo = AgentAnalysisRepository(db_session)
        session_id = uuid4()
        
        # Create multiple analyses
        for agent_type in [AgentType.COMPANY_ANALYST, AgentType.TECHNICAL_ANALYST]:
            analysis = AgentAnalysis(
                session_id=session_id,
                agent_type=agent_type,
                analysis_result=f"Analysis by {agent_type.value}",
                confidence_score=0.75
            )
            await repo.create_analysis(analysis)
        
        # Get session analyses
        analyses = await repo.get_session_analyses(session_id)
        
        assert len(analyses) == 2
        assert all(a.session_id == session_id for a in analyses)


@pytest.mark.asyncio
class TestInvestmentDecisionRepository:
    """Test InvestmentDecisionRepository operations."""
    
    async def test_create_decision(self, db_session):
        """Test creating investment decision."""
        from backend.domain.entities.analysis import InvestmentDecision
        repo = InvestmentDecisionRepository(db_session)
        
        decision = InvestmentDecision(
            session_id=uuid4(),
            decision=InvestmentDecisionType.BUY,
            confidence=0.82,
            rationale="Strong buy signal",
            price_target=200.0,
            stop_loss=180.0,
            time_horizon="6-12 months",
            risk_level=RiskLevel.MEDIUM
        )
        
        saved = await repo.create_decision(decision)
        
        assert saved.id is not None
        assert saved.decision == InvestmentDecisionType.BUY
        assert saved.confidence == 0.82
    
    async def test_get_decision_statistics(self, db_session):
        """Test getting decision statistics."""
        from backend.domain.entities.analysis import InvestmentDecision
        repo = InvestmentDecisionRepository(db_session)
        
        # Create test decisions
        decisions = [
            (InvestmentDecisionType.BUY, 0.85),
            (InvestmentDecisionType.BUY, 0.78),
            (InvestmentDecisionType.SELL, 0.72),
            (InvestmentDecisionType.HOLD, 0.65),
        ]
        
        for decision_type, confidence in decisions:
            decision = InvestmentDecision(
                session_id=uuid4(),
                decision=decision_type,
                confidence=confidence,
                rationale=f"Test {decision_type.value}"
            )
            await repo.create_decision(decision)
        
        # Get statistics
        stats = await repo.get_decision_statistics(days=30)
        
        assert stats["total"] >= 4
        assert stats["buy_count"] >= 2
        assert stats["sell_count"] >= 1
        assert stats["hold_count"] >= 1
        assert stats["avg_confidence"] > 0