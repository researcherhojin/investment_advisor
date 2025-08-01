"""
Analyze Stock Use Case

Main use case for performing comprehensive stock analysis using AI agents.
Implements the core business workflow for investment analysis.
"""

import asyncio
from typing import Optional, Callable
from uuid import UUID

import structlog

from domain.entities.analysis import AnalysisSession, AnalysisStatus
from domain.entities.stock import Stock
from domain.services.analysis_orchestrator import AnalysisOrchestrator
from domain.repositories.stock_repository import StockRepository
from domain.repositories.analysis_repository import (
    AnalysisSessionRepository,
    AgentAnalysisRepository,
    InvestmentDecisionRepository
)
from application.services.agent_service import AgentService
from application.dtos.analysis_dto import AnalysisRequestDTO, AnalysisResultDTO

logger = structlog.get_logger(__name__)


class AnalyzeStockUseCase:
    """
    Use case for comprehensive stock analysis.
    
    Orchestrates the complete analysis workflow from session creation
    to final investment decision generation.
    """
    
    def __init__(
        self,
        stock_repository: StockRepository,
        session_repository: AnalysisSessionRepository,
        agent_analysis_repository: AgentAnalysisRepository,
        decision_repository: InvestmentDecisionRepository,
        agent_service: AgentService,
        analysis_orchestrator: AnalysisOrchestrator
    ):
        self.stock_repository = stock_repository
        self.session_repository = session_repository
        self.agent_analysis_repository = agent_analysis_repository
        self.decision_repository = decision_repository
        self.agent_service = agent_service
        self.analysis_orchestrator = analysis_orchestrator
    
    async def execute(
        self,
        request: AnalysisRequestDTO,
        progress_callback: Optional[Callable] = None
    ) -> AnalysisResultDTO:
        """
        Execute comprehensive stock analysis.
        
        Args:
            request: Analysis request containing stock info and parameters
            progress_callback: Optional callback for progress updates
            
        Returns:
            Complete analysis results
        """
        logger.info(
            "Starting stock analysis use case",
            ticker=request.ticker,
            market=request.market,
            user_id=request.user_id
        )
        
        try:
            # 1. Validate and get stock information
            stock = await self._get_or_create_stock(request)
            
            # 2. Create analysis session
            session = await self._create_analysis_session(stock, request)
            
            if progress_callback:
                await progress_callback("분석 세션 생성 완료", 5)
            
            # 3. Start analysis
            session.start_analysis()
            await self.session_repository.update_session(session)
            
            if progress_callback:
                await progress_callback("AI 에이전트 분석 시작", 10)
            
            # 4. Execute AI agent analysis
            agent_analyses = await self.analysis_orchestrator.orchestrate_analysis(
                session=session,
                stock=stock,
                agent_executor_func=self._execute_agent,
                progress_callback=progress_callback
            )
            
            # 5. Save agent analyses
            saved_analyses = {}
            for agent_type, analysis in agent_analyses.items():
                saved_analysis = await self.agent_analysis_repository.create_analysis(analysis)
                saved_analyses[agent_type] = saved_analysis
            
            # 6. Generate final investment decision
            try:
                current_price = await self._get_current_price(stock)
                decision = self.analysis_orchestrator.consolidate_decision(
                    saved_analyses,
                    current_price
                )
                
                # Save decision
                saved_decision = await self.decision_repository.create_decision(decision)
                
            except Exception as e:
                logger.error(
                    "Failed to generate investment decision",
                    session_id=session.id,
                    error=str(e)
                )
                saved_decision = None
            
            # 7. Complete analysis session
            session.complete_analysis()
            await self.session_repository.update_session(session)
            
            if progress_callback:
                await progress_callback("분석 완료", 100)
            
            # 8. Compile results
            result = AnalysisResultDTO(
                session_id=session.id,
                stock_info={
                    "ticker": stock.ticker,
                    "name": stock.name,
                    "market": stock.market,
                    "sector": stock.sector,
                    "industry": stock.industry
                },
                agent_analyses={
                    agent_type.value: {
                        "content": analysis.analysis_result,
                        "confidence": float(analysis.confidence_score or 0),
                        "execution_time_ms": analysis.execution_time_ms
                    }
                    for agent_type, analysis in saved_analyses.items()
                },
                investment_decision={
                    "decision": saved_decision.decision.value,
                    "confidence": float(saved_decision.confidence),
                    "rationale": saved_decision.rationale,
                    "price_target": float(saved_decision.price_target) if saved_decision.price_target else None,
                    "stop_loss": float(saved_decision.stop_loss) if saved_decision.stop_loss else None,
                    "time_horizon": saved_decision.time_horizon,
                    "risk_level": saved_decision.risk_level.value if saved_decision.risk_level else None
                } if saved_decision else None,
                analysis_metadata={
                    "started_at": session.started_at.isoformat(),
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "duration_seconds": session.duration_seconds,
                    "analysis_period_months": session.analysis_period,
                    "total_agents": len(saved_analyses),
                    "successful_agents": len([
                        a for a in saved_analyses.values() 
                        if a.confidence_score is not None
                    ])
                }
            )
            
            logger.info(
                "Stock analysis completed successfully",
                session_id=session.id,
                ticker=stock.ticker,
                duration_seconds=session.duration_seconds,
                decision=saved_decision.decision.value if saved_decision else None
            )
            
            return result
            
        except Exception as e:
            # Handle failure
            if 'session' in locals():
                session.fail_analysis(str(e))
                await self.session_repository.update_session(session)
            
            logger.error(
                "Stock analysis failed",
                ticker=request.ticker,
                market=request.market,
                error=str(e),
                exc_info=e
            )
            raise
    
    async def _get_or_create_stock(self, request: AnalysisRequestDTO) -> Stock:
        """Get existing stock or create new one."""
        # Try to get existing stock
        stock = await self.stock_repository.get_stock_by_ticker(
            request.ticker, 
            request.market
        )
        
        if stock is None:
            # Create new stock record
            stock = Stock(
                ticker=request.ticker,
                name=request.stock_name or request.ticker,
                market=request.market,
                sector=request.sector,
                industry=request.industry
            )
            stock = await self.stock_repository.create_stock(stock)
            
            logger.info(
                "Created new stock record",
                ticker=stock.ticker,
                market=stock.market,
                stock_id=stock.id
            )
        
        return stock
    
    async def _create_analysis_session(
        self, 
        stock: Stock,
        request: AnalysisRequestDTO
    ) -> AnalysisSession:
        """Create new analysis session."""
        session = AnalysisSession(
            user_id=request.user_id,
            stock_id=stock.id,
            analysis_period=request.analysis_period or 12,
            session_data={
                "request_data": request.dict(),
                "created_from": "api_v1"
            }
        )
        
        return await self.session_repository.create_session(session)
    
    async def _execute_agent(self, agent_type, stock, session, additional_context=None):
        """Execute individual agent (wrapper for orchestrator)."""
        return await self.agent_service.execute_agent(
            agent_type=agent_type,
            stock=stock,
            session=session,
            additional_context=additional_context
        )
    
    async def _get_current_price(self, stock: Stock) -> Optional[float]:
        """Get current stock price."""
        try:
            # Get latest price data
            latest_price = await self.stock_repository.get_latest_price(stock.id)
            if latest_price:
                return float(latest_price.close_price)
        except Exception as e:
            logger.warning(
                "Failed to get current stock price",
                stock_id=stock.id,
                ticker=stock.ticker,
                error=str(e)
            )
        
        return None


class GetAnalysisResultsUseCase:
    """Use case for retrieving analysis results."""
    
    def __init__(
        self,
        session_repository: AnalysisSessionRepository,
        agent_analysis_repository: AgentAnalysisRepository,
        decision_repository: InvestmentDecisionRepository,
        stock_repository: StockRepository
    ):
        self.session_repository = session_repository
        self.agent_analysis_repository = agent_analysis_repository
        self.decision_repository = decision_repository
        self.stock_repository = stock_repository
    
    async def execute(self, session_id: UUID) -> Optional[AnalysisResultDTO]:
        """Get analysis results by session ID."""
        # Get session
        session = await self.session_repository.get_session_by_id(session_id)
        if not session:
            return None
        
        # Get stock info
        stock = await self.stock_repository.get_stock_by_id(session.stock_id)
        if not stock:
            return None
        
        # Get agent analyses
        agent_analyses = await self.agent_analysis_repository.get_session_analyses(session_id)
        
        # Get investment decision
        decision = await self.decision_repository.get_session_decision(session_id)
        
        # Compile results
        return AnalysisResultDTO(
            session_id=session.id,
            stock_info={
                "ticker": stock.ticker,
                "name": stock.name,
                "market": stock.market,
                "sector": stock.sector,
                "industry": stock.industry
            },
            agent_analyses={
                analysis.agent_type.value: {
                    "content": analysis.analysis_result,
                    "confidence": float(analysis.confidence_score or 0),
                    "execution_time_ms": analysis.execution_time_ms
                }
                for analysis in agent_analyses
            },
            investment_decision={
                "decision": decision.decision.value,
                "confidence": float(decision.confidence),
                "rationale": decision.rationale,
                "price_target": float(decision.price_target) if decision.price_target else None,
                "stop_loss": float(decision.stop_loss) if decision.stop_loss else None,
                "time_horizon": decision.time_horizon,
                "risk_level": decision.risk_level.value if decision.risk_level else None
            } if decision else None,
            analysis_metadata={
                "started_at": session.started_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "duration_seconds": session.duration_seconds,
                "analysis_period_months": session.analysis_period,
                "status": session.status.value,
                "total_agents": len(agent_analyses),
                "successful_agents": len([
                    a for a in agent_analyses 
                    if a.confidence_score is not None
                ])
            }
        )