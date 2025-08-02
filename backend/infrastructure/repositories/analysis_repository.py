"""
Analysis Repository

Repository for analysis-related database operations.
"""

from typing import Optional, List, Type, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload
import structlog

from .base import BaseRepository
from backend.infrastructure.database.models import Analysis, AnalysisStatus, Market

logger = structlog.get_logger(__name__)


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for analysis operations."""
    
    @property
    def model_class(self) -> Type[Analysis]:
        return Analysis
    
    async def get_user_analyses(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[AnalysisStatus] = None
    ) -> List[Analysis]:
        """Get analyses for a specific user."""
        try:
            query = (
                select(Analysis)
                .where(Analysis.user_id == user_id)
                .options(
                    selectinload(Analysis.stock),
                    selectinload(Analysis.user)
                )
                .order_by(Analysis.created_at.desc())
            )
            
            if status:
                query = query.where(Analysis.status == status)
            
            query = query.offset(skip).limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error("Error getting user analyses", user_id=user_id, error=str(e))
            raise
    
    async def get_recent_by_stock(
        self,
        stock_id: UUID,
        hours: int = 24
    ) -> Optional[Analysis]:
        """Get most recent analysis for a stock within specified hours."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = (
                select(Analysis)
                .where(
                    and_(
                        Analysis.stock_id == stock_id,
                        Analysis.status == AnalysisStatus.COMPLETED,
                        Analysis.created_at >= cutoff_time
                    )
                )
                .order_by(Analysis.created_at.desc())
                .limit(1)
            )
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting recent analysis", stock_id=stock_id, error=str(e))
            raise
    
    async def get_statistics(
        self,
        user_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analysis statistics."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            query = select(
                func.count(Analysis.id).label("total"),
                func.count(
                    case(
                        (Analysis.status == AnalysisStatus.COMPLETED, 1),
                        else_=None
                    )
                ).label("completed"),
                func.count(
                    case(
                        (Analysis.status == AnalysisStatus.FAILED, 1),
                        else_=None
                    )
                ).label("failed"),
                func.avg(
                    case(
                        (Analysis.status == AnalysisStatus.COMPLETED, Analysis.confidence_score),
                        else_=None
                    )
                ).label("avg_confidence")
            ).where(Analysis.created_at >= cutoff_date)
            
            if user_id:
                query = query.where(Analysis.user_id == user_id)
            
            result = await self.session.execute(query)
            row = result.one()
            
            return {
                "total": row.total or 0,
                "completed": row.completed or 0,
                "failed": row.failed or 0,
                "success_rate": (row.completed / row.total * 100) if row.total > 0 else 0,
                "avg_confidence": float(row.avg_confidence) if row.avg_confidence else 0
            }
        except Exception as e:
            logger.error("Error getting analysis statistics", error=str(e))
            raise
    
    async def get_top_decisions(
        self,
        market: Optional[Market] = None,
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get top investment decisions by confidence."""
        try:
            from backend.infrastructure.database.models import Stock
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = (
                select(
                    Analysis.id,
                    Analysis.final_decision,
                    Analysis.confidence_score,
                    Analysis.target_price,
                    Analysis.created_at,
                    Stock.ticker,
                    Stock.name,
                    Stock.market
                )
                .join(Stock, Analysis.stock_id == Stock.id)
                .where(
                    and_(
                        Analysis.status == AnalysisStatus.COMPLETED,
                        Analysis.created_at >= cutoff_date,
                        Analysis.confidence_score.isnot(None)
                    )
                )
                .order_by(Analysis.confidence_score.desc())
            )
            
            if market:
                query = query.where(Stock.market == market)
            
            query = query.limit(limit)
            
            result = await self.session.execute(query)
            
            return [
                {
                    "id": row.id,
                    "ticker": row.ticker,
                    "name": row.name,
                    "market": row.market,
                    "decision": row.final_decision,
                    "confidence": row.confidence_score,
                    "target_price": row.target_price,
                    "created_at": row.created_at
                }
                for row in result
            ]
        except Exception as e:
            logger.error("Error getting top decisions", error=str(e))
            raise
    
    async def cleanup_old_analyses(
        self,
        days: int = 90
    ) -> int:
        """Clean up old analyses."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old pending/failed analyses
            from sqlalchemy import delete
            
            stmt = delete(Analysis).where(
                and_(
                    Analysis.created_at < cutoff_date,
                    Analysis.status.in_([AnalysisStatus.PENDING, AnalysisStatus.FAILED])
                )
            )
            
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            return result.rowcount
        except Exception as e:
            logger.error("Error cleaning up analyses", error=str(e))
            raise