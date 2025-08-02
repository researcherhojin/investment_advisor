"""
Integration Tests for Use Cases

Test complete use case flows with all dependencies.
"""

import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from backend.application.use_cases.analyze_stock import AnalyzeStockUseCase, GetAnalysisResultsUseCase
from backend.application.dtos.analysis_dto import AnalysisRequestDTO
from backend.domain.entities.analysis import AnalysisStatus, InvestmentDecisionType


@pytest.mark.asyncio
class TestAnalyzeStockUseCase:
    """Test AnalyzeStockUseCase with real repositories."""
    
    async def test_complete_analysis_workflow(
        self,
        db_session,
        create_test_user,
        create_test_stock,
        mock_agent_responses
    ):
        """Test complete analysis workflow from request to decision."""
        from backend.infrastructure.repositories.stock_repository import StockRepository
        from backend.infrastructure.repositories.analysis_session_repository import AnalysisSessionRepository
        from backend.infrastructure.repositories.agent_analysis_repository import AgentAnalysisRepository
        from backend.infrastructure.repositories.investment_decision_repository import InvestmentDecisionRepository
        from backend.application.services.agent_service import AgentService
        from backend.domain.services.analysis_orchestrator import AnalysisOrchestrator
        
        # Create test data
        user = await create_test_user()
        stock = await create_test_stock(ticker="AAPL", name="Apple Inc.", market="US")
        
        # Initialize repositories
        stock_repo = StockRepository(db_session)
        session_repo = AnalysisSessionRepository(db_session)
        agent_repo = AgentAnalysisRepository(db_session)
        decision_repo = InvestmentDecisionRepository(db_session)
        
        # Mock agent service
        agent_service = AgentService()
        with patch.object(agent_service, 'execute_agent') as mock_execute:
            mock_execute.side_effect = lambda agent_type, **kwargs: {
                "content": mock_agent_responses.get(
                    agent_type.value, 
                    mock_agent_responses["company_analyst"]
                )["content"],
                "confidence": mock_agent_responses.get(
                    agent_type.value,
                    mock_agent_responses["company_analyst"]
                )["confidence"]
            }
            
            # Initialize use case
            use_case = AnalyzeStockUseCase(
                stock_repository=stock_repo,
                session_repository=session_repo,
                agent_analysis_repository=agent_repo,
                decision_repository=decision_repo,
                agent_service=agent_service,
                analysis_orchestrator=AnalysisOrchestrator()
            )
            
            # Create analysis request
            request = AnalysisRequestDTO(
                ticker="AAPL",
                market="US",
                user_id=str(user.id),
                analysis_period=12
            )
            
            # Execute use case
            result = await use_case.execute(request)
            
            # Verify result
            assert result.session_id is not None
            assert result.stock_info["ticker"] == "AAPL"
            assert len(result.agent_analyses) > 0
            assert result.investment_decision is not None
            assert result.investment_decision["decision"] in ["BUY", "SELL", "HOLD"]
            assert result.analysis_metadata["status"] == AnalysisStatus.COMPLETED.value
    
    async def test_analysis_with_progress_callback(
        self,
        db_session,
        create_test_user,
        create_test_stock
    ):
        """Test analysis with progress callback."""
        from backend.infrastructure.repositories.stock_repository import StockRepository
        from backend.infrastructure.repositories.analysis_session_repository import AnalysisSessionRepository
        from backend.infrastructure.repositories.agent_analysis_repository import AgentAnalysisRepository
        from backend.infrastructure.repositories.investment_decision_repository import InvestmentDecisionRepository
        from backend.application.services.agent_service import AgentService
        from backend.domain.services.analysis_orchestrator import AnalysisOrchestrator
        
        # Create test data
        user = await create_test_user()
        stock = await create_test_stock(ticker="MSFT", name="Microsoft", market="US")
        
        # Track progress
        progress_updates = []
        
        async def progress_callback(message, percent):
            progress_updates.append((message, percent))
        
        # Mock agent service
        agent_service = AgentService()
        with patch.object(agent_service, 'execute_agent') as mock_execute:
            mock_execute.return_value = {
                "content": "Test analysis",
                "confidence": 0.75
            }
            
            # Initialize use case
            use_case = AnalyzeStockUseCase(
                stock_repository=StockRepository(db_session),
                session_repository=AnalysisSessionRepository(db_session),
                agent_analysis_repository=AgentAnalysisRepository(db_session),
                decision_repository=InvestmentDecisionRepository(db_session),
                agent_service=agent_service,
                analysis_orchestrator=AnalysisOrchestrator()
            )
            
            # Create analysis request
            request = AnalysisRequestDTO(
                ticker="MSFT",
                market="US",
                user_id=str(user.id)
            )
            
            # Execute with progress callback
            result = await use_case.execute(request, progress_callback)
            
            # Verify progress was tracked
            assert len(progress_updates) > 0
            assert progress_updates[0][1] == 5  # Session creation
            assert progress_updates[1][1] == 10  # Analysis start
            assert any(p[1] == 100 for p in progress_updates)  # Completion
    
    async def test_analysis_failure_handling(
        self,
        db_session,
        create_test_user
    ):
        """Test handling of analysis failure."""
        from backend.infrastructure.repositories.stock_repository import StockRepository
        from backend.infrastructure.repositories.analysis_session_repository import AnalysisSessionRepository
        from backend.infrastructure.repositories.agent_analysis_repository import AgentAnalysisRepository
        from backend.infrastructure.repositories.investment_decision_repository import InvestmentDecisionRepository
        from backend.application.services.agent_service import AgentService
        from backend.domain.services.analysis_orchestrator import AnalysisOrchestrator
        
        # Create test data
        user = await create_test_user()
        
        # Mock agent service to fail
        agent_service = AgentService()
        with patch.object(agent_service, 'execute_agent') as mock_execute:
            mock_execute.side_effect = Exception("Agent execution failed")
            
            # Initialize use case
            use_case = AnalyzeStockUseCase(
                stock_repository=StockRepository(db_session),
                session_repository=AnalysisSessionRepository(db_session),
                agent_analysis_repository=AgentAnalysisRepository(db_session),
                decision_repository=InvestmentDecisionRepository(db_session),
                agent_service=agent_service,
                analysis_orchestrator=AnalysisOrchestrator()
            )
            
            # Create analysis request
            request = AnalysisRequestDTO(
                ticker="INVALID",
                market="US",
                user_id=str(user.id)
            )
            
            # Execute should raise exception
            with pytest.raises(Exception):
                await use_case.execute(request)


@pytest.mark.asyncio
class TestGetAnalysisResultsUseCase:
    """Test GetAnalysisResultsUseCase."""
    
    async def test_get_existing_analysis_results(
        self,
        db_session,
        create_test_user,
        create_test_stock
    ):
        """Test retrieving existing analysis results."""
        from backend.infrastructure.repositories.analysis_session_repository import AnalysisSessionRepository
        from backend.infrastructure.repositories.agent_analysis_repository import AgentAnalysisRepository
        from backend.infrastructure.repositories.investment_decision_repository import InvestmentDecisionRepository
        from backend.infrastructure.repositories.stock_repository import StockRepository
        from backend.domain.entities.analysis import (
            AnalysisSession, AgentAnalysis, AgentType,
            InvestmentDecision, InvestmentDecisionType, RiskLevel
        )
        
        # Create test data
        user = await create_test_user()
        stock = await create_test_stock(ticker="GOOGL", name="Alphabet", market="US")
        
        # Create analysis session
        session_repo = AnalysisSessionRepository(db_session)
        session = AnalysisSession(
            user_id=user.id,
            stock_id=stock.id,
            analysis_period=12
        )
        session.start_analysis()
        session.complete_analysis()
        saved_session = await session_repo.create_session(session)
        
        # Create agent analyses
        agent_repo = AgentAnalysisRepository(db_session)
        for agent_type in [AgentType.COMPANY_ANALYST, AgentType.TECHNICAL_ANALYST]:
            analysis = AgentAnalysis(
                session_id=saved_session.id,
                agent_type=agent_type,
                analysis_result=f"Analysis by {agent_type.value}",
                confidence_score=0.80,
                execution_time_ms=1200
            )
            await agent_repo.create_analysis(analysis)
        
        # Create investment decision
        decision_repo = InvestmentDecisionRepository(db_session)
        decision = InvestmentDecision(
            session_id=saved_session.id,
            decision=InvestmentDecisionType.BUY,
            confidence=0.82,
            rationale="Strong buy recommendation",
            risk_level=RiskLevel.MEDIUM
        )
        await decision_repo.create_decision(decision)
        
        # Initialize use case
        use_case = GetAnalysisResultsUseCase(
            session_repository=session_repo,
            agent_analysis_repository=agent_repo,
            decision_repository=decision_repo,
            stock_repository=StockRepository(db_session)
        )
        
        # Get results
        result = await use_case.execute(saved_session.id)
        
        # Verify results
        assert result is not None
        assert result.session_id == saved_session.id
        assert result.stock_info["ticker"] == "GOOGL"
        assert len(result.agent_analyses) == 2
        assert result.investment_decision["decision"] == "BUY"
        assert result.investment_decision["confidence"] == 0.82
        assert result.analysis_metadata["status"] == "completed"
    
    async def test_get_nonexistent_analysis(
        self,
        db_session
    ):
        """Test retrieving non-existent analysis."""
        from backend.infrastructure.repositories.analysis_session_repository import AnalysisSessionRepository
        from backend.infrastructure.repositories.agent_analysis_repository import AgentAnalysisRepository
        from backend.infrastructure.repositories.investment_decision_repository import InvestmentDecisionRepository
        from backend.infrastructure.repositories.stock_repository import StockRepository
        
        # Initialize use case
        use_case = GetAnalysisResultsUseCase(
            session_repository=AnalysisSessionRepository(db_session),
            agent_analysis_repository=AgentAnalysisRepository(db_session),
            decision_repository=InvestmentDecisionRepository(db_session),
            stock_repository=StockRepository(db_session)
        )
        
        # Get results for non-existent session
        result = await use_case.execute(uuid4())
        
        # Should return None
        assert result is None