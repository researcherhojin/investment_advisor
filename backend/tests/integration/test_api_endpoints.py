"""
Integration Tests for API Endpoints

Test complete API request/response flows.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    async def test_health_check(self, client: AsyncClient):
        """Test basic health check."""
        response = await client.get("/api/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check."""
        response = await client.get("/api/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "cache" in data["checks"]
        assert "openai" in data["checks"]
    
    async def test_liveness_check(self, client: AsyncClient):
        """Test liveness check."""
        response = await client.get("/api/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data


@pytest.mark.asyncio
class TestStockEndpoints:
    """Test stock-related endpoints."""
    
    async def test_search_stocks(self, client: AsyncClient, create_test_stock):
        """Test stock search."""
        # Create test stocks
        await create_test_stock(ticker="AAPL", name="Apple Inc.", market="US")
        await create_test_stock(ticker="MSFT", name="Microsoft Corp", market="US")
        
        # Search stocks
        response = await client.get("/api/stocks/search?query=Apple")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["ticker"] == "AAPL"
        assert data[0]["name"] == "Apple Inc."
    
    async def test_get_stock_details(self, client: AsyncClient, create_test_stock):
        """Test getting stock details."""
        # Create test stock
        stock = await create_test_stock(
            ticker="GOOGL",
            name="Alphabet Inc.",
            market="US",
            sector="Technology",
            industry="Internet Services"
        )
        
        # Get stock details
        response = await client.get("/api/stocks/GOOGL?market=US")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "GOOGL"
        assert data["name"] == "Alphabet Inc."
        assert data["sector"] == "Technology"
        assert data["id"] == str(stock.id)
    
    async def test_stock_not_found(self, client: AsyncClient):
        """Test stock not found error."""
        response = await client.get("/api/stocks/INVALID")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_get_price_history(self, client: AsyncClient, create_test_stock):
        """Test getting price history."""
        # Create test stock
        stock = await create_test_stock(ticker="TSLA", name="Tesla Inc.", market="US")
        
        # Get price history
        response = await client.get("/api/stocks/TSLA/price-history?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Note: Will be empty unless we add price history data
    
    async def test_get_trending_stocks(self, client: AsyncClient, create_test_stock):
        """Test getting trending stocks."""
        # Create test stocks
        await create_test_stock(ticker="NVDA", name="NVIDIA Corp", market="US")
        await create_test_stock(ticker="AMD", name="AMD Inc.", market="US")
        
        response = await client.get("/api/stocks/trending?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
class TestAnalysisEndpoints:
    """Test analysis-related endpoints."""
    
    async def test_create_analysis(
        self,
        client: AsyncClient,
        create_test_stock,
        create_test_user,
        mock_agent_responses
    ):
        """Test creating new analysis."""
        # Create test data
        user = await create_test_user()
        stock = await create_test_stock(ticker="AAPL", name="Apple Inc.", market="US")
        
        # Mock agent service
        with patch('backend.application.services.agent_service.AgentService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.execute_agent = AsyncMock(return_value=mock_agent_responses["company_analyst"])
            
            # Create analysis request
            request_data = {
                "ticker": "AAPL",
                "market": "US",
                "user_id": str(user.id),
                "analysis_period": 12
            }
            
            response = await client.post("/api/analysis/", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert data["stock_info"]["ticker"] == "AAPL"
            assert "agent_analyses" in data
            assert "analysis_metadata" in data
    
    async def test_get_analysis_results(
        self,
        client: AsyncClient,
        db_session,
        create_test_user,
        create_test_stock
    ):
        """Test retrieving analysis results."""
        from backend.infrastructure.database.models import AnalysisSession as SessionModel
        from backend.infrastructure.database.models import AnalysisStatus
        
        # Create test session
        user = await create_test_user()
        stock = await create_test_stock(ticker="MSFT", name="Microsoft", market="US")
        
        session = SessionModel(
            user_id=user.id,
            stock_id=stock.id,
            analysis_period=12,
            status=AnalysisStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()
        
        # Get analysis results
        response = await client.get(f"/api/analysis/{session.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == str(session.id)
        assert data["stock_info"]["ticker"] == "MSFT"
    
    async def test_analysis_not_found(self, client: AsyncClient):
        """Test analysis not found error."""
        from uuid import uuid4
        
        response = await client.get(f"/api/analysis/{uuid4()}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_list_analyses(
        self,
        client: AsyncClient,
        db_session,
        create_test_user,
        create_test_stock
    ):
        """Test listing analyses."""
        # Note: This endpoint returns mock data in current implementation
        response = await client.get("/api/analysis/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "session_id" in data[0]
            assert "stock_ticker" in data[0]
            assert "status" in data[0]
    
    async def test_analysis_progress(self, client: AsyncClient):
        """Test getting analysis progress."""
        from uuid import uuid4
        
        # Note: This endpoint returns mock data in current implementation
        response = await client.get(f"/api/analysis/{uuid4()}/progress")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "progress_percentage" in data
        assert "current_step" in data