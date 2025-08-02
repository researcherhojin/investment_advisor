"""
Unit Tests for Domain Entities

Test domain entity creation and business logic.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from backend.domain.entities.stock import Stock
from backend.domain.entities.analysis import (
    AnalysisSession,
    AnalysisStatus,
    AgentAnalysis,
    AgentType,
    InvestmentDecision,
    InvestmentDecisionType,
    RiskLevel
)


class TestStockEntity:
    """Test Stock entity."""
    
    def test_create_stock(self):
        """Test creating a stock entity."""
        stock = Stock(
            ticker="AAPL",
            name="Apple Inc.",
            market="US"
        )
        
        assert stock.ticker == "AAPL"
        assert stock.name == "Apple Inc."
        assert stock.market == "US"
        assert stock.currency == "USD"  # Default for US market
    
    def test_korean_stock_currency(self):
        """Test Korean stock defaults to KRW."""
        stock = Stock(
            ticker="005930",
            name="Samsung Electronics",
            market="KR"
        )
        
        assert stock.currency == "KRW"
        assert stock.is_korean_stock is True
    
    def test_stock_validation(self):
        """Test stock validation rules."""
        # Valid stock
        stock = Stock(
            ticker="AAPL",
            name="Apple Inc.",
            market="US",
            sector="Technology"
        )
        
        errors = stock.validate()
        assert len(errors) == 0
        
        # Invalid market
        stock.market = "INVALID"
        errors = stock.validate()
        assert len(errors) > 0
        assert any("market" in error.lower() for error in errors)


class TestAnalysisSession:
    """Test AnalysisSession entity."""
    
    def test_create_session(self):
        """Test creating an analysis session."""
        user_id = uuid4()
        stock_id = uuid4()
        
        session = AnalysisSession(
            user_id=user_id,
            stock_id=stock_id,
            analysis_period=12
        )
        
        assert session.user_id == user_id
        assert session.stock_id == stock_id
        assert session.analysis_period == 12
        assert session.status == AnalysisStatus.PENDING
    
    def test_start_analysis(self):
        """Test starting an analysis."""
        session = AnalysisSession(
            user_id=uuid4(),
            stock_id=uuid4()
        )
        
        session.start_analysis()
        
        assert session.status == AnalysisStatus.RUNNING
        assert session.started_at is not None
        assert isinstance(session.started_at, datetime)
    
    def test_complete_analysis(self):
        """Test completing an analysis."""
        session = AnalysisSession(
            user_id=uuid4(),
            stock_id=uuid4()
        )
        
        session.start_analysis()
        session.complete_analysis()
        
        assert session.status == AnalysisStatus.COMPLETED
        assert session.completed_at is not None
        assert session.duration_seconds > 0
    
    def test_fail_analysis(self):
        """Test failing an analysis."""
        session = AnalysisSession(
            user_id=uuid4(),
            stock_id=uuid4()
        )
        
        session.start_analysis()
        error_msg = "Test error"
        session.fail_analysis(error_msg)
        
        assert session.status == AnalysisStatus.FAILED
        assert session.error_message == error_msg
        assert session.completed_at is not None


class TestAgentAnalysis:
    """Test AgentAnalysis entity."""
    
    def test_create_agent_analysis(self):
        """Test creating an agent analysis."""
        session_id = uuid4()
        
        analysis = AgentAnalysis(
            session_id=session_id,
            agent_type=AgentType.COMPANY_ANALYST,
            analysis_result="Strong financial performance...",
            confidence_score=Decimal("0.85"),
            execution_time_ms=1500
        )
        
        assert analysis.session_id == session_id
        assert analysis.agent_type == AgentType.COMPANY_ANALYST
        assert analysis.confidence_score == Decimal("0.85")
        assert analysis.execution_time_ms == 1500
    
    def test_agent_analysis_metadata(self):
        """Test agent analysis with metadata."""
        analysis = AgentAnalysis(
            session_id=uuid4(),
            agent_type=AgentType.TECHNICAL_ANALYST,
            analysis_result="Technical indicators show...",
            metadata={
                "rsi": 65,
                "macd": "bullish",
                "volume": "increasing"
            }
        )
        
        assert analysis.metadata["rsi"] == 65
        assert analysis.metadata["macd"] == "bullish"


class TestInvestmentDecision:
    """Test InvestmentDecision entity."""
    
    def test_create_investment_decision(self):
        """Test creating an investment decision."""
        session_id = uuid4()
        
        decision = InvestmentDecision(
            session_id=session_id,
            decision=InvestmentDecisionType.BUY,
            confidence=Decimal("0.82"),
            rationale="Strong fundamentals and positive technical indicators",
            price_target=Decimal("210.50"),
            stop_loss=Decimal("185.00"),
            time_horizon="6-12 months",
            risk_level=RiskLevel.MEDIUM
        )
        
        assert decision.session_id == session_id
        assert decision.decision == InvestmentDecisionType.BUY
        assert decision.confidence == Decimal("0.82")
        assert decision.price_target == Decimal("210.50")
        assert decision.risk_level == RiskLevel.MEDIUM
    
    def test_decision_with_insights(self):
        """Test investment decision with structured insights."""
        decision = InvestmentDecision(
            decision=InvestmentDecisionType.HOLD,
            confidence=Decimal("0.70"),
            rationale="Market uncertainty suggests caution",
            key_factors=[
                "Strong revenue growth",
                "Increasing market share",
                "High valuation"
            ],
            risks=[
                "Regulatory challenges",
                "Competition from new entrants"
            ],
            opportunities=[
                "International expansion",
                "New product launches"
            ]
        )
        
        assert len(decision.key_factors) == 3
        assert len(decision.risks) == 2
        assert len(decision.opportunities) == 2
        assert decision.decision == InvestmentDecisionType.HOLD