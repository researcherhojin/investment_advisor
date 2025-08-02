"""
Tests for Streamlit Agent Adapter

Test the adapter that bridges Streamlit agents to FastAPI.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from backend.application.services.streamlit_agent_adapter import StreamlitAgentAdapter


@pytest.mark.asyncio
class TestStreamlitAgentAdapter:
    """Test StreamlitAgentAdapter functionality."""
    
    async def test_execute_agent_success(self):
        """Test successful agent execution."""
        adapter = StreamlitAgentAdapter()
        
        # Mock the Streamlit agent
        with patch('backend.application.services.streamlit_agent_adapter.CompanyAnalystAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run.return_value = "회사의 재무 상태가 매우 양호하며, 강력한 매수 신호입니다."
            mock_agent_class.return_value = mock_agent
            
            result = await adapter.execute_agent(
                agent_type="company_analyst",
                ticker="AAPL",
                industry="Technology",
                market="미국장"
            )
            
            assert result["success"] is True
            assert result["agent_type"] == "company_analyst"
            assert result["ticker"] == "AAPL"
            assert "재무 상태가 매우 양호" in result["content"]
            assert result["confidence"] > 0
            assert result["recommendation"] in ["BUY", "SELL", "HOLD"]
    
    async def test_execute_agent_with_additional_context(self):
        """Test agent execution with additional context."""
        adapter = StreamlitAgentAdapter()
        
        with patch('backend.application.services.streamlit_agent_adapter.MediatorAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run.return_value = "종합 분석 결과, 보유를 권장합니다."
            mock_agent_class.return_value = mock_agent
            
            additional_context = {
                "agent_analyses": {
                    "company_analyst": "긍정적",
                    "technical_analyst": "중립적"
                }
            }
            
            result = await adapter.execute_agent(
                agent_type="mediator",
                ticker="MSFT",
                industry="Software",
                market="미국장",
                additional_context=additional_context
            )
            
            # Verify agent was called with merged context
            call_args = mock_agent.run.call_args[0][0]
            assert "agent_analyses" in call_args
            assert call_args["ticker"] == "MSFT"
    
    async def test_execute_unknown_agent_type(self):
        """Test executing unknown agent type."""
        adapter = StreamlitAgentAdapter()
        
        result = await adapter.execute_agent(
            agent_type="unknown_agent",
            ticker="AAPL",
            industry="Technology",
            market="미국장"
        )
        
        assert result["success"] is False
        assert "Unknown agent type" in result["error"]
    
    async def test_execute_agent_failure(self):
        """Test handling agent execution failure."""
        adapter = StreamlitAgentAdapter()
        
        with patch('backend.application.services.streamlit_agent_adapter.TechnicalAnalystAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run.side_effect = Exception("Agent failed")
            mock_agent_class.return_value = mock_agent
            
            result = await adapter.execute_agent(
                agent_type="technical_analyst",
                ticker="TSLA",
                industry="Automotive",
                market="미국장"
            )
            
            assert result["success"] is False
            assert "Agent failed" in result["error"]
            assert result["agent_type"] == "technical_analyst"
    
    async def test_confidence_extraction(self):
        """Test confidence score extraction from agent results."""
        adapter = StreamlitAgentAdapter()
        
        test_cases = [
            ("강력히 추천합니다. 확실한 매수 기회입니다.", 0.8),  # High confidence
            ("불확실한 상황입니다. 리스크가 높습니다.", 0.3),     # Low confidence
            ("일반적인 분석 결과입니다.", 0.6),                    # Default confidence
        ]
        
        for content, expected_min in test_cases:
            confidence = adapter._extract_confidence(content)
            assert confidence >= Decimal(str(expected_min))
    
    async def test_recommendation_extraction(self):
        """Test investment recommendation extraction."""
        adapter = StreamlitAgentAdapter()
        
        test_cases = [
            ("매수 추천합니다. 긍정적 전망", "BUY"),
            ("매도를 권고합니다. 부정적 신호", "SELL"),
            ("현재 보유 유지하시기 바랍니다.", "HOLD"),
            ("중립적인 상황입니다.", "HOLD"),  # Default to HOLD
        ]
        
        for content, expected in test_cases:
            recommendation = adapter._extract_recommendation(content)
            assert recommendation == expected
    
    async def test_execute_all_agents(self):
        """Test executing all agents in parallel."""
        adapter = StreamlitAgentAdapter()
        
        # Mock all agent classes
        agent_types = ["company_analyst", "industry_expert", "macroeconomist", 
                      "technical_analyst", "risk_manager"]
        
        with patch.multiple(
            'backend.application.services.streamlit_agent_adapter',
            CompanyAnalystAgent=Mock(return_value=Mock(run=Mock(return_value="Company analysis"))),
            IndustryExpertAgent=Mock(return_value=Mock(run=Mock(return_value="Industry analysis"))),
            MacroeconomistAgent=Mock(return_value=Mock(run=Mock(return_value="Macro analysis"))),
            TechnicalAnalystAgent=Mock(return_value=Mock(run=Mock(return_value="Technical analysis"))),
            RiskManagerAgent=Mock(return_value=Mock(run=Mock(return_value="Risk analysis")))
        ):
            results = await adapter.execute_all_agents(
                ticker="NVDA",
                industry="Semiconductors",
                market="미국장"
            )
            
            assert len(results) == len(agent_types)
            for agent_type in agent_types:
                assert agent_type in results
                assert results[agent_type]["success"] is True
                assert results[agent_type]["content"] is not None
    
    async def test_execute_mediator_with_agent_results(self):
        """Test executing mediator with other agents' results."""
        adapter = StreamlitAgentAdapter()
        
        # Prepare agent results
        agent_results = {
            "company_analyst": {
                "success": True,
                "content": "재무 상태 양호, 매수 추천"
            },
            "technical_analyst": {
                "success": True,
                "content": "기술적 지표 긍정적"
            },
            "risk_manager": {
                "success": True,
                "content": "리스크 관리 가능"
            }
        }
        
        with patch('backend.application.services.streamlit_agent_adapter.MediatorAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run.return_value = "종합 분석 결과, 매수를 추천합니다."
            mock_agent_class.return_value = mock_agent
            
            result = await adapter.execute_mediator(
                ticker="AMZN",
                industry="E-commerce",
                market="미국장",
                agent_results=agent_results
            )
            
            assert result["success"] is True
            assert result["agent_type"] == "mediator"
            assert "매수를 추천" in result["content"]
            
            # Verify mediator received agent analyses
            call_args = mock_agent.run.call_args[0][0]
            assert "agent_analyses" in call_args
            assert len(call_args["agent_analyses"]) == 3