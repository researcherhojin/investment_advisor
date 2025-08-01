"""
Stock Domain Entity

Core business entity representing a stock/security.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class Stock(BaseModel):
    """
    Stock entity representing a tradeable security.
    
    This is the core domain entity that encapsulates all stock-related
    business logic and rules.
    """
    
    id: UUID = Field(default_factory=uuid4)
    ticker: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    market: str = Field(..., regex="^(US|KR)$")
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=200)
    exchange: Optional[str] = Field(None, max_length=50)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("ticker")
    def validate_ticker(cls, v: str) -> str:
        """Validate ticker format."""
        ticker = v.upper().strip()
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        return ticker
    
    @validator("currency")
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        currency = v.upper().strip()
        if currency not in ["USD", "KRW", "EUR", "JPY", "GBP"]:
            raise ValueError("Invalid currency code")
        return currency
    
    @property
    def full_ticker(self) -> str:
        """Get full ticker with exchange suffix for Korean stocks."""
        if self.market == "KR" and not self.ticker.endswith(".KS"):
            return f"{self.ticker}.KS"
        return self.ticker
    
    @property
    def is_korean_stock(self) -> bool:
        """Check if this is a Korean stock."""
        return self.market == "KR"
    
    @property
    def is_us_stock(self) -> bool:
        """Check if this is a US stock."""
        return self.market == "US"
    
    def update_info(self, **kwargs) -> None:
        """Update stock information."""
        allowed_fields = {
            "name", "sector", "industry", "exchange", "currency", "is_active"
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class PriceData(BaseModel):
    """Price data for a specific date."""
    
    id: UUID = Field(default_factory=uuid4)
    stock_id: UUID
    date: datetime
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    close_price: Decimal
    volume: Optional[int] = None
    adjusted_close: Optional[Decimal] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("close_price", "open_price", "high_price", "low_price", "adjusted_close")
    def validate_positive_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that prices are positive."""
        if v is not None and v <= 0:
            raise ValueError("Price must be positive")
        return v
    
    @validator("volume")
    def validate_volume(cls, v: Optional[int]) -> Optional[int]:
        """Validate volume is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Volume cannot be negative")
        return v
    
    @property
    def price_change(self) -> Optional[Decimal]:
        """Calculate price change from open to close."""
        if self.open_price is None:
            return None
        return self.close_price - self.open_price
    
    @property
    def price_change_percent(self) -> Optional[Decimal]:
        """Calculate percentage price change."""
        if self.open_price is None or self.open_price == 0:
            return None
        return (self.price_change / self.open_price) * 100
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        }


class FinancialData(BaseModel):
    """Financial data for a stock."""
    
    id: UUID = Field(default_factory=uuid4)
    stock_id: UUID
    period: str = Field(..., regex="^(Q1|Q2|Q3|Q4|FY)$")
    year: int = Field(..., ge=1900, le=2100)
    revenue: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_equity: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    free_cash_flow: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    roe: Optional[Decimal] = None  # Return on Equity
    roa: Optional[Decimal] = None  # Return on Assets
    debt_to_equity: Optional[Decimal] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("pe_ratio", "pb_ratio")
    def validate_positive_ratios(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that ratios are positive."""
        if v is not None and v < 0:
            raise ValueError("Financial ratios must be non-negative")
        return v
    
    @validator("roe", "roa")
    def validate_percentage_ratios(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate percentage ratios are within reasonable bounds."""
        if v is not None and (v < -100 or v > 100):
            raise ValueError("Percentage ratios must be between -100 and 100")
        return v
    
    @property
    def is_profitable(self) -> Optional[bool]:
        """Check if the company is profitable."""
        if self.net_income is None:
            return None
        return self.net_income > 0
    
    @property
    def is_quarterly(self) -> bool:
        """Check if this is quarterly data."""
        return self.period in ["Q1", "Q2", "Q3", "Q4"]
    
    @property
    def is_annual(self) -> bool:
        """Check if this is annual data."""
        return self.period == "FY"
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        }