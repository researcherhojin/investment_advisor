"""
News Analysis Agent

Analyzes news, social media sentiment, and market events.
"""

from typing import Any, Dict, List
import logging
from datetime import datetime, timedelta
import re

from langchain.prompts import PromptTemplate
from pydantic import Field

from .base import InvestmentAgent
from ..core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


class NewsAnalysisAgent(InvestmentAgent):
    """Agent specialized in news and media sentiment analysis."""
    
    name: str = "뉴스분석가"
    description: str = "뉴스, 소셜 미디어, 시장 이벤트를 분석하는 전문가"
    
    # Prompt template for news analysis
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["ticker", "market", "company_name", "news_data"],
        template="""당신은 금융 뉴스와 미디어 분석 전문가입니다.

종목: {ticker}
회사명: {company_name}
시장: {market}

뉴스 및 미디어 데이터:
{news_data}

다음 관점에서 분석해주세요:

1. **주요 뉴스 분석**
   - 최근 중요 뉴스 및 공시 사항
   - 뉴스의 긍정/부정 영향도 평가
   - 시장 반응 예상

2. **감성 분석**
   - 전반적인 미디어 톤 (긍정/중립/부정)
   - 감성 변화 추이
   - 주요 키워드 및 테마

3. **이벤트 영향 평가**
   - 예정된 주요 이벤트 (실적 발표, 제품 출시 등)
   - 이벤트의 잠재적 영향
   - 시장 기대치 vs 실제 가능성

4. **소셜 미디어 및 여론**
   - 소셜 미디어 언급량 추이
   - 투자자 커뮤니티 반응
   - 루머 및 추측성 정보 평가

5. **뉴스 기반 투자 시그널**
   - 뉴스 모멘텀 (증가/감소)
   - 정보의 신뢰성 평가
   - 단기/중기 영향 전망

구체적인 뉴스 내용과 함께 투자 관점에서의 해석을 제공해주세요.
"""
    )
    
    def _run(self, ticker: str, market: str) -> str:
        """
        Run news analysis for the given ticker.
        
        Args:
            ticker: Stock ticker symbol
            market: Market identifier (한국장/미국장)
            
        Returns:
            News analysis report
        """
        try:
            logger.info(f"Starting news analysis for {ticker} in {market}")
            
            # Mock company name (in real implementation, fetch from stock info)
            company_name = self._get_company_name(ticker, market)
            
            # Collect news data
            news_data = self._collect_news_data(ticker, company_name, market)
            
            # Prepare context for analysis
            context = {
                "ticker": ticker,
                "market": market,
                "company_name": company_name,
                "news_data": self._format_news_data(news_data)
            }
            
            # Generate analysis using LLM
            analysis = self.llm.predict(self.prompt.format(**context))
            
            # Add metadata
            analysis += f"\n\n---\n📰 분석 시점: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            analysis += f"\n📊 뉴스 감성 점수: {news_data.get('sentiment_score', 'N/A')}"
            analysis += f"\n🎯 신뢰도: {self._calculate_confidence(news_data)}"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in news analysis: {str(e)}")
            raise AnalysisError(f"뉴스 분석 실패: {str(e)}")
    
    def _get_company_name(self, ticker: str, market: str) -> str:
        """Get company name for the ticker."""
        # In real implementation, this would fetch from stock data
        # For now, using a simple mapping
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "035720": "카카오",
            "035420": "NAVER"
        }
        
        return company_names.get(ticker, ticker)
    
    def _collect_news_data(self, ticker: str, company_name: str, market: str) -> Dict[str, Any]:
        """Collect news and media data."""
        news_data = {}
        
        try:
            # Mock news data collection
            # In real implementation, this would:
            # 1. Fetch from news APIs (Bloomberg, Reuters, etc.)
            # 2. Scrape financial news websites
            # 3. Get social media mentions
            # 4. Analyze Reddit/Twitter sentiment
            
            # Recent news articles (mock data)
            news_data['recent_articles'] = self._get_mock_news_articles(ticker, company_name)
            
            # Sentiment analysis
            news_data['sentiment_analysis'] = self._analyze_news_sentiment(
                news_data['recent_articles']
            )
            
            # Social media metrics
            news_data['social_metrics'] = self._get_mock_social_metrics(ticker)
            
            # Upcoming events
            news_data['upcoming_events'] = self._get_mock_upcoming_events(ticker, company_name)
            
            # News volume trend
            news_data['news_volume'] = self._analyze_news_volume_trend()
            
            # Calculate overall sentiment score
            news_data['sentiment_score'] = self._calculate_overall_sentiment(news_data)
            
        except Exception as e:
            logger.warning(f"Error collecting news data: {e}")
            news_data['error'] = str(e)
        
        return news_data
    
    def _get_mock_news_articles(self, ticker: str, company_name: str) -> List[Dict[str, Any]]:
        """Get mock news articles for demonstration."""
        # In production, this would fetch real news
        base_date = datetime.now()
        
        articles = [
            {
                "title": f"{company_name} 4분기 실적 예상치 상회 전망",
                "source": "Financial Times",
                "date": (base_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "애널리스트들은 강한 수요와 비용 절감으로 실적 개선 예상",
                "sentiment": "positive",
                "relevance": 0.95
            },
            {
                "title": f"{company_name} 신제품 출시 임박, 시장 기대감 상승",
                "source": "Reuters",
                "date": (base_date - timedelta(days=2)).strftime("%Y-%m-%d"),
                "summary": "혁신적인 기능으로 시장 점유율 확대 기대",
                "sentiment": "positive",
                "relevance": 0.88
            },
            {
                "title": f"규제 당국, {company_name} 관련 조사 착수",
                "source": "Bloomberg",
                "date": (base_date - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "독점 관련 우려로 당국 조사, 단기 불확실성 증가",
                "sentiment": "negative",
                "relevance": 0.82
            },
            {
                "title": f"{company_name} CEO, 장기 성장 전략 발표",
                "source": "CNBC",
                "date": (base_date - timedelta(days=5)).strftime("%Y-%m-%d"),
                "summary": "AI 및 클라우드 투자 확대, 5년 내 매출 2배 목표",
                "sentiment": "positive",
                "relevance": 0.90
            }
        ]
        
        return articles
    
    def _analyze_news_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from news articles."""
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for article in articles:
            sentiment = article.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1
        
        total = len(articles)
        
        return {
            "positive_ratio": sentiment_counts["positive"] / total if total > 0 else 0,
            "negative_ratio": sentiment_counts["negative"] / total if total > 0 else 0,
            "neutral_ratio": sentiment_counts["neutral"] / total if total > 0 else 0,
            "dominant_sentiment": max(sentiment_counts, key=sentiment_counts.get),
            "total_articles": total
        }
    
    def _get_mock_social_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get mock social media metrics."""
        import random
        
        # Generate some realistic-looking metrics
        base_mentions = random.randint(1000, 10000)
        
        return {
            "twitter_mentions_24h": base_mentions,
            "twitter_sentiment": random.choice(["positive", "neutral", "mixed"]),
            "reddit_mentions_24h": int(base_mentions * 0.3),
            "reddit_top_posts": [
                f"DD: Why ${ticker} is undervalued",
                f"${ticker} technical analysis - breakout incoming?",
                f"Thoughts on ${ticker} earnings?"
            ],
            "stocktwits_sentiment": {
                "bullish": random.randint(55, 75),
                "bearish": random.randint(25, 45)
            },
            "google_trends_score": random.randint(40, 80),
            "mention_growth_7d": f"{random.randint(-20, 50)}%"
        }
    
    def _get_mock_upcoming_events(self, ticker: str, company_name: str) -> List[Dict[str, str]]:
        """Get mock upcoming events."""
        base_date = datetime.now()
        
        events = [
            {
                "date": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "event": "Q4 실적 발표",
                "importance": "high",
                "expected_impact": "주가 변동성 증가 예상"
            },
            {
                "date": (base_date + timedelta(days=14)).strftime("%Y-%m-%d"),
                "event": "신제품 발표 이벤트",
                "importance": "medium",
                "expected_impact": "긍정적 반응 예상"
            },
            {
                "date": (base_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                "event": "연례 주주총회",
                "importance": "medium",
                "expected_impact": "경영 전략 발표 주목"
            }
        ]
        
        return events
    
    def _analyze_news_volume_trend(self) -> Dict[str, Any]:
        """Analyze news volume trend."""
        import random
        
        # Mock news volume data
        current_volume = random.randint(50, 200)
        avg_volume = random.randint(40, 100)
        
        return {
            "current_24h": current_volume,
            "average_24h": avg_volume,
            "volume_ratio": current_volume / avg_volume,
            "trend": "increasing" if current_volume > avg_volume * 1.2 else 
                    "decreasing" if current_volume < avg_volume * 0.8 else "stable",
            "unusual_activity": current_volume > avg_volume * 1.5
        }
    
    def _calculate_overall_sentiment(self, news_data: Dict[str, Any]) -> float:
        """Calculate overall sentiment score (0-100)."""
        score = 50  # Neutral baseline
        
        # News sentiment component
        sentiment = news_data.get('sentiment_analysis', {})
        score += (sentiment.get('positive_ratio', 0) - sentiment.get('negative_ratio', 0)) * 30
        
        # Social media component
        social = news_data.get('social_metrics', {})
        if social.get('twitter_sentiment') == 'positive':
            score += 10
        elif social.get('twitter_sentiment') == 'negative':
            score -= 10
            
        # StockTwits sentiment
        stocktwits = social.get('stocktwits_sentiment', {})
        bullish_pct = stocktwits.get('bullish', 50)
        score += (bullish_pct - 50) * 0.4
        
        # News volume (high volume can be good or bad, so smaller weight)
        volume = news_data.get('news_volume', {})
        if volume.get('unusual_activity'):
            # Combine with sentiment direction
            if sentiment.get('dominant_sentiment') == 'positive':
                score += 5
            elif sentiment.get('dominant_sentiment') == 'negative':
                score -= 5
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _format_news_data(self, data: Dict[str, Any]) -> str:
        """Format news data for prompt."""
        formatted = []
        
        # Overall sentiment score
        sentiment_score = data.get('sentiment_score', 50)
        sentiment_desc = "매우 부정적" if sentiment_score < 20 else \
                        "부정적" if sentiment_score < 40 else \
                        "중립" if sentiment_score < 60 else \
                        "긍정적" if sentiment_score < 80 else "매우 긍정적"
        
        formatted.append(f"전체 뉴스 감성: {sentiment_score:.0f}/100 ({sentiment_desc})")
        formatted.append("")
        
        # Recent articles
        if 'recent_articles' in data:
            formatted.append("최근 주요 뉴스:")
            for article in data['recent_articles'][:5]:  # Top 5 articles
                formatted.append(f"\n[{article['date']}] {article['title']}")
                formatted.append(f"  출처: {article['source']}")
                formatted.append(f"  요약: {article['summary']}")
                formatted.append(f"  감성: {article['sentiment']} (관련도: {article['relevance']:.0%})")
            formatted.append("")
        
        # Sentiment analysis
        if 'sentiment_analysis' in data:
            sent = data['sentiment_analysis']
            formatted.append("뉴스 감성 분석:")
            formatted.append(f"- 긍정: {sent.get('positive_ratio', 0):.0%}")
            formatted.append(f"- 부정: {sent.get('negative_ratio', 0):.0%}")
            formatted.append(f"- 중립: {sent.get('neutral_ratio', 0):.0%}")
            formatted.append(f"- 주요 감성: {sent.get('dominant_sentiment', 'N/A')}")
            formatted.append("")
        
        # Social media metrics
        if 'social_metrics' in data:
            social = data['social_metrics']
            formatted.append("소셜 미디어 지표:")
            formatted.append(f"- Twitter 언급 (24h): {social.get('twitter_mentions_24h', 0):,}")
            formatted.append(f"- Reddit 언급 (24h): {social.get('reddit_mentions_24h', 0):,}")
            formatted.append(f"- StockTwits: 강세 {social.get('stocktwits_sentiment', {}).get('bullish', 0)}% / 약세 {social.get('stocktwits_sentiment', {}).get('bearish', 0)}%")
            formatted.append(f"- 언급 증가율 (7일): {social.get('mention_growth_7d', 'N/A')}")
            formatted.append("")
        
        # Upcoming events
        if 'upcoming_events' in data:
            formatted.append("예정된 주요 이벤트:")
            for event in data['upcoming_events']:
                formatted.append(f"- {event['date']}: {event['event']} (중요도: {event['importance']})")
                formatted.append(f"  예상 영향: {event['expected_impact']}")
            formatted.append("")
        
        # News volume
        if 'news_volume' in data:
            volume = data['news_volume']
            formatted.append("뉴스 볼륨 분석:")
            formatted.append(f"- 현재 (24h): {volume.get('current_24h', 0)}건")
            formatted.append(f"- 평균 대비: {volume.get('volume_ratio', 1):.1f}x")
            formatted.append(f"- 추세: {volume.get('trend', 'N/A')}")
            if volume.get('unusual_activity'):
                formatted.append("- ⚠️ 비정상적으로 높은 뉴스 활동 감지")
        
        return "\n".join(formatted)
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> str:
        """Calculate confidence level based on data quality and volume."""
        if 'error' in data:
            return "낮음"
        
        # Check data completeness and quality
        confidence_factors = [
            len(data.get('recent_articles', [])) >= 3,
            'sentiment_analysis' in data,
            'social_metrics' in data,
            data.get('sentiment_analysis', {}).get('total_articles', 0) >= 5,
            data.get('news_volume', {}).get('current_24h', 0) >= 20
        ]
        
        confidence_score = sum(confidence_factors) / len(confidence_factors)
        
        if confidence_score >= 0.8:
            return "높음"
        elif confidence_score >= 0.5:
            return "보통"
        else:
            return "낮음"