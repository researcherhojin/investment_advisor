"""
Type definitions for Investment Advisor system

Provides strongly typed data structures for better type safety and IDE support.
"""

from typing import TypedDict, Literal, Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class Market(str, Enum):
    """Supported markets"""
    US = "미국장"
    KOREA = "한국장"


class Decision(str, Enum):
    """Investment decisions"""
    STRONG_BUY = "강력매수"
    BUY = "매수"
    HOLD = "보유"
    SELL = "매도"
    STRONG_SELL = "강력매도"


class Confidence(str, Enum):
    """Confidence levels"""
    HIGH = "높음"
    MEDIUM = "보통"
    LOW = "낮음"


class StockInfo(TypedDict, total=False):
    """Stock information data structure"""
    ticker: str
    currentPrice: float
    marketCap: int
    PER: Optional[float]
    PBR: Optional[float]
    ROE: Optional[float]
    dividendYield: Optional[float]
    beta: Optional[float]
    volume: int
    EPS: Optional[float]
    revenue: Optional[int]
    profitMargin: Optional[float]
    longName: Optional[str]
    shortName: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    country: str
    employees: Optional[int]
    
    # Korean field names
    현재가: Optional[float]
    시가총액: Optional[int]
    배당수익률: Optional[float]
    베타: Optional[float]
    거래량: Optional[int]
    회사명: Optional[str]
    섹터: Optional[str]
    산업: Optional[str]
    국가: Optional[str]
    직원수: Optional[int]
    
    # 52-week range
    fiftyTwoWeekHigh: Optional[float]
    fiftyTwoWeekLow: Optional[float]
    
    # Data quality indicators
    source: Optional[str]
    data_quality: Optional[str]


class TechnicalIndicators(TypedDict, total=False):
    """Technical analysis indicators"""
    rsi: float
    macd: float
    macd_signal: float
    macd_diff: float
    sma_20: float
    sma_50: float
    sma_200: float
    bb_upper: float
    bb_lower: float
    bb_middle: float
    volume_avg_20: float
    support_level: float
    resistance_level: float
    volatility: float


class FundamentalScores(TypedDict):
    """Fundamental analysis scores"""
    overall_score: float
    growth_score: float
    value_score: float
    profitability_score: float
    financial_health_score: float


class RiskMetrics(TypedDict, total=False):
    """Risk analysis metrics"""
    beta: float
    volatility: float
    max_drawdown: float
    var_95: float
    sharpe_ratio: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]


class AgentAnalysis(TypedDict):
    """Individual agent analysis result"""
    agent_name: str
    analysis: str
    confidence: Confidence
    key_points: List[str]
    timestamp: datetime


class AnalysisResult(TypedDict):
    """Complete analysis result"""
    ticker: str
    market: Market
    decision: Decision
    confidence: Confidence
    target_price: Optional[float]
    stop_loss: Optional[float]
    time_horizon: Literal["단기", "중기", "장기"]
    
    # Detailed components
    stock_info: StockInfo
    technical_indicators: TechnicalIndicators
    fundamental_scores: FundamentalScores
    risk_metrics: RiskMetrics
    
    # Agent analyses
    agent_results: Dict[str, AgentAnalysis]
    final_recommendation: str
    
    # Metadata
    timestamp: datetime
    analysis_id: str
    version: str


class PriceTarget(TypedDict):
    """Price target information"""
    buy_price: float
    target_price: float
    stop_loss_price: float
    time_frame: Literal["1M", "3M", "6M", "12M"]
    confidence: float


class SectorData(TypedDict):
    """Sector performance data"""
    sector: str
    performance: float
    trend: Literal["상승", "하락", "보합"]
    relative_strength: float


class EconomicIndicator(TypedDict):
    """Economic indicator data"""
    name: str
    value: float
    unit: str
    change: float
    trend: Literal["상승", "하락", "보합"]
    impact: Literal["긍정적", "부정적", "중립적"]


class MarketCondition(TypedDict):
    """Overall market condition"""
    sentiment: Literal["강세", "약세", "중립"]
    volatility: Literal["높음", "보통", "낮음"]
    trend: Literal["상승", "하락", "횡보"]
    key_factors: List[str]


# Request/Response types for API
class AnalysisRequest(TypedDict):
    """Analysis request structure"""
    ticker: str
    market: Market
    industry: str
    period: int
    advanced_options: Dict[str, bool]


class AnalysisResponse(TypedDict):
    """Analysis response structure"""
    success: bool
    data: Optional[AnalysisResult]
    error: Optional[str]
    error_code: Optional[str]
    timestamp: datetime


# Utility type guards
def is_valid_market(value: str) -> bool:
    """Check if value is a valid market"""
    return value in [market.value for market in Market]


def is_valid_decision(value: str) -> bool:
    """Check if value is a valid decision"""
    return value in [decision.value for decision in Decision]


def is_valid_confidence(value: str) -> bool:
    """Check if value is a valid confidence level"""
    return value in [confidence.value for confidence in Confidence]