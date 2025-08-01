"""
Stock Data Routes

API endpoints for stock information and price data.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_stocks():
    """List available stocks."""
    return {"message": "Stock listing endpoint - to be implemented"}


@router.get("/{ticker}")
async def get_stock(ticker: str):
    """Get stock information."""
    return {"message": f"Stock {ticker} endpoint - to be implemented"}


@router.get("/{ticker}/price-history")
async def get_price_history(ticker: str):
    """Get stock price history."""
    return {"message": f"Price history for {ticker} - to be implemented"}