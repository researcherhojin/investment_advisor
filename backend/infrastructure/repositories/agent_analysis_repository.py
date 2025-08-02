"""
Agent Analysis Repository

Repository for agent analysis database operations.
"""

from typing import List, Optional, Type
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
import structlog

from .base import BaseRepository
from domain.entities.analysis import AgentAnalysis, AgentType
from backend.infrastructure.database.models import AgentAnalysis as AgentAnalysisModel

logger = structlog.get_logger(__name__)


class AgentAnalysisRepository(BaseRepository[AgentAnalysisModel]):
    """Repository for agent analysis operations."""
    
    @property
    def model_class(self) -> Type[AgentAnalysisModel]:
        return AgentAnalysisModel
    
    async def create_analysis(self, analysis: AgentAnalysis) -> AgentAnalysis:
        """Create new agent analysis."""
        try:
            # Convert domain entity to model
            model = AgentAnalysisModel(
                session_id=analysis.session_id,
                agent_type=analysis.agent_type,
                analysis_result=analysis.analysis_result,
                confidence_score=float(analysis.confidence_score) if analysis.confidence_score else None,
                execution_time_ms=analysis.execution_time_ms,
                metadata=analysis.metadata
            )
            
            # Save to database
            saved_model = await self.create(model)
            
            # Convert back to domain entity
            return self._to_domain_entity(saved_model)
            
        except Exception as e:
            logger.error("Error creating agent analysis", error=str(e))
            raise
    
    async def get_session_analyses(
        self,
        session_id: UUID,
        agent_type: Optional[AgentType] = None
    ) -> List[AgentAnalysis]:
        """Get all analyses for a session."""
        try:
            query = (
                select(AgentAnalysisModel)
                .where(AgentAnalysisModel.session_id == session_id)
                .order_by(AgentAnalysisModel.created_at)
            )
            
            if agent_type:
                query = query.where(AgentAnalysisModel.agent_type == agent_type)
            
            result = await self.session.execute(query)
            models = result.scalars().all()
            
            return [self._to_domain_entity(model) for model in models]
            
        except Exception as e:
            logger.error("Error getting session analyses", session_id=session_id, error=str(e))
            raise
    
    async def get_analysis_by_id(self, analysis_id: UUID) -> Optional[AgentAnalysis]:
        """Get analysis by ID."""
        model = await self.get_by_id(analysis_id)
        return self._to_domain_entity(model) if model else None
    
    async def update_analysis_result(
        self,
        analysis_id: UUID,
        result: str,
        confidence_score: Optional[float] = None,
        execution_time_ms: Optional[int] = None
    ) -> Optional[AgentAnalysis]:
        """Update analysis result."""
        try:
            updates = {
                "analysis_result": result,
                "execution_time_ms": execution_time_ms
            }
            
            if confidence_score is not None:
                updates["confidence_score"] = confidence_score
            
            updated_model = await self.update(analysis_id, updates)
            return self._to_domain_entity(updated_model) if updated_model else None
            
        except Exception as e:
            logger.error("Error updating analysis result", analysis_id=analysis_id, error=str(e))
            raise
    
    def _to_domain_entity(self, model: AgentAnalysisModel) -> AgentAnalysis:
        """Convert database model to domain entity."""
        return AgentAnalysis(
            id=model.id,
            session_id=model.session_id,
            agent_type=model.agent_type,
            analysis_result=model.analysis_result,
            confidence_score=model.confidence_score,
            execution_time_ms=model.execution_time_ms,
            metadata=model.metadata,
            created_at=model.created_at,
            updated_at=model.updated_at
        )