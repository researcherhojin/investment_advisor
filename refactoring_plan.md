# 🔧 리팩토링 계획

## 1. 🚨 긴급 리팩토링 사항

### 1.1 에러 처리 일관성 개선
현재 각 모듈마다 다른 방식으로 에러를 처리하고 있습니다.

**문제점:**
- 일부는 로깅만, 일부는 raise, 일부는 silent fail
- 사용자에게 보여지는 에러 메시지가 일관되지 않음

**개선안:**
```python
# investment_advisor/core/exceptions.py (새 파일)
class InvestmentAdvisorError(Exception):
    """Base exception for all custom errors"""
    pass

class DataFetchError(InvestmentAdvisorError):
    """Error fetching data from external sources"""
    pass

class AnalysisError(InvestmentAdvisorError):
    """Error during analysis process"""
    pass

class ConfigurationError(InvestmentAdvisorError):
    """Configuration related errors"""
    pass
```

### 1.2 중복 코드 제거 (DRY 원칙)

**문제점 1: 데이터 fetcher들의 중복된 retry 로직**
```python
# us_stock.py, korea_stock.py에 중복된 코드
time.sleep(self.request_delay + random.uniform(0, 1))
```

**개선안:**
```python
# investment_advisor/data/mixins.py
class RetryMixin:
    def with_retry(self, func, max_retries=3):
        """Common retry logic for all data fetchers"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(self.request_delay * (2 ** attempt))
```

**문제점 2: Agent들의 중복된 포맷팅 로직**
- 각 에이전트가 비슷한 방식으로 결과를 포맷팅

**개선안:**
- BaseAgent에서 공통 포맷팅 메서드 제공
- 각 에이전트는 순수한 분석 로직만 구현

### 1.3 타입 힌팅 완성도 향상

**현재 상태:**
- 일부 함수만 타입 힌팅이 있음
- Dict[str, Any] 같은 모호한 타입 사용

**개선안:**
```python
# investment_advisor/types.py
from typing import TypedDict, Literal, Optional
from datetime import datetime

class StockData(TypedDict):
    ticker: str
    currentPrice: float
    marketCap: int
    PER: Optional[float]
    PBR: Optional[float]
    
class AnalysisResult(TypedDict):
    decision: Literal["BUY", "SELL", "HOLD"]
    confidence: float
    reasoning: str
    timestamp: datetime
```

## 2. 🏗️ 구조적 개선사항

### 2.1 설정 관리 중앙화

**문제점:**
- 설정이 여러 파일에 분산됨
- 환경 변수와 하드코딩된 값이 혼재

**개선안:**
```python
# investment_advisor/core/config.py
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    alpha_vantage_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")
    
    # Model Configuration
    model_name: str = Field("gpt-4o-mini-2024-07-18", env="DEFAULT_MODEL")
    temperature: float = Field(0.1, env="MODEL_TEMPERATURE")
    
    # Data Configuration
    cache_enabled: bool = Field(True, env="USE_CACHE")
    cache_ttl: int = Field(900, env="CACHE_TTL")
    
    # Application Configuration
    request_timeout: int = Field(15, env="REQUEST_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton pattern
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

### 2.2 의존성 주입 패턴 적용

**문제점:**
- 각 클래스가 직접 의존성을 생성
- 테스트 어려움

**개선안:**
```python
# investment_advisor/core/container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)
    
    # Data fetchers
    simple_fetcher = providers.Singleton(
        SimpleStockFetcher,
        config=config
    )
    
    us_stock_fetcher = providers.Singleton(
        USStockDataFetcher,
        simple_fetcher=simple_fetcher,
        config=config
    )
    
    # Agents
    company_analyst = providers.Factory(
        CompanyAnalystAgent,
        simple_fetcher=simple_fetcher,
        llm_config=config.provided.model_config
    )
```

### 2.3 비즈니스 로직 분리

**문제점:**
- UI 코드에 비즈니스 로직이 섞여 있음
- 데이터 fetching과 처리 로직이 혼재

**개선안:**
```python
# investment_advisor/services/analysis_service.py
class AnalysisService:
    def __init__(self, 
                 data_fetcher: DataFetcher,
                 agents: Dict[str, InvestmentAgent],
                 cache: CacheManager):
        self.data_fetcher = data_fetcher
        self.agents = agents
        self.cache = cache
    
    async def analyze_stock(self, 
                          ticker: str, 
                          market: str) -> AnalysisResult:
        """Pure business logic for stock analysis"""
        # 1. Fetch data
        stock_data = await self.data_fetcher.fetch_async(ticker, market)
        
        # 2. Run agents in parallel
        agent_results = await self._run_agents_async(stock_data)
        
        # 3. Aggregate results
        final_decision = self._aggregate_decisions(agent_results)
        
        return final_decision
```

## 3. 🔄 패턴 개선사항

### 3.1 Strategy Pattern for Data Sources

```python
# investment_advisor/data/strategies.py
from abc import ABC, abstractmethod

class DataSourceStrategy(ABC):
    @abstractmethod
    async def fetch_stock_data(self, ticker: str) -> StockData:
        pass

class YahooFinanceStrategy(DataSourceStrategy):
    async def fetch_stock_data(self, ticker: str) -> StockData:
        # Yahoo Finance implementation
        pass

class AlphaVantageStrategy(DataSourceStrategy):
    async def fetch_stock_data(self, ticker: str) -> StockData:
        # Alpha Vantage implementation
        pass

class MockDataStrategy(DataSourceStrategy):
    async def fetch_stock_data(self, ticker: str) -> StockData:
        # Mock data implementation
        pass

class DataFetcherContext:
    def __init__(self, strategy: DataSourceStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: DataSourceStrategy):
        self._strategy = strategy
    
    async def fetch_data(self, ticker: str) -> StockData:
        return await self._strategy.fetch_stock_data(ticker)
```

### 3.2 Observer Pattern for Progress Updates

```python
# investment_advisor/core/events.py
from typing import Protocol
from dataclasses import dataclass

class ProgressObserver(Protocol):
    def on_progress(self, event: ProgressEvent) -> None:
        ...

@dataclass
class ProgressEvent:
    stage: str
    progress: float
    message: str

class AnalysisObservable:
    def __init__(self):
        self._observers: List[ProgressObserver] = []
    
    def attach(self, observer: ProgressObserver):
        self._observers.append(observer)
    
    def notify(self, event: ProgressEvent):
        for observer in self._observers:
            observer.on_progress(event)
```

### 3.3 Repository Pattern for Data Access

```python
# investment_advisor/repositories/stock_repository.py
from abc import ABC, abstractmethod

class StockRepository(ABC):
    @abstractmethod
    async def get_by_ticker(self, ticker: str) -> Optional[Stock]:
        pass
    
    @abstractmethod
    async def save(self, stock: Stock) -> Stock:
        pass

class CachedStockRepository(StockRepository):
    def __init__(self, 
                 cache: CacheManager,
                 remote_repo: StockRepository):
        self.cache = cache
        self.remote_repo = remote_repo
    
    async def get_by_ticker(self, ticker: str) -> Optional[Stock]:
        # Check cache first
        cached = await self.cache.get(f"stock:{ticker}")
        if cached:
            return cached
        
        # Fetch from remote
        stock = await self.remote_repo.get_by_ticker(ticker)
        if stock:
            await self.cache.set(f"stock:{ticker}", stock)
        
        return stock
```

## 4. 🧪 테스트 가능성 개선

### 4.1 Mock 객체 준비

```python
# tests/mocks.py
class MockLLM:
    def __init__(self, responses: Dict[str, str]):
        self.responses = responses
    
    def invoke(self, prompt: str) -> MockResponse:
        # Return predefined responses for testing
        pass

class MockDataFetcher:
    def __init__(self, data: Dict[str, StockData]):
        self.data = data
    
    async def fetch_stock_data(self, ticker: str) -> StockData:
        return self.data.get(ticker, {})
```

### 4.2 테스트 구조

```
tests/
├── unit/
│   ├── test_agents.py
│   ├── test_data_fetchers.py
│   └── test_services.py
├── integration/
│   ├── test_analysis_flow.py
│   └── test_api_endpoints.py
└── e2e/
    └── test_full_analysis.py
```

## 5. 🎯 실행 계획

### Phase 1 (즉시 실행 가능)
1. [ ] 커스텀 예외 클래스 생성
2. [ ] 중복 코드를 mixin/utility로 추출
3. [ ] 타입 힌팅 추가

### Phase 2 (구조 개선)
4. [ ] 설정 관리 중앙화
5. [ ] 서비스 레이어 도입
6. [ ] Repository 패턴 구현

### Phase 3 (패턴 적용)
7. [ ] Strategy 패턴으로 데이터 소스 관리
8. [ ] Observer 패턴으로 진행상황 관리
9. [ ] 의존성 주입 컨테이너 도입

### Phase 4 (테스트)
10. [ ] 단위 테스트 작성
11. [ ] 통합 테스트 작성
12. [ ] E2E 테스트 작성

## 6. 📊 예상 효과

- **코드 중복 감소**: 약 30% 코드량 감소 예상
- **테스트 커버리지**: 0% → 80% 목표
- **유지보수성**: 모듈화로 인한 변경 영향 범위 축소
- **확장성**: 새로운 데이터 소스나 에이전트 추가 용이
- **성능**: 비동기 처리로 분석 속도 2-3배 향상 예상

---

*작성일: 2025-08-02*