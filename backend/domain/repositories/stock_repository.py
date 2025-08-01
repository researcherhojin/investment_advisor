"""
Stock Repository Interface

Abstract repository interface for stock data operations.
Follows the Repository pattern from Clean Architecture.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from domain.entities.stock import Stock, PriceData, FinancialData


class StockRepository(ABC):
    """Abstract repository interface for stock operations."""
    
    @abstractmethod
    async def create_stock(self, stock: Stock) -> Stock:
        """Create a new stock record."""
        pass
    
    @abstractmethod
    async def get_stock_by_id(self, stock_id: UUID) -> Optional[Stock]:
        """Get stock by ID."""
        pass
    
    @abstractmethod
    async def get_stock_by_ticker(self, ticker: str, market: str) -> Optional[Stock]:
        """Get stock by ticker and market."""
        pass
    
    @abstractmethod
    async def list_stocks(
        self, 
        market: Optional[str] = None,
        sector: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Stock]:
        """List stocks with optional filters."""
        pass
    
    @abstractmethod
    async def update_stock(self, stock: Stock) -> Stock:
        """Update an existing stock."""
        pass
    
    @abstractmethod
    async def delete_stock(self, stock_id: UUID) -> bool:
        """Delete a stock by ID."""
        pass
    
    @abstractmethod
    async def search_stocks(self, query: str, limit: int = 10) -> List[Stock]:
        """Search stocks by name or ticker."""
        pass


class PriceDataRepository(ABC):
    """Abstract repository interface for price data operations."""
    
    @abstractmethod
    async def create_price_data(self, price_data: PriceData) -> PriceData:
        """Create new price data record."""
        pass
    
    @abstractmethod
    async def get_price_data(
        self,
        stock_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[PriceData]:
        """Get price data for a date range."""
        pass
    
    @abstractmethod
    async def get_latest_price(self, stock_id: UUID) -> Optional[PriceData]:
        """Get the most recent price data for a stock."""
        pass
    
    @abstractmethod
    async def bulk_create_price_data(self, price_data_list: List[PriceData]) -> List[PriceData]:
        """Bulk create price data records."""
        pass
    
    @abstractmethod
    async def delete_price_data(
        self,
        stock_id: UUID,
        before_date: Optional[datetime] = None
    ) -> int:
        """Delete price data, optionally before a specific date."""
        pass


class FinancialDataRepository(ABC):
    """Abstract repository interface for financial data operations."""
    
    @abstractmethod
    async def create_financial_data(self, financial_data: FinancialData) -> FinancialData:
        """Create new financial data record."""
        pass
    
    @abstractmethod
    async def get_financial_data(
        self,
        stock_id: UUID,
        period: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[FinancialData]:
        """Get financial data with optional filters."""
        pass
    
    @abstractmethod
    async def get_latest_financial_data(
        self,
        stock_id: UUID,
        period_type: str = "FY"  # "FY" for annual, "Q" for quarterly
    ) -> Optional[FinancialData]:
        """Get the most recent financial data for a stock."""
        pass
    
    @abstractmethod
    async def update_financial_data(self, financial_data: FinancialData) -> FinancialData:
        """Update existing financial data."""
        pass
    
    @abstractmethod
    async def delete_financial_data(self, financial_data_id: UUID) -> bool:
        """Delete financial data by ID."""
        pass