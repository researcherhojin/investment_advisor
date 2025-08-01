"""
Analysis Domain Entities

Core business entities for investment analysis and AI agent results.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class AnalysisStatus(str, Enum):
    """Analysis session status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestmentDecision(str, Enum):
    """Investment decision types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class RiskLevel(str, Enum):
    """Risk level categories."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AgentType(str, Enum):
    """AI Agent types."""
    COMPANY_ANALYST = "기업분석가"
    INDUSTRY_EXPERT = "산업전문가"
    MACROECONOMIST = "거시경제전문가"
    TECHNICAL_ANALYST = "기술분석가"
    RISK_MANAGER = "리스크관리자"
    MEDIATOR = "중재자"


class AnalysisSession(BaseModel):
    """
    Analysis session representing a complete investment analysis.
    
    Orchestrates multiple AI agents to analyze a stock and make
    investment recommendations.
    """
    
    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    stock_id: UUID
    session_data: Dict[str, Any] = Field(default_factory=dict)
    analysis_period: int = Field(default=12, ge=1, le=60)  # months
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @validator("analysis_period")
    def validate_analysis_period(cls, v: int) -> int:
        """Validate analysis period is reasonable."""
        if v not in [1, 3, 6, 12, 24, 36, 60]:
            raise ValueError("Analysis period must be 1, 3, 6, 12, 24, 36, or 60 months")
        return v
    
    def start_analysis(self) -> None:
        """Mark analysis as started."""
        if self.status != AnalysisStatus.PENDING:
            raise ValueError("Analysis can only be started from pending state")
        
        self.status = AnalysisStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete_analysis(self) -> None:
        """Mark analysis as completed."""
        if self.status != AnalysisStatus.RUNNING:
            raise ValueError("Analysis can only be completed from running state")
        
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def fail_analysis(self, error_message: str) -> None:
        """Mark analysis as failed."""
        if self.status not in [AnalysisStatus.PENDING, AnalysisStatus.RUNNING]:
            raise ValueError("Analysis can only be failed from pending or running state")
        
        self.status = AnalysisStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    @property
    def duration_seconds(self) -> Optional[int]:
        """Get analysis duration in seconds."""
        if self.completed_at is None:
            return None
        return int((self.completed_at - self.started_at).total_seconds())
    
    @property
    def is_completed(self) -> bool:
        """Check if analysis is completed."""
        return self.status == AnalysisStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if analysis failed."""
        return self.status == AnalysisStatus.FAILED
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class AgentAnalysis(BaseModel):
    """
    Individual AI agent analysis result.
    
    Represents the output of a single AI agent's analysis
    of a stock or market condition.
    """
    
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    agent_type: AgentType
    agent_weight: Decimal = Field(default=Decimal("1.0"), ge=0, le=2)
    analysis_result: str = Field(..., min_length=1)
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=1)
    execution_time_ms: Optional[int] = Field(None, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("analysis_result")
    def validate_analysis_result(cls, v: str) -> str:
        """Validate analysis result is not empty."""
        if not v.strip():
            raise ValueError("Analysis result cannot be empty")
        return v.strip()
    
    @validator("confidence_score")
    def validate_confidence_score(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate confidence score is between 0 and 1."""
        if v is not None and not (0 <= v <= 1):
            raise ValueError("Confidence score must be between 0 and 1")
        return v
    
    @property
    def confidence_percentage(self) -> Optional[int]:
        """Get confidence as percentage."""
        if self.confidence_score is None:
            return None
        return int(self.confidence_score * 100)
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if analysis has high confidence."""
        if self.confidence_score is None:
            return False
        return self.confidence_score >= Decimal("0.8")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        }


class InvestmentDecisionEntity(BaseModel):
    """
    Final investment decision entity.
    
    Represents the consolidated recommendation from all AI agents
    after mediation and risk assessment.
    """
    
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    decision: InvestmentDecision
    confidence: Decimal = Field(..., ge=0, le=1)
    rationale: str = Field(..., min_length=10)
    price_target: Optional[Decimal] = Field(None, gt=0)
    stop_loss: Optional[Decimal] = Field(None, gt=0)
    time_horizon: Optional[str] = Field(None, max_length=20)
    risk_level: Optional[RiskLevel] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("rationale")
    def validate_rationale(cls, v: str) -> str:
        """Validate rationale is meaningful."""
        rationale = v.strip()
        if len(rationale) < 10:
            raise ValueError("Rationale must be at least 10 characters long")
        return rationale
    
    @validator("confidence")
    def validate_confidence(cls, v: Decimal) -> Decimal:
        """Validate confidence is between 0 and 1."""
        if not (0 <= v <= 1):
            raise ValueError("Confidence must be between 0 and 1")
        return v
    
    @property
    def confidence_percentage(self) -> int:
        """Get confidence as percentage."""
        return int(self.confidence * 100)
    
    @property
    def is_strong_decision(self) -> bool:
        """Check if decision has strong confidence."""
        return self.confidence >= Decimal("0.75")
    
    @property
    def is_buy_recommendation(self) -> bool:
        """Check if this is a buy recommendation."""
        return self.decision == InvestmentDecision.BUY
    
    @property
    def is_sell_recommendation(self) -> bool:
        """Check if this is a sell recommendation."""
        return self.decision == InvestmentDecision.SELL
    
    @property
    def is_hold_recommendation(self) -> bool:
        """Check if this is a hold recommendation."""
        return self.decision == InvestmentDecision.HOLD
    
    def validate_price_targets(self, current_price: Decimal) -> None:
        """Validate price targets against current price."""
        if self.price_target is not None:
            if self.is_buy_recommendation and self.price_target <= current_price:
                raise ValueError("Buy price target should be higher than current price")
            elif self.is_sell_recommendation and self.price_target >= current_price:
                raise ValueError("Sell price target should be lower than current price")
        
        if self.stop_loss is not None:
            if self.is_buy_recommendation and self.stop_loss >= current_price:
                raise ValueError("Stop loss should be lower than current price for buy recommendation")
            elif self.is_sell_recommendation and self.stop_loss <= current_price:
                raise ValueError("Stop loss should be higher than current price for sell recommendation")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        }