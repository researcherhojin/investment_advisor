"""
Analysis Session Repository

Repository for analysis session database operations.
"""

from typing import List, Optional, Type
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import structlog

from .base import BaseRepository
from domain.entities.analysis import AnalysisSession, AnalysisStatus
from backend.infrastructure.database.models import AnalysisSession as AnalysisSessionModel

logger = structlog.get_logger(__name__)


class AnalysisSessionRepository(BaseRepository[AnalysisSessionModel]):
    """Repository for analysis session operations."""
    
    @property
    def model_class(self) -> Type[AnalysisSessionModel]:
        return AnalysisSessionModel
    
    async def create_session(self, session: AnalysisSession) -> AnalysisSession:
        """Create new analysis session."""
        try:
            # Convert domain entity to model
            model = AnalysisSessionModel(
                user_id=session.user_id,
                stock_id=session.stock_id,
                analysis_period=session.analysis_period,
                status=session.status,
                session_data=session.session_data
            )
            
            # Save to database
            saved_model = await self.create(model)
            
            # Convert back to domain entity
            return self._to_domain_entity(saved_model)
            
        except Exception as e:
            logger.error("Error creating analysis session", error=str(e))
            raise
    
    async def get_session_by_id(self, session_id: UUID) -> Optional[AnalysisSession]:
        """Get session by ID."""
        model = await self.get_by_id(session_id)
        return self._to_domain_entity(model) if model else None
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        status: Optional[AnalysisStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[AnalysisSession]:
        """Get sessions for a specific user."""
        try:
            query = (
                select(AnalysisSessionModel)
                .where(AnalysisSessionModel.user_id == user_id)
                .order_by(AnalysisSessionModel.created_at.desc())
            )
            
            if status:
                query = query.where(AnalysisSessionModel.status == status)
            
            query = query.offset(skip).limit(limit)
            
            result = await self.session.execute(query)
            models = result.scalars().all()
            
            return [self._to_domain_entity(model) for model in models]
            
        except Exception as e:
            logger.error("Error getting user sessions", user_id=user_id, error=str(e))
            raise
    
    async def update_session(self, session: AnalysisSession) -> AnalysisSession:
        """Update analysis session."""
        try:
            updates = {
                "status": session.status,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
                "error_message": session.error_message,
                "session_data": session.session_data
            }
            
            updated_model = await self.update(session.id, updates)
            return self._to_domain_entity(updated_model) if updated_model else session
            
        except Exception as e:
            logger.error("Error updating session", session_id=session.id, error=str(e))
            raise
    
    async def get_active_sessions(self) -> List[AnalysisSession]:
        """Get all active (running) sessions."""
        try:
            query = (
                select(AnalysisSessionModel)
                .where(AnalysisSessionModel.status == AnalysisStatus.RUNNING)
                .order_by(AnalysisSessionModel.started_at)
            )
            
            result = await self.session.execute(query)
            models = result.scalars().all()
            
            return [self._to_domain_entity(model) for model in models]
            
        except Exception as e:
            logger.error("Error getting active sessions", error=str(e))
            raise
    
    async def cleanup_stale_sessions(self, timeout_hours: int = 24) -> int:
        """Clean up stale running sessions."""
        try:
            from sqlalchemy import update
            cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
            
            stmt = (
                update(AnalysisSessionModel)
                .where(
                    and_(
                        AnalysisSessionModel.status == AnalysisStatus.RUNNING,
                        AnalysisSessionModel.started_at < cutoff_time
                    )
                )
                .values(
                    status=AnalysisStatus.FAILED,
                    error_message="Session timeout",
                    completed_at=datetime.utcnow()
                )
            )
            
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            return result.rowcount
            
        except Exception as e:
            logger.error("Error cleaning up stale sessions", error=str(e))
            raise
    
    def _to_domain_entity(self, model: AnalysisSessionModel) -> AnalysisSession:
        """Convert database model to domain entity."""
        session = AnalysisSession(
            user_id=model.user_id,
            stock_id=model.stock_id,
            analysis_period=model.analysis_period,
            session_data=model.session_data
        )
        
        # Set properties that aren't in constructor
        session.id = model.id
        session.status = model.status
        session.started_at = model.started_at
        session.completed_at = model.completed_at
        session.error_message = model.error_message
        session.created_at = model.created_at
        session.updated_at = model.updated_at
        
        return session