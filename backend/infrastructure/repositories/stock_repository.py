"""
Stock Repository

Repository for stock-related database operations.
"""

from typing import Optional, List, Type
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
import structlog

from .base import BaseRepository
from backend.infrastructure.database.models import Stock, Market, PriceHistory

logger = structlog.get_logger(__name__)


class StockRepository(BaseRepository[Stock]):
    """Repository for stock operations."""
    
    @property
    def model_class(self) -> Type[Stock]:
        return Stock
    
    async def get_by_ticker(
        self,
        ticker: str,
        market: Market
    ) -> Optional[Stock]:
        """Get stock by ticker and market."""
        try:
            query = select(Stock).where(
                and_(
                    Stock.ticker == ticker.upper(),
                    Stock.market == market
                )
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting stock by ticker", ticker=ticker, market=market, error=str(e))
            raise
    
    async def get_or_create(
        self,
        ticker: str,
        market: Market,
        **kwargs
    ) -> Stock:
        """Get existing stock or create new one."""
        stock = await self.get_by_ticker(ticker, market)
        
        if stock:
            return stock
        
        return await self.create(
            ticker=ticker.upper(),
            market=market,
            **kwargs
        )
    
    async def search(
        self,
        query: str,
        market: Optional[Market] = None,
        limit: int = 10
    ) -> List[Stock]:
        """Search stocks by ticker or name."""
        try:
            search_term = f"%{query}%"
            
            conditions = or_(
                Stock.ticker.ilike(search_term),
                Stock.name.ilike(search_term)
            )
            
            stmt = select(Stock).where(conditions)
            
            if market:
                stmt = stmt.where(Stock.market == market)
            
            stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error("Error searching stocks", query=query, error=str(e))
            raise
    
    async def get_trending(
        self,
        market: Optional[Market] = None,
        limit: int = 10
    ) -> List[Stock]:
        """Get trending stocks based on recent analyses."""
        try:
            # Subquery to count recent analyses
            from backend.infrastructure.database.models import Analysis
            
            recent_date = datetime.utcnow() - timedelta(days=7)
            
            analysis_count = (
                select(
                    Analysis.stock_id,
                    func.count(Analysis.id).label("analysis_count")
                )
                .where(Analysis.created_at >= recent_date)
                .group_by(Analysis.stock_id)
                .subquery()
            )
            
            # Main query
            query = (
                select(Stock)
                .join(
                    analysis_count,
                    Stock.id == analysis_count.c.stock_id
                )
                .order_by(analysis_count.c.analysis_count.desc())
            )
            
            if market:
                query = query.where(Stock.market == market)
            
            query = query.limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error("Error getting trending stocks", error=str(e))
            raise


class PriceHistoryRepository(BaseRepository[PriceHistory]):
    """Repository for price history operations."""
    
    @property
    def model_class(self) -> Type[PriceHistory]:
        return PriceHistory
    
    async def get_by_date_range(
        self,
        stock_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[PriceHistory]:
        """Get price history for a date range."""
        try:
            query = (
                select(PriceHistory)
                .where(
                    and_(
                        PriceHistory.stock_id == stock_id,
                        PriceHistory.date >= start_date,
                        PriceHistory.date <= end_date
                    )
                )
                .order_by(PriceHistory.date)
            )
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error("Error getting price history", stock_id=stock_id, error=str(e))
            raise
    
    async def bulk_upsert(
        self,
        stock_id: UUID,
        price_data: List[Dict[str, Any]]
    ) -> int:
        """Bulk insert or update price history."""
        try:
            # For PostgreSQL, we can use INSERT ... ON CONFLICT
            from sqlalchemy.dialects.postgresql import insert
            
            stmt = insert(PriceHistory)
            
            # Prepare data
            records = [
                {
                    "stock_id": stock_id,
                    "date": record["date"],
                    "open": record.get("open"),
                    "high": record.get("high"),
                    "low": record.get("low"),
                    "close": record["close"],
                    "volume": record.get("volume")
                }
                for record in price_data
            ]
            
            # Upsert
            stmt = stmt.on_conflict_do_update(
                index_elements=["stock_id", "date"],
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "volume": stmt.excluded.volume
                }
            )
            
            await self.session.execute(stmt, records)
            await self.session.flush()
            
            return len(records)
        except Exception as e:
            logger.error("Error bulk upserting price history", stock_id=stock_id, error=str(e))
            raise
    
    async def get_latest_price(
        self,
        stock_id: UUID
    ) -> Optional[PriceHistory]:
        """Get the latest price for a stock."""
        try:
            query = (
                select(PriceHistory)
                .where(PriceHistory.stock_id == stock_id)
                .order_by(PriceHistory.date.desc())
                .limit(1)
            )
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting latest price", stock_id=stock_id, error=str(e))
            raise