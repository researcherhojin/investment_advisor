"""
Analysis Repository Interface

Abstract repository interface for analysis and AI agent operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from domain.entities.analysis import (
    AnalysisSession,
    AgentAnalysis,
    InvestmentDecisionEntity,
    AnalysisStatus,
    AgentType
)


class AnalysisSessionRepository(ABC):
    """Abstract repository interface for analysis session operations."""
    
    @abstractmethod
    async def create_session(self, session: AnalysisSession) -> AnalysisSession:
        """Create a new analysis session."""
        pass
    
    @abstractmethod
    async def get_session_by_id(self, session_id: UUID) -> Optional[AnalysisSession]:
        """Get analysis session by ID."""
        pass
    
    @abstractmethod
    async def list_sessions(
        self,
        user_id: Optional[UUID] = None,
        stock_id: Optional[UUID] = None,
        status: Optional[AnalysisStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnalysisSession]:
        """List analysis sessions with optional filters."""
        pass
    
    @abstractmethod
    async def update_session(self, session: AnalysisSession) -> AnalysisSession:
        """Update an existing analysis session."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: UUID) -> bool:
        """Delete an analysis session."""
        pass
    
    @abstractmethod
    async def get_user_sessions(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[AnalysisSession]:
        """Get all sessions for a specific user."""
        pass
    
    @abstractmethod
    async def get_running_sessions(self) -> List[AnalysisSession]:
        """Get all currently running analysis sessions."""
        pass


class AgentAnalysisRepository(ABC):
    """Abstract repository interface for AI agent analysis operations."""
    
    @abstractmethod
    async def create_analysis(self, analysis: AgentAnalysis) -> AgentAnalysis:
        """Create a new agent analysis result."""
        pass
    
    @abstractmethod
    async def get_analysis_by_id(self, analysis_id: UUID) -> Optional[AgentAnalysis]:
        """Get agent analysis by ID."""
        pass
    
    @abstractmethod
    async def get_session_analyses(self, session_id: UUID) -> List[AgentAnalysis]:
        """Get all agent analyses for a session."""
        pass
    
    @abstractmethod
    async def get_agent_analysis(
        self,
        session_id: UUID,
        agent_type: AgentType
    ) -> Optional[AgentAnalysis]:
        """Get specific agent analysis for a session."""
        pass
    
    @abstractmethod
    async def update_analysis(self, analysis: AgentAnalysis) -> AgentAnalysis:
        """Update an existing agent analysis."""
        pass
    
    @abstractmethod
    async def delete_analysis(self, analysis_id: UUID) -> bool:
        """Delete an agent analysis."""
        pass
    
    @abstractmethod
    async def get_agent_performance(
        self,
        agent_type: AgentType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get performance metrics for a specific agent."""
        pass


class InvestmentDecisionRepository(ABC):
    """Abstract repository interface for investment decision operations."""
    
    @abstractmethod
    async def create_decision(self, decision: InvestmentDecisionEntity) -> InvestmentDecisionEntity:
        """Create a new investment decision."""
        pass
    
    @abstractmethod
    async def get_decision_by_id(self, decision_id: UUID) -> Optional[InvestmentDecisionEntity]:
        """Get investment decision by ID."""
        pass
    
    @abstractmethod
    async def get_session_decision(self, session_id: UUID) -> Optional[InvestmentDecisionEntity]:
        """Get investment decision for a session."""
        pass
    
    @abstractmethod
    async def list_decisions(
        self,
        user_id: Optional[UUID] = None,
        stock_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[InvestmentDecisionEntity]:
        """List investment decisions with optional filters."""
        pass
    
    @abstractmethod
    async def update_decision(self, decision: InvestmentDecisionEntity) -> InvestmentDecisionEntity:
        """Update an existing investment decision."""
        pass
    
    @abstractmethod
    async def delete_decision(self, decision_id: UUID) -> bool:
        """Delete an investment decision."""
        pass
    
    @abstractmethod
    async def get_user_decisions(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[InvestmentDecisionEntity]:
        """Get all decisions for a specific user."""
        pass