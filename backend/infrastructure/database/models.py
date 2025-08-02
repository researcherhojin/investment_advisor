"""
Database Models

SQLAlchemy models for the AI Investment Advisory System.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, DateTime, JSON, Float, Integer, Boolean,
    ForeignKey, Index, Text, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .connection import Base


class Market(str, enum.Enum):
    """Market enumeration."""
    US = "US"
    KR = "KR"
    CRYPTO = "CRYPTO"


class AnalysisStatus(str, enum.Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RUNNING = "running"  # Add RUNNING status
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, enum.Enum):
    """Agent type enumeration."""
    COMPANY_ANALYST = "company_analyst"
    INDUSTRY_EXPERT = "industry_expert"
    MACROECONOMIST = "macroeconomist"
    TECHNICAL_ANALYST = "technical_analyst"
    RISK_MANAGER = "risk_manager"
    MEDIATOR = "mediator"


class InvestmentDecisionType(str, enum.Enum):
    """Investment decision type enumeration."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )


class Stock(Base):
    """Stock information model."""
    __tablename__ = "stocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    market = Column(SQLEnum(Market), nullable=False)
    name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    currency = Column(String(10))
    exchange = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="stock")
    price_history = relationship("PriceHistory", back_populates="stock", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("ticker", "market", name="uq_stocks_ticker_market"),
        Index("ix_stocks_ticker_market", "ticker", "market"),
    )


class Analysis(Base):
    """Stock analysis model."""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    
    # Analysis parameters
    analysis_period = Column(Integer, default=12)  # months
    industry = Column(String(100))
    
    # Results
    final_decision = Column(Text)
    confidence_score = Column(Float)
    target_price = Column(Float)
    risk_score = Column(Float)
    
    # Agent results stored as JSON
    agent_results = Column(JSON, default=dict)
    technical_indicators = Column(JSON, default=dict)
    fundamental_metrics = Column(JSON, default=dict)
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    stock = relationship("Stock", back_populates="analyses")
    
    __table_args__ = (
        Index("ix_analyses_user_created", "user_id", "created_at"),
        Index("ix_analyses_stock_created", "stock_id", "created_at"),
    )


class PriceHistory(Base):
    """Historical price data model."""
    __tablename__ = "price_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Float)
    
    # Relationships
    stock = relationship("Stock", back_populates="price_history")
    
    __table_args__ = (
        UniqueConstraint("stock_id", "date", name="uq_price_history_stock_date"),
        Index("ix_price_history_stock_date", "stock_id", "date"),
    )


class Watchlist(Base):
    """User watchlist model."""
    __tablename__ = "watchlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_watchlists_user_name", "user_id", "name"),
    )


class WatchlistItem(Base):
    """Watchlist item model."""
    __tablename__ = "watchlist_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    watchlist_id = Column(UUID(as_uuid=True), ForeignKey("watchlists.id"), nullable=False)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    notes = Column(Text)
    alert_price = Column(Float)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    stock = relationship("Stock")
    
    __table_args__ = (
        UniqueConstraint("watchlist_id", "stock_id", name="uq_watchlist_items_watchlist_stock"),
    )


class AgentLog(Base):
    """AI Agent execution log model."""
    __tablename__ = "agent_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)
    status = Column(String(50))
    error_message = Column(Text)
    result = Column(JSON)
    
    # Relationships
    analysis = relationship("Analysis")
    
    __table_args__ = (
        Index("ix_agent_logs_analysis_agent", "analysis_id", "agent_name"),
    )


class AnalysisSession(Base):
    """Analysis session model - tracks a complete analysis workflow."""
    __tablename__ = "analysis_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    analysis_period = Column(Integer, default=12)  # Months
    
    # Status tracking
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Session metadata
    session_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    stock = relationship("Stock")
    agent_analyses = relationship("AgentAnalysis", back_populates="session", cascade="all, delete-orphan")
    investment_decision = relationship("InvestmentDecision", back_populates="session", uselist=False)
    
    __table_args__ = (
        Index("ix_analysis_sessions_user_created", "user_id", "created_at"),
        Index("ix_analysis_sessions_stock_created", "stock_id", "created_at"),
        Index("ix_analysis_sessions_status", "status"),
    )


class AgentAnalysis(Base):
    """Individual agent analysis result."""
    __tablename__ = "agent_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("analysis_sessions.id"), nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    
    # Analysis result
    analysis_result = Column(Text, nullable=False)
    confidence_score = Column(Float)
    execution_time_ms = Column(Integer)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="agent_analyses")
    
    __table_args__ = (
        UniqueConstraint("session_id", "agent_type", name="uq_agent_analyses_session_agent"),
        Index("ix_agent_analyses_session", "session_id"),
    )


class InvestmentDecision(Base):
    """Final investment decision for an analysis session."""
    __tablename__ = "investment_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("analysis_sessions.id"), nullable=False, unique=True)
    
    # Decision details
    decision = Column(SQLEnum(InvestmentDecisionType), nullable=False)
    confidence = Column(Float, nullable=False)
    rationale = Column(Text, nullable=False)
    
    # Price targets
    price_target = Column(Float)
    stop_loss = Column(Float)
    
    # Risk assessment
    time_horizon = Column(String(50))  # e.g., "3-6 months"
    risk_level = Column(SQLEnum(RiskLevel))
    
    # Structured insights
    key_factors = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="investment_decision")
    
    __table_args__ = (
        Index("ix_investment_decisions_decision", "decision"),
        Index("ix_investment_decisions_created", "created_at"),
    )