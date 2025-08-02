"""
Pytest Configuration and Fixtures

Global test configuration and shared fixtures.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from datetime import datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from backend.main import app
from backend.core.config import Settings, get_settings
from backend.infrastructure.database.connection import Base
from backend.api.dependencies.database import get_db_session


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_stock_db"


# Override settings for testing
def get_test_settings() -> Settings:
    """Get test-specific settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/1",  # Use different Redis DB
        environment="testing",
        debug=True,
        use_streamlit_agents=False,  # Use mocked agents in tests
        openai_api_key="test_key",
        secret_key="test_secret_key_for_testing_only_32_chars",
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_settings] = get_test_settings
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "market": "US",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currency": "USD"
    }


@pytest.fixture
def sample_analysis_request():
    """Sample analysis request data."""
    return {
        "ticker": "AAPL",
        "market": "US",
        "user_id": str(uuid4()),
        "analysis_period": 12
    }


@pytest_asyncio.fixture
async def create_test_user(db_session: AsyncSession):
    """Factory fixture to create test users."""
    from backend.infrastructure.database.models import User
    
    created_users = []
    
    async def _create_user(**kwargs):
        user_data = {
            "email": f"user_{uuid4().hex[:8]}@test.com",
            "username": f"user_{uuid4().hex[:8]}",
            "hashed_password": "hashed_password",
            "is_active": True,
            **kwargs
        }
        
        user = User(**user_data)
        db_session.add(user)
        await db_session.flush()
        created_users.append(user)
        return user
    
    yield _create_user
    
    # Cleanup
    for user in created_users:
        await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture
async def create_test_stock(db_session: AsyncSession):
    """Factory fixture to create test stocks."""
    from backend.infrastructure.database.models import Stock
    
    created_stocks = []
    
    async def _create_stock(**kwargs):
        stock_data = {
            "ticker": f"TEST{uuid4().hex[:4].upper()}",
            "name": f"Test Company {uuid4().hex[:4]}",
            "market": "US",
            "currency": "USD",
            **kwargs
        }
        
        stock = Stock(**stock_data)
        db_session.add(stock)
        await db_session.flush()
        created_stocks.append(stock)
        return stock
    
    yield _create_stock
    
    # Cleanup
    for stock in created_stocks:
        await db_session.delete(stock)
    await db_session.commit()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": "Based on my analysis, this stock shows strong growth potential..."
            }
        }]
    }


@pytest.fixture
def mock_agent_responses():
    """Mock responses for different agent types."""
    return {
        "company_analyst": {
            "content": "회사 재무 상태가 양호하며 성장 가능성이 높습니다.",
            "confidence": 0.85,
            "recommendation": "BUY"
        },
        "industry_expert": {
            "content": "산업 전망이 긍정적이며 시장 점유율이 확대되고 있습니다.",
            "confidence": 0.80,
            "recommendation": "BUY"
        },
        "technical_analyst": {
            "content": "기술적 지표가 상승 추세를 나타내고 있습니다.",
            "confidence": 0.75,
            "recommendation": "HOLD"
        },
        "risk_manager": {
            "content": "리스크는 관리 가능한 수준입니다.",
            "confidence": 0.70,
            "recommendation": "HOLD"
        },
        "macroeconomist": {
            "content": "거시경제 환경이 우호적입니다.",
            "confidence": 0.65,
            "recommendation": "BUY"
        },
        "mediator": {
            "content": "종합적으로 매수를 추천합니다.",
            "confidence": 0.80,
            "recommendation": "BUY"
        }
    }