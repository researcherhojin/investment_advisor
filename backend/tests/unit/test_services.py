"""
Unit Tests for Application Services

Test application services and use cases.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from backend.application.services.agent_service import AgentService
from backend.domain.services.analysis_orchestrator import AnalysisOrchestrator
from backend.domain.entities.analysis import (
    AnalysisSession, AgentType, AgentAnalysis,
    InvestmentDecisionType, RiskLevel
)
from backend.domain.entities.stock import Stock


@pytest.mark.asyncio
class TestAgentService:
    """Test AgentService operations."""
    
    async def test_execute_agent_with_openai(self):
        """Test executing agent with OpenAI."""
        service = AgentService()
        
        # Mock OpenAI client
        mock_openai = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test analysis result"))]
        mock_openai.chat.completions.create.return_value = mock_response
        service.openai_client = mock_openai
        
        # Mock settings to use OpenAI
        with patch('backend.application.services.agent_service.get_settings') as mock_settings:
            mock_settings.return_value.use_streamlit_agents = False
            
            stock = Stock(ticker="AAPL", name="Apple Inc.", market="US")
            session = AnalysisSession(user_id=uuid4(), stock_id=uuid4())
            
            result = await service.execute_agent(
                agent_type=AgentType.COMPANY_ANALYST,
                stock=stock,
                session=session
            )
            
            assert result["content"] == "Test analysis result"
            assert "confidence" in result
            assert result["agent_type"] == AgentType.COMPANY_ANALYST.value
    
    async def test_execute_agent_with_streamlit_adapter(self):
        """Test executing agent with Streamlit adapter."""
        service = AgentService()
        
        # Mock Streamlit adapter
        mock_adapter = AsyncMock()
        mock_adapter.execute_agent.return_value = {
            "success": True,
            "content": "Streamlit agent result",
            "confidence": 0.85,
            "recommendation": "BUY"
        }
        service.streamlit_adapter = mock_adapter
        
        # Mock settings to use Streamlit agents
        with patch('backend.application.services.agent_service.get_settings') as mock_settings:
            mock_settings.return_value.use_streamlit_agents = True
            
            stock = Stock(ticker="AAPL", name="Apple Inc.", market="US")
            session = AnalysisSession(user_id=uuid4(), stock_id=uuid4())
            
            result = await service.execute_agent(
                agent_type=AgentType.TECHNICAL_ANALYST,
                stock=stock,
                session=session
            )
            
            assert result["content"] == "Streamlit agent result"
            assert result["confidence"] == Decimal("0.85")
            assert result["source"] == "streamlit_agent"
    
    async def test_agent_prompts_formatting(self):
        """Test agent prompt formatting with context."""
        service = AgentService()
        
        context = {
            "stock": {
                "ticker": "TSLA",
                "name": "Tesla Inc.",
                "sector": "Automotive",
                "industry": "Electric Vehicles"
            },
            "market_context": {
                "market_type": "미국 시장"
            },
            "analysis": {
                "period_months": 12
            }
        }
        
        prompt_template = service._get_company_analyst_prompt()
        formatted = await service._format_prompt(prompt_template, context)
        
        assert "TSLA" in formatted
        assert "Tesla Inc." in formatted
        assert "미국 시장" in formatted
        assert "12" in formatted


@pytest.mark.asyncio
class TestAnalysisOrchestrator:
    """Test AnalysisOrchestrator operations."""
    
    async def test_orchestrate_analysis(self):
        """Test orchestrating complete analysis workflow."""
        orchestrator = AnalysisOrchestrator()
        
        # Mock data
        session = AnalysisSession(user_id=uuid4(), stock_id=uuid4())
        session.id = uuid4()
        stock = Stock(ticker="AAPL", name="Apple Inc.", market="US")
        
        # Mock agent executor
        async def mock_executor(agent_type, stock, session, additional_context=None):
            return {
                "content": f"Analysis by {agent_type.value}",
                "confidence": 0.80,
                "execution_time_ms": 1000
            }
        
        # Execute orchestration
        result = await orchestrator.orchestrate_analysis(
            session=session,
            stock=stock,
            agent_executor_func=mock_executor
        )
        
        # Verify all agents were executed
        assert len(result) == len(orchestrator.agent_order) + 1  # +1 for mediator
        assert AgentType.MEDIATOR in result
        
        # Verify agent analysis structure
        for agent_type, analysis in result.items():
            assert isinstance(analysis, AgentAnalysis)
            assert analysis.session_id == session.id
            assert analysis.agent_type == agent_type
            assert analysis.confidence_score == Decimal("0.80")
    
    async def test_consolidate_decision_with_mediator(self):
        """Test consolidating decision with mediator result."""
        orchestrator = AnalysisOrchestrator()
        
        # Create agent analyses
        session_id = uuid4()
        agent_analyses = {
            AgentType.MEDIATOR: AgentAnalysis(
                session_id=session_id,
                agent_type=AgentType.MEDIATOR,
                analysis_result="종합 분석 결과, 강력한 매수 신호입니다. 높은 위험",
                confidence_score=Decimal("0.85")
            )
        }
        
        decision = orchestrator.consolidate_decision(agent_analyses)
        
        assert decision.decision == InvestmentDecisionType.BUY
        assert decision.confidence == Decimal("0.85")
        assert decision.risk_level == RiskLevel.HIGH
    
    async def test_consolidate_decision_without_mediator(self):
        """Test consolidating decision without mediator (fallback)."""
        orchestrator = AnalysisOrchestrator()
        
        # Create agent analyses
        session_id = uuid4()
        agent_analyses = {
            AgentType.COMPANY_ANALYST: AgentAnalysis(
                session_id=session_id,
                agent_type=AgentType.COMPANY_ANALYST,
                analysis_result="재무 상태 양호, 매수 추천",
                confidence_score=Decimal("0.85")
            ),
            AgentType.TECHNICAL_ANALYST: AgentAnalysis(
                session_id=session_id,
                agent_type=AgentType.TECHNICAL_ANALYST,
                analysis_result="기술적 지표 긍정적, 매수 시점",
                confidence_score=Decimal("0.80")
            ),
            AgentType.RISK_MANAGER: AgentAnalysis(
                session_id=session_id,
                agent_type=AgentType.RISK_MANAGER,
                analysis_result="리스크 관리 필요, 보유 권고",
                confidence_score=Decimal("0.70")
            )
        }
        
        decision = orchestrator.consolidate_decision(agent_analyses)
        
        assert decision.decision == InvestmentDecisionType.BUY  # 2 BUY vs 1 HOLD
        assert decision.confidence == Decimal("0.78")  # Average: (0.85 + 0.80 + 0.70) / 3
        assert decision.risk_level == RiskLevel.MEDIUM
    
    async def test_orchestrate_with_progress_callback(self):
        """Test orchestration with progress callback."""
        orchestrator = AnalysisOrchestrator()
        
        session = AnalysisSession(user_id=uuid4(), stock_id=uuid4())
        session.id = uuid4()
        stock = Stock(ticker="AAPL", name="Apple Inc.", market="US")
        
        # Track progress calls
        progress_calls = []
        
        async def mock_progress(message, percent):
            progress_calls.append((message, percent))
        
        async def mock_executor(agent_type, stock, session, additional_context=None):
            return {"content": "Test", "confidence": 0.75}
        
        await orchestrator.orchestrate_analysis(
            session=session,
            stock=stock,
            agent_executor_func=mock_executor,
            progress_callback=mock_progress
        )
        
        # Verify progress was reported
        assert len(progress_calls) > 0
        assert any("분석 중" in call[0] for call in progress_calls)
        assert progress_calls[-1][1] == 90  # Last progress before completion