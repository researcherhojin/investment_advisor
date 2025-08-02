"""
Stock Routes

API endpoints for stock information and market data.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from application.dtos.stock_dto import StockDTO, StockSearchDTO, PriceHistoryDTO
from infrastructure.repositories.stock_repository import StockRepository
from api.dependencies.use_cases import get_stock_repository

router = APIRouter()


@router.get("/search", response_model=List[StockSearchDTO])
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query"),
    market: Optional[str] = Query(None, description="Market filter (US, KR)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    stock_repo: StockRepository = Depends(get_stock_repository)
):
    """
    Search stocks by ticker or name.
    
    Searches across both US and Korean markets unless filtered.
    """
    try:
        results = await stock_repo.search_stocks(query, market, limit)
        
        return [
            StockSearchDTO(
                ticker=stock.ticker,
                name=stock.name,
                market=stock.market,
                exchange=stock.exchange,
                sector=stock.sector,
                industry=stock.industry
            )
            for stock in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Stock search failed")


@router.get("/{ticker}", response_model=StockDTO)
async def get_stock(
    ticker: str,
    market: Optional[str] = Query(None, description="Market (US, KR)"),
    stock_repo: StockRepository = Depends(get_stock_repository)
):
    """
    Get detailed stock information.
    
    Returns comprehensive stock data including company details.
    """
    try:
        stock = await stock_repo.get_stock_by_ticker(ticker, market)
        
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Get latest price
        latest_price = await stock_repo.get_latest_price(stock.id)
        
        return StockDTO(
            id=stock.id,
            ticker=stock.ticker,
            name=stock.name,
            market=stock.market,
            exchange=stock.exchange,
            sector=stock.sector,
            industry=stock.industry,
            currency=stock.currency,
            current_price=float(latest_price.close_price) if latest_price else None,
            price_updated_at=latest_price.created_at if latest_price else None,
            market_cap=stock.market_cap,
            description=stock.description,
            website=stock.website,
            employees=stock.employees,
            founded_year=stock.founded_year
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve stock information")


@router.get("/{ticker}/price-history", response_model=List[PriceHistoryDTO])
async def get_price_history(
    ticker: str,
    market: Optional[str] = Query(None, description="Market (US, KR)"),
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    stock_repo: StockRepository = Depends(get_stock_repository)
):
    """
    Get historical price data for a stock.
    
    Returns daily OHLCV data for the specified period.
    """
    try:
        # Get stock
        stock = await stock_repo.get_stock_by_ticker(ticker, market)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Get price history
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        history = await stock_repo.get_price_history(
            stock.id,
            start_date,
            end_date
        )
        
        return [
            PriceHistoryDTO(
                date=record.date.isoformat(),
                open=record.open,
                high=record.high,
                low=record.low,
                close=record.close,
                volume=record.volume
            )
            for record in history
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve price history")


@router.get("/trending", response_model=List[StockSearchDTO])
async def get_trending_stocks(
    market: Optional[str] = Query(None, description="Market filter (US, KR)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    stock_repo: StockRepository = Depends(get_stock_repository)
):
    """
    Get trending stocks based on recent analysis activity.
    
    Returns stocks with the most analysis requests in the last 24 hours.
    """
    try:
        # Get trending stocks
        trending = await stock_repo.get_trending_stocks(market, limit)
        
        return [
            StockSearchDTO(
                ticker=stock.ticker,
                name=stock.name,
                market=stock.market,
                exchange=stock.exchange,
                sector=stock.sector,
                industry=stock.industry
            )
            for stock in trending
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve trending stocks")


@router.post("/{ticker}/refresh-data")
async def refresh_stock_data(
    ticker: str,
    market: Optional[str] = Query(None, description="Market (US, KR)"),
    stock_repo: StockRepository = Depends(get_stock_repository)
):
    """
    Trigger a refresh of stock data from external sources.
    
    Updates price data and company information.
    """
    try:
        # Get stock
        stock = await stock_repo.get_stock_by_ticker(ticker, market)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # TODO: Implement data refresh logic
        # This would typically:
        # 1. Fetch latest price data from Yahoo Finance or other sources
        # 2. Update company information if needed
        # 3. Store in database
        
        return {
            "message": "Stock data refresh initiated",
            "ticker": ticker,
            "market": stock.market
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to refresh stock data")