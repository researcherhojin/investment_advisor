"""
Analysis Orchestrator

Domain service for orchestrating the complete analysis workflow.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from decimal import Decimal

import structlog

from domain.entities.analysis import (
    AnalysisSession,
    AgentAnalysis,
    AgentType,
    InvestmentDecision,
    InvestmentDecisionType,
    RiskLevel
)
from domain.entities.stock import Stock

logger = structlog.get_logger(__name__)


class AnalysisOrchestrator:
    """
    Orchestrates the complete investment analysis workflow.
    
    Coordinates multiple AI agents and consolidates their findings
    into a final investment decision.
    """
    
    def __init__(self):
        # Agent execution order (excluding mediator)
        self.agent_order = [
            AgentType.COMPANY_ANALYST,
            AgentType.INDUSTRY_EXPERT,
            AgentType.MACROECONOMIST,
            AgentType.TECHNICAL_ANALYST,
            AgentType.RISK_MANAGER,
        ]
    
    async def orchestrate_analysis(
        self,
        session: AnalysisSession,
        stock: Stock,
        agent_executor_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> Dict[AgentType, AgentAnalysis]:
        """
        Orchestrate the complete analysis workflow.
        
        Args:
            session: Analysis session
            stock: Stock to analyze
            agent_executor_func: Function to execute individual agents
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary mapping agent types to their analysis results
        """
        logger.info(
            "Starting analysis orchestration",
            session_id=session.id,
            stock_ticker=stock.ticker
        )
        
        agent_analyses = {}
        total_agents = len(self.agent_order) + 1  # +1 for mediator
        
        # Execute individual agents
        for i, agent_type in enumerate(self.agent_order):
            try:
                if progress_callback:
                    progress_percent = int((i / total_agents) * 80) + 10
                    await progress_callback(
                        f"{agent_type.value} 분석 중...",
                        progress_percent
                    )
                
                # Execute agent
                start_time = datetime.utcnow()
                result = await agent_executor_func(
                    agent_type=agent_type,
                    stock=stock,
                    session=session
                )
                execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Create agent analysis entity
                agent_analysis = AgentAnalysis(
                    session_id=session.id,
                    agent_type=agent_type,
                    analysis_result=result.get("content", ""),
                    confidence_score=Decimal(str(result.get("confidence", 0.7))),
                    execution_time_ms=execution_time_ms,
                    metadata=result
                )
                
                agent_analyses[agent_type] = agent_analysis
                
                logger.info(
                    "Agent analysis completed",
                    agent_type=agent_type.value,
                    confidence=agent_analysis.confidence_score,
                    execution_time_ms=execution_time_ms
                )
                
            except Exception as e:
                logger.error(
                    "Agent execution failed",
                    agent_type=agent_type.value,
                    error=str(e),
                    exc_info=e
                )
                # Continue with other agents
        
        # Execute mediator agent with all results
        if progress_callback:
            await progress_callback("종합 분석 중재자 실행 중...", 90)
        
        try:
            # Prepare agent analyses for mediator
            agent_analyses_content = {
                agent_type.value: analysis.analysis_result
                for agent_type, analysis in agent_analyses.items()
            }
            
            # Execute mediator
            mediator_result = await agent_executor_func(
                agent_type=AgentType.MEDIATOR,
                stock=stock,
                session=session,
                additional_context={"agent_analyses": agent_analyses_content}
            )
            
            # Create mediator analysis
            mediator_analysis = AgentAnalysis(
                session_id=session.id,
                agent_type=AgentType.MEDIATOR,
                analysis_result=mediator_result.get("content", ""),
                confidence_score=Decimal(str(mediator_result.get("confidence", 0.8))),
                execution_time_ms=mediator_result.get("execution_time_ms", 0),
                metadata=mediator_result
            )
            
            agent_analyses[AgentType.MEDIATOR] = mediator_analysis
            
        except Exception as e:
            logger.error(
                "Mediator execution failed",
                error=str(e),
                exc_info=e
            )
        
        return agent_analyses
    
    def consolidate_decision(
        self,
        agent_analyses: Dict[AgentType, AgentAnalysis],
        current_price: Optional[float] = None
    ) -> InvestmentDecision:
        """
        Consolidate agent analyses into final investment decision.
        
        Args:
            agent_analyses: Dictionary of agent analyses
            current_price: Current stock price
            
        Returns:
            Final investment decision
        """
        # Get mediator analysis if available
        mediator_analysis = agent_analyses.get(AgentType.MEDIATOR)
        
        # If mediator succeeded, use its decision
        if mediator_analysis:
            decision = self._parse_mediator_decision(mediator_analysis)
        else:
            # Fallback: aggregate individual agent opinions
            decision = self._aggregate_agent_decisions(agent_analyses)
        
        # Add session ID
        decision.session_id = agent_analyses[next(iter(agent_analyses))].session_id
        
        return decision
    
    def _parse_mediator_decision(self, mediator_analysis: AgentAnalysis) -> InvestmentDecision:
        """Parse investment decision from mediator analysis."""
        content = mediator_analysis.analysis_result.lower()
        
        # Extract decision type
        if "매수" in content or "buy" in content:
            decision_type = InvestmentDecisionType.BUY
        elif "매도" in content or "sell" in content:
            decision_type = InvestmentDecisionType.SELL
        else:
            decision_type = InvestmentDecisionType.HOLD
        
        # Extract confidence (use mediator's confidence)
        confidence = mediator_analysis.confidence_score
        
        # Extract risk level
        risk_level = RiskLevel.MEDIUM  # Default
        if "높은 위험" in content or "high risk" in content:
            risk_level = RiskLevel.HIGH
        elif "낮은 위험" in content or "low risk" in content:
            risk_level = RiskLevel.LOW
        
        # Create decision
        return InvestmentDecision(
            decision=decision_type,
            confidence=confidence,
            rationale=mediator_analysis.analysis_result,
            time_horizon="3-6개월",
            risk_level=risk_level
        )
    
    def _aggregate_agent_decisions(
        self,
        agent_analyses: Dict[AgentType, AgentAnalysis]
    ) -> InvestmentDecision:
        """Aggregate individual agent decisions (fallback method)."""
        # Count recommendations
        buy_count = 0
        sell_count = 0
        hold_count = 0
        total_confidence = Decimal("0")
        
        for agent_type, analysis in agent_analyses.items():
            if agent_type == AgentType.MEDIATOR:
                continue
            
            content = analysis.analysis_result.lower()
            if "매수" in content or "buy" in content:
                buy_count += 1
            elif "매도" in content or "sell" in content:
                sell_count += 1
            else:
                hold_count += 1
            
            total_confidence += analysis.confidence_score or Decimal("0.5")
        
        # Determine decision
        if buy_count > sell_count and buy_count > hold_count:
            decision_type = InvestmentDecisionType.BUY
        elif sell_count > buy_count and sell_count > hold_count:
            decision_type = InvestmentDecisionType.SELL
        else:
            decision_type = InvestmentDecisionType.HOLD
        
        # Average confidence
        agent_count = len(agent_analyses) - (1 if AgentType.MEDIATOR in agent_analyses else 0)
        avg_confidence = total_confidence / agent_count if agent_count > 0 else Decimal("0.5")
        
        # Create rationale
        rationale = f"""
        종합 분석 결과:
        - 매수 의견: {buy_count}개
        - 매도 의견: {sell_count}개
        - 보유 의견: {hold_count}개
        
        최종 결정: {decision_type.value}
        """
        
        return InvestmentDecision(
            decision=decision_type,
            confidence=avg_confidence,
            rationale=rationale,
            time_horizon="3-6개월",
            risk_level=RiskLevel.MEDIUM
        )