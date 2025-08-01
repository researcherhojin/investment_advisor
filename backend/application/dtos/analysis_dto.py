"""
Analysis Data Transfer Objects

DTOs for analysis-related operations between application layers.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AnalysisRequestDTO(BaseModel):
    """DTO for analysis request."""
    
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    market: str = Field(..., regex="^(US|KR)$", description="Market (US or KR)")
    stock_name: Optional[str] = Field(None, max_length=255, description="Stock name")
    sector: Optional[str] = Field(None, max_length=100, description="Sector")
    industry: Optional[str] = Field(None, max_length=200, description="Industry")
    analysis_period: Optional[int] = Field(12, ge=1, le=60, description="Analysis period in months")
    user_id: Optional[UUID] = Field(None, description="User ID (optional for anonymous analysis)")
    
    @validator("ticker")
    def validate_ticker(cls, v: str) -> str:
        """Validate and normalize ticker."""
        return v.upper().strip()
    
    @validator("market")
    def validate_market(cls, v: str) -> str:
        """Validate and normalize market."""
        return v.upper().strip()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}


class AnalysisResultDTO(BaseModel):
    """DTO for complete analysis results."""
    
    session_id: UUID = Field(..., description="Analysis session ID")
    stock_info: Dict[str, Any] = Field(..., description="Stock information")
    agent_analyses: Dict[str, Dict[str, Any]] = Field(..., description="AI agent analysis results")
    investment_decision: Optional[Dict[str, Any]] = Field(None, description="Final investment decision")
    analysis_metadata: Dict[str, Any] = Field(..., description="Analysis metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}


class AgentAnalysisDTO(BaseModel):
    """DTO for individual agent analysis."""
    
    agent_type: str = Field(..., description="Agent type")
    content: str = Field(..., description="Analysis content")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    created_at: str = Field(..., description="Creation timestamp")


class InvestmentDecisionDTO(BaseModel):
    """DTO for investment decision."""
    
    decision: str = Field(..., regex="^(BUY|SELL|HOLD)$", description="Investment decision")
    confidence: float = Field(..., ge=0, le=1, description="Decision confidence")
    rationale: str = Field(..., min_length=10, description="Decision rationale")
    price_target: Optional[float] = Field(None, gt=0, description="Price target")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    time_horizon: Optional[str] = Field(None, description="Investment time horizon")
    risk_level: Optional[str] = Field(None, regex="^(LOW|MEDIUM|HIGH)$", description="Risk level")


class AnalysisProgressDTO(BaseModel):
    """DTO for analysis progress updates."""
    
    session_id: UUID = Field(..., description="Analysis session ID")
    status: str = Field(..., description="Current status")
    progress_percentage: int = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current step description")
    completed_agents: int = Field(default=0, description="Number of completed agents")
    total_agents: int = Field(default=6, description="Total number of agents")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated time remaining in seconds")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}


class AnalysisListItemDTO(BaseModel):
    """DTO for analysis list item (summary view)."""
    
    session_id: UUID = Field(..., description="Analysis session ID")
    stock_ticker: str = Field(..., description="Stock ticker")
    stock_name: str = Field(..., description="Stock name")
    market: str = Field(..., description="Market")
    status: str = Field(..., description="Analysis status")
    created_at: str = Field(..., description="Creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    decision: Optional[str] = Field(None, description="Investment decision")
    confidence: Optional[float] = Field(None, description="Decision confidence")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}