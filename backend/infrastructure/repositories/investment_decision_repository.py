"""
Investment Decision Repository

Repository for investment decision database operations.
"""

from typing import Optional, Type, List
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
import structlog

from .base import BaseRepository
from domain.entities.analysis import InvestmentDecision, InvestmentDecisionType, RiskLevel
from backend.infrastructure.database.models import InvestmentDecision as InvestmentDecisionModel

logger = structlog.get_logger(__name__)


class InvestmentDecisionRepository(BaseRepository[InvestmentDecisionModel]):
    """Repository for investment decision operations."""
    
    @property
    def model_class(self) -> Type[InvestmentDecisionModel]:
        return InvestmentDecisionModel
    
    async def create_decision(self, decision: InvestmentDecision) -> InvestmentDecision:
        """Create new investment decision."""
        try:
            # Convert domain entity to model
            model = InvestmentDecisionModel(
                session_id=decision.session_id,
                decision=decision.decision,
                confidence=float(decision.confidence),
                rationale=decision.rationale,
                price_target=float(decision.price_target) if decision.price_target else None,
                stop_loss=float(decision.stop_loss) if decision.stop_loss else None,
                time_horizon=decision.time_horizon,
                risk_level=decision.risk_level,
                key_factors=decision.key_factors,
                risks=decision.risks,
                opportunities=decision.opportunities
            )
            
            # Save to database
            saved_model = await self.create(model)
            
            # Convert back to domain entity
            return self._to_domain_entity(saved_model)
            
        except Exception as e:
            logger.error("Error creating investment decision", error=str(e))
            raise
    
    async def get_session_decision(self, session_id: UUID) -> Optional[InvestmentDecision]:
        """Get investment decision for a session."""
        try:
            query = (
                select(InvestmentDecisionModel)
                .where(InvestmentDecisionModel.session_id == session_id)
                .limit(1)
            )
            
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
            
            return self._to_domain_entity(model) if model else None
            
        except Exception as e:
            logger.error("Error getting session decision", session_id=session_id, error=str(e))
            raise
    
    async def get_recent_decisions(
        self,
        user_id: Optional[UUID] = None,
        stock_id: Optional[UUID] = None,
        decision_type: Optional[InvestmentDecisionType] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[InvestmentDecision]:
        """Get recent investment decisions."""
        try:
            from backend.infrastructure.database.models import AnalysisSession
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = (
                select(InvestmentDecisionModel)
                .join(AnalysisSession, InvestmentDecisionModel.session_id == AnalysisSession.id)
                .where(InvestmentDecisionModel.created_at >= cutoff_date)
                .order_by(InvestmentDecisionModel.created_at.desc())
            )
            
            if user_id:
                query = query.where(AnalysisSession.user_id == user_id)
            
            if stock_id:
                query = query.where(AnalysisSession.stock_id == stock_id)
            
            if decision_type:
                query = query.where(InvestmentDecisionModel.decision == decision_type)
            
            query = query.limit(limit)
            
            result = await self.session.execute(query)
            models = result.scalars().all()
            
            return [self._to_domain_entity(model) for model in models]
            
        except Exception as e:
            logger.error("Error getting recent decisions", error=str(e))
            raise
    
    async def get_decision_statistics(
        self,
        user_id: Optional[UUID] = None,
        days: int = 90
    ) -> dict:
        """Get decision statistics."""
        try:
            from backend.infrastructure.database.models import AnalysisSession
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            query = (
                select(
                    func.count(InvestmentDecisionModel.id).label("total"),
                    func.count(
                        func.case(
                            (InvestmentDecisionModel.decision == InvestmentDecisionType.BUY, 1),
                            else_=None
                        )
                    ).label("buy_count"),
                    func.count(
                        func.case(
                            (InvestmentDecisionModel.decision == InvestmentDecisionType.SELL, 1),
                            else_=None
                        )
                    ).label("sell_count"),
                    func.count(
                        func.case(
                            (InvestmentDecisionModel.decision == InvestmentDecisionType.HOLD, 1),
                            else_=None
                        )
                    ).label("hold_count"),
                    func.avg(InvestmentDecisionModel.confidence).label("avg_confidence")
                )
                .where(InvestmentDecisionModel.created_at >= cutoff_date)
            )
            
            if user_id:
                query = query.join(
                    AnalysisSession, 
                    InvestmentDecisionModel.session_id == AnalysisSession.id
                ).where(AnalysisSession.user_id == user_id)
            
            result = await self.session.execute(query)
            row = result.one()
            
            return {
                "total": row.total or 0,
                "buy_count": row.buy_count or 0,
                "sell_count": row.sell_count or 0,
                "hold_count": row.hold_count or 0,
                "avg_confidence": float(row.avg_confidence) if row.avg_confidence else 0,
                "buy_percentage": (row.buy_count / row.total * 100) if row.total > 0 else 0,
                "sell_percentage": (row.sell_count / row.total * 100) if row.total > 0 else 0,
                "hold_percentage": (row.hold_count / row.total * 100) if row.total > 0 else 0
            }
            
        except Exception as e:
            logger.error("Error getting decision statistics", error=str(e))
            raise
    
    def _to_domain_entity(self, model: InvestmentDecisionModel) -> InvestmentDecision:
        """Convert database model to domain entity."""
        return InvestmentDecision(
            id=model.id,
            session_id=model.session_id,
            decision=model.decision,
            confidence=model.confidence,
            rationale=model.rationale,
            price_target=model.price_target,
            stop_loss=model.stop_loss,
            time_horizon=model.time_horizon,
            risk_level=model.risk_level,
            key_factors=model.key_factors,
            risks=model.risks,
            opportunities=model.opportunities,
            created_at=model.created_at,
            updated_at=model.updated_at
        )