"""
Stock DTOs

Data Transfer Objects for stock-related data.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StockSearchDTO(BaseModel):
    """DTO for stock search results."""
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    market: str = Field(..., description="Market (US, KR)")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry classification")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "market": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Consumer Electronics"
            }
        }


class StockDTO(BaseModel):
    """DTO for detailed stock information."""
    id: UUID = Field(..., description="Stock ID")
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    market: str = Field(..., description="Market (US, KR)")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry classification")
    currency: str = Field(..., description="Trading currency")
    
    # Price information
    current_price: Optional[float] = Field(None, description="Current stock price")
    price_updated_at: Optional[datetime] = Field(None, description="Price last updated")
    
    # Company details
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(None, description="Company website")
    employees: Optional[int] = Field(None, description="Number of employees")
    founded_year: Optional[int] = Field(None, description="Year founded")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "market": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "currency": "USD",
                "current_price": 195.42,
                "price_updated_at": "2025-01-15T10:30:00Z",
                "market_cap": 3050000000000,
                "description": "Apple Inc. designs, manufactures, and markets smartphones...",
                "website": "https://www.apple.com",
                "employees": 164000,
                "founded_year": 1976
            }
        }


class PriceHistoryDTO(BaseModel):
    """DTO for historical price data."""
    date: str = Field(..., description="Date (ISO format)")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: Optional[float] = Field(None, description="Trading volume")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2025-01-15",
                "open": 194.50,
                "high": 196.20,
                "low": 193.80,
                "close": 195.42,
                "volume": 52341200
            }
        }


class StockQuoteDTO(BaseModel):
    """DTO for real-time stock quote."""
    ticker: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    change_percent: float = Field(..., description="Price change percentage")
    volume: float = Field(..., description="Trading volume")
    timestamp: datetime = Field(..., description="Quote timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "price": 195.42,
                "change": 2.15,
                "change_percent": 1.11,
                "volume": 52341200,
                "timestamp": "2025-01-15T15:30:00Z"
            }
        }