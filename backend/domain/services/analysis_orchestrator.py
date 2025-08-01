"""
Analysis Orchestrator Domain Service

Coordinates the execution of multiple AI agents for investment analysis.
This is a domain service that encapsulates complex business logic.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

import structlog

from domain.entities.analysis import (
    AnalysisSession,
    AgentAnalysis,
    InvestmentDecisionEntity,
    AnalysisStatus,
    AgentType,
    InvestmentDecision,
    RiskLevel
)
from domain.entities.stock import Stock

logger = structlog.get_logger(__name__)


class AnalysisOrchestrator:
    """
    Domain service for orchestrating investment analysis.
    
    Coordinates multiple AI agents, manages analysis workflow,
    and consolidates results into final investment decisions.
    """
    
    def __init__(self):
        self.agent_weights = {
            AgentType.COMPANY_ANALYST: Decimal("1.2"),
            AgentType.INDUSTRY_EXPERT: Decimal("1.0"),
            AgentType.MACROECONOMIST: Decimal("0.8"),
            AgentType.TECHNICAL_ANALYST: Decimal("1.1"),
            AgentType.RISK_MANAGER: Decimal("1.3"),
            AgentType.MEDIATOR: Decimal("1.0"),
        }
    
    async def orchestrate_analysis(
        self,
        session: AnalysisSession,
        stock: Stock,
        agent_executor_func,  # Function to execute individual agents
        progress_callback: Optional[callable] = None
    ) -> Dict[AgentType, AgentAnalysis]:
        """
        Orchestrate complete analysis using all available agents.
        
        Args:
            session: Analysis session
            stock: Stock to analyze
            agent_executor_func: Function to execute individual agents
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary of agent analyses
        """
        logger.info(
            "Starting analysis orchestration",
            session_id=session.id,
            stock_ticker=stock.ticker,
            market=stock.market
        )
        
        analyses = {}
        total_agents = len(AgentType) - 1  # Exclude mediator from initial count
        completed = 0
        
        try:
            # Execute agents in parallel where possible
            tasks = []
            
            # Core analysis agents (can run in parallel)
            core_agents = [
                AgentType.COMPANY_ANALYST,
                AgentType.INDUSTRY_EXPERT,
                AgentType.MACROECONOMIST,
                AgentType.TECHNICAL_ANALYST,
                AgentType.RISK_MANAGER,
            ]
            
            for agent_type in core_agents:
                task = asyncio.create_task(
                    self._execute_agent_with_retry(
                        agent_type, session, stock, agent_executor_func
                    )
                )
                tasks.append((agent_type, task))
            
            # Wait for all core agents to complete
            for agent_type, task in tasks:
                try:
                    analysis = await task
                    analyses[agent_type] = analysis
                    completed += 1
                    
                    if progress_callback:
                        progress = int((completed / total_agents) * 90)  # Reserve 10% for mediator
                        await progress_callback(
                            f"{agent_type.value} 분석 완료 ({completed}/{total_agents})",
                            progress
                        )
                    
                    logger.info(
                        "Agent analysis completed",
                        agent_type=agent_type.value,
                        session_id=session.id,
                        confidence=analysis.confidence_score
                    )
                    
                except Exception as e:
                    logger.error(
                        "Agent analysis failed",
                        agent_type=agent_type.value,
                        session_id=session.id,
                        error=str(e)
                    )
                    # Create failed analysis record
                    analyses[agent_type] = self._create_failed_analysis(
                        agent_type, session.id, str(e)
                    )
            
            # Execute mediator with results from other agents
            if analyses:
                try:
                    mediator_analysis = await self._execute_mediator(
                        session, stock, analyses, agent_executor_func
                    )
                    analyses[AgentType.MEDIATOR] = mediator_analysis
                    
                    if progress_callback:
                        await progress_callback("중재자 분석 완료", 100)
                    
                except Exception as e:
                    logger.error(
                        "Mediator analysis failed",
                        session_id=session.id,
                        error=str(e)
                    )
                    analyses[AgentType.MEDIATOR] = self._create_failed_analysis(
                        AgentType.MEDIATOR, session.id, str(e)
                    )
            
            logger.info(
                "Analysis orchestration completed",
                session_id=session.id,
                total_analyses=len(analyses),
                successful_analyses=len([a for a in analyses.values() if a.confidence_score is not None])
            )
            
            return analyses
            
        except Exception as e:
            logger.error(
                "Analysis orchestration failed",
                session_id=session.id,
                error=str(e),
                exc_info=e
            )
            raise
    
    async def _execute_agent_with_retry(
        self,
        agent_type: AgentType,
        session: AnalysisSession,
        stock: Stock,
        agent_executor_func,
        max_retries: int = 2
    ) -> AgentAnalysis:
        """Execute agent with retry logic."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = datetime.utcnow()
                
                # Execute agent
                result = await agent_executor_func(agent_type, stock, session)
                
                execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Create analysis record
                analysis = AgentAnalysis(
                    session_id=session.id,
                    agent_type=agent_type,
                    agent_weight=self.agent_weights.get(agent_type, Decimal("1.0")),
                    analysis_result=result["content"],
                    confidence_score=result.get("confidence", Decimal("0.8")),
                    execution_time_ms=execution_time
                )
                
                logger.debug(
                    "Agent execution successful",
                    agent_type=agent_type.value,
                    attempt=attempt + 1,
                    execution_time_ms=execution_time
                )
                
                return analysis
                
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        "Agent execution failed, retrying",
                        agent_type=agent_type.value,
                        attempt=attempt + 1,
                        wait_time=wait_time,
                        error=str(e)
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        "Agent execution failed after all retries",
                        agent_type=agent_type.value,
                        attempts=max_retries + 1,
                        error=str(e)
                    )
        
        raise last_error
    
    async def _execute_mediator(
        self,
        session: AnalysisSession,
        stock: Stock,
        analyses: Dict[AgentType, AgentAnalysis],
        agent_executor_func
    ) -> AgentAnalysis:
        """Execute mediator agent with consolidated inputs."""
        # Prepare mediator inputs
        mediator_inputs = {
            "stock_info": {
                "ticker": stock.ticker,
                "name": stock.name,
                "market": stock.market,
                "sector": stock.sector,
                "industry": stock.industry
            },
            "agent_analyses": {
                agent_type.value: {
                    "content": analysis.analysis_result,
                    "confidence": float(analysis.confidence_score or 0),
                    "weight": float(analysis.agent_weight)
                }
                for agent_type, analysis in analyses.items()
                if agent_type != AgentType.MEDIATOR
            }
        }
        
        start_time = datetime.utcnow()
        
        # Execute mediator
        result = await agent_executor_func(AgentType.MEDIATOR, stock, session, mediator_inputs)
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return AgentAnalysis(
            session_id=session.id,
            agent_type=AgentType.MEDIATOR,
            agent_weight=self.agent_weights[AgentType.MEDIATOR],
            analysis_result=result["content"],
            confidence_score=result.get("confidence", Decimal("0.8")),
            execution_time_ms=execution_time
        )
    
    def _create_failed_analysis(
        self,
        agent_type: AgentType,
        session_id: UUID,
        error_message: str
    ) -> AgentAnalysis:
        """Create a failed analysis record."""
        return AgentAnalysis(
            session_id=session_id,
            agent_type=agent_type,
            agent_weight=self.agent_weights.get(agent_type, Decimal("1.0")),
            analysis_result=f"분석 실패: {error_message}",
            confidence_score=None,
            execution_time_ms=None
        )
    
    def consolidate_decision(
        self,
        analyses: Dict[AgentType, AgentAnalysis],
        current_price: Optional[Decimal] = None
    ) -> InvestmentDecisionEntity:
        """
        Consolidate agent analyses into final investment decision.
        
        This implements the business logic for decision making based on
        weighted agent opinions and confidence scores.
        """
        if AgentType.MEDIATOR not in analyses:
            raise ValueError("Mediator analysis is required for decision consolidation")
        
        mediator_analysis = analyses[AgentType.MEDIATOR]
        
        # Extract decision from mediator analysis
        decision_text = mediator_analysis.analysis_result.lower()
        
        # Simple decision extraction logic (can be enhanced with NLP)
        if any(word in decision_text for word in ["매수", "buy", "구매"]):
            decision = InvestmentDecision.BUY
        elif any(word in decision_text for word in ["매도", "sell", "판매"]):
            decision = InvestmentDecision.SELL
        else:
            decision = InvestmentDecision.HOLD
        
        # Calculate overall confidence
        valid_analyses = [
            a for a in analyses.values() 
            if a.confidence_score is not None and a.agent_type != AgentType.MEDIATOR
        ]
        
        if valid_analyses:
            # Weighted average confidence
            total_weight = sum(a.agent_weight for a in valid_analyses)
            weighted_confidence = sum(
                a.confidence_score * a.agent_weight 
                for a in valid_analyses
            ) / total_weight
        else:
            weighted_confidence = mediator_analysis.confidence_score or Decimal("0.5")
        
        # Determine risk level based on analyses
        risk_analysis = analyses.get(AgentType.RISK_MANAGER)
        if risk_analysis and risk_analysis.confidence_score:
            if risk_analysis.confidence_score >= Decimal("0.8"):
                risk_level = RiskLevel.LOW
            elif risk_analysis.confidence_score >= Decimal("0.5"):
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.MEDIUM
        
        return InvestmentDecisionEntity(
            session_id=mediator_analysis.session_id,
            decision=decision,
            confidence=min(weighted_confidence, Decimal("1.0")),
            rationale=mediator_analysis.analysis_result,
            price_target=self._extract_price_target(mediator_analysis.analysis_result),
            stop_loss=self._extract_stop_loss(mediator_analysis.analysis_result),
            time_horizon=self._extract_time_horizon(mediator_analysis.analysis_result),
            risk_level=risk_level
        )
    
    def _extract_price_target(self, analysis_text: str) -> Optional[Decimal]:
        """Extract price target from analysis text."""
        # Simple regex-based extraction (can be enhanced)
        import re
        
        # Look for patterns like "목표가 $150", "target price 150", etc.
        patterns = [
            r"목표가[:\s]*\$?([0-9,]+\.?[0-9]*)",
            r"target price[:\s]*\$?([0-9,]+\.?[0-9]*)",
            r"price target[:\s]*\$?([0-9,]+\.?[0-9]*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(",", "")
                    return Decimal(price_str)
                except:
                    continue
        
        return None
    
    def _extract_stop_loss(self, analysis_text: str) -> Optional[Decimal]:
        """Extract stop loss from analysis text."""
        import re
        
        patterns = [
            r"손절[:\s]*\$?([0-9,]+\.?[0-9]*)",
            r"stop loss[:\s]*\$?([0-9,]+\.?[0-9]*)",
            r"스톱로스[:\s]*\$?([0-9,]+\.?[0-9]*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(",", "")
                    return Decimal(price_str)
                except:
                    continue
        
        return None
    
    def _extract_time_horizon(self, analysis_text: str) -> Optional[str]:
        """Extract time horizon from analysis text."""
        import re
        
        # Look for time-related terms
        time_patterns = {
            r"단기": "단기 (1-3개월)",
            r"중기": "중기 (3-12개월)", 
            r"장기": "장기 (1년 이상)",
            r"short.?term": "단기 (1-3개월)",
            r"medium.?term": "중기 (3-12개월)",
            r"long.?term": "장기 (1년 이상)",
            r"([0-9]+)\s*개월": lambda m: f"{m.group(1)}개월",
            r"([0-9]+)\s*months?": lambda m: f"{m.group(1)}개월"
        }
        
        for pattern, replacement in time_patterns.items():
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                if callable(replacement):
                    return replacement(match)
                return replacement
        
        return None