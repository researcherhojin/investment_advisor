"""
Streamlit Agent Adapter

Adapter to use existing Streamlit AI agents in FastAPI backend.
This allows gradual migration while maintaining functionality.
"""

import sys
import os
from typing import Dict, Any, Optional, Type
from datetime import datetime
from decimal import Decimal
import asyncio
from concurrent.futures import ThreadPoolExecutor

import structlog

# Add parent directory to path to import Streamlit agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from investment_advisor.agents import (
    CompanyAnalystAgent,
    IndustryExpertAgent,
    MacroeconomistAgent,
    TechnicalAnalystAgent,
    RiskManagerAgent,
    MediatorAgent
)
from investment_advisor.agents.base import InvestmentAgent

logger = structlog.get_logger(__name__)


class StreamlitAgentAdapter:
    """
    Adapter to use existing Streamlit agents in FastAPI backend.
    
    This adapter wraps the synchronous Streamlit agents to work
    asynchronously in the FastAPI environment.
    """
    
    def __init__(self):
        # Map agent types to Streamlit agent classes
        self.agent_map = {
            "company_analyst": CompanyAnalystAgent,
            "industry_expert": IndustryExpertAgent,
            "macroeconomist": MacroeconomistAgent,
            "technical_analyst": TechnicalAnalystAgent,
            "risk_manager": RiskManagerAgent,
            "mediator": MediatorAgent,
        }
        
        # Thread pool for running synchronous agents
        self.executor = ThreadPoolExecutor(max_workers=6)
    
    async def execute_agent(
        self,
        agent_type: str,
        ticker: str,
        industry: str,
        market: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a Streamlit agent asynchronously.
        
        Args:
            agent_type: Type of agent to execute
            ticker: Stock ticker
            industry: Industry classification
            market: Market (미국장/한국장)
            additional_context: Additional context data
            
        Returns:
            Dictionary containing agent result
        """
        logger.info(
            "Executing Streamlit agent",
            agent_type=agent_type,
            ticker=ticker,
            market=market
        )
        
        try:
            # Get agent class
            agent_class = self._get_agent_class(agent_type)
            
            # Run agent in thread pool
            result = await self._run_agent_async(
                agent_class,
                ticker,
                industry,
                market,
                additional_context
            )
            
            # Process result
            processed_result = self._process_agent_result(
                result,
                agent_type,
                ticker
            )
            
            logger.info(
                "Streamlit agent execution completed",
                agent_type=agent_type,
                ticker=ticker,
                success=processed_result.get("success", False)
            )
            
            return processed_result
            
        except Exception as e:
            logger.error(
                "Streamlit agent execution failed",
                agent_type=agent_type,
                ticker=ticker,
                error=str(e),
                exc_info=e
            )
            
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type,
                "ticker": ticker,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_agent_class(self, agent_type: str) -> Type[InvestmentAgent]:
        """Get agent class by type."""
        agent_class = self.agent_map.get(agent_type)
        
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return agent_class
    
    async def _run_agent_async(
        self,
        agent_class: Type[InvestmentAgent],
        ticker: str,
        industry: str,
        market: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Run synchronous agent in thread pool."""
        loop = asyncio.get_event_loop()
        
        # Create agent instance
        agent = agent_class()
        
        # Prepare input data
        input_data = {
            "ticker": ticker,
            "industry": industry,
            "market": market
        }
        
        # Add additional context if provided
        if additional_context:
            input_data.update(additional_context)
        
        # Run agent in thread pool
        result = await loop.run_in_executor(
            self.executor,
            agent.run,
            input_data
        )
        
        return result
    
    def _process_agent_result(
        self,
        raw_result: str,
        agent_type: str,
        ticker: str
    ) -> Dict[str, Any]:
        """Process raw agent result into structured format."""
        # Check if result is valid
        if not raw_result or not isinstance(raw_result, str):
            return {
                "success": False,
                "error": "Invalid agent result",
                "agent_type": agent_type,
                "ticker": ticker,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Extract confidence score (simplified)
        confidence = self._extract_confidence(raw_result)
        
        # Determine recommendation
        recommendation = self._extract_recommendation(raw_result)
        
        return {
            "success": True,
            "agent_type": agent_type,
            "ticker": ticker,
            "content": raw_result.strip(),
            "confidence": float(confidence),
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat(),
            "word_count": len(raw_result.split()),
            "source": "streamlit_agent"
        }
    
    def _extract_confidence(self, content: str) -> Decimal:
        """Extract confidence score from agent result."""
        # Simple heuristic based on content
        content_lower = content.lower()
        
        # High confidence indicators
        high_confidence_keywords = [
            "강력히 추천", "확실한", "명확한", "뚜렷한",
            "strongly recommend", "clear", "definite"
        ]
        
        # Low confidence indicators
        low_confidence_keywords = [
            "불확실", "리스크가 높", "주의 필요", "신중",
            "uncertain", "risky", "caution"
        ]
        
        high_count = sum(1 for keyword in high_confidence_keywords if keyword in content_lower)
        low_count = sum(1 for keyword in low_confidence_keywords if keyword in content_lower)
        
        # Calculate base confidence
        if high_count > low_count:
            base_confidence = 0.7 + (0.1 * min(high_count, 3))
        elif low_count > high_count:
            base_confidence = 0.5 - (0.1 * min(low_count, 3))
        else:
            base_confidence = 0.6
        
        # Adjust for content length
        word_count = len(content.split())
        if word_count > 500:
            base_confidence += 0.05
        elif word_count < 100:
            base_confidence -= 0.05
        
        # Ensure within bounds
        confidence = max(0.1, min(1.0, base_confidence))
        
        return Decimal(str(round(confidence, 2)))
    
    def _extract_recommendation(self, content: str) -> str:
        """Extract investment recommendation from agent result."""
        content_lower = content.lower()
        
        # Buy indicators
        buy_keywords = [
            "매수 추천", "매수를 권", "buy", "구매 추천",
            "긍정적", "상승 전망", "투자 가치"
        ]
        
        # Sell indicators
        sell_keywords = [
            "매도 추천", "매도를 권", "sell", "처분",
            "부정적", "하락 전망", "위험"
        ]
        
        # Hold indicators
        hold_keywords = [
            "보유", "관망", "hold", "중립",
            "현상 유지", "추가 관찰"
        ]
        
        buy_count = sum(1 for keyword in buy_keywords if keyword in content_lower)
        sell_count = sum(1 for keyword in sell_keywords if keyword in content_lower)
        hold_count = sum(1 for keyword in hold_keywords if keyword in content_lower)
        
        # Determine recommendation
        if buy_count > sell_count and buy_count > hold_count:
            return "BUY"
        elif sell_count > buy_count and sell_count > hold_count:
            return "SELL"
        else:
            return "HOLD"
    
    async def execute_all_agents(
        self,
        ticker: str,
        industry: str,
        market: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute all agents (except mediator) in parallel.
        
        Returns:
            Dictionary mapping agent type to result
        """
        # Agents to execute (excluding mediator)
        agent_types = [
            "company_analyst",
            "industry_expert",
            "macroeconomist",
            "technical_analyst",
            "risk_manager"
        ]
        
        # Execute agents in parallel
        tasks = [
            self.execute_agent(agent_type, ticker, industry, market, additional_context)
            for agent_type in agent_types
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Map results to agent types
        agent_results = {}
        for agent_type, result in zip(agent_types, results):
            agent_results[agent_type] = result
        
        return agent_results
    
    async def execute_mediator(
        self,
        ticker: str,
        industry: str,
        market: str,
        agent_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute mediator agent with other agents' results.
        
        Args:
            ticker: Stock ticker
            industry: Industry classification
            market: Market type
            agent_results: Results from other agents
            
        Returns:
            Mediator's final decision
        """
        # Prepare agent analyses for mediator
        agent_analyses = {}
        for agent_type, result in agent_results.items():
            if result.get("success") and result.get("content"):
                agent_analyses[agent_type] = result["content"]
        
        # Additional context for mediator
        additional_context = {
            "agent_analyses": agent_analyses
        }
        
        # Execute mediator
        return await self.execute_agent(
            "mediator",
            ticker,
            industry,
            market,
            additional_context
        )
    
    def cleanup(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)