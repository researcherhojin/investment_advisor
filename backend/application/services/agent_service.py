"""
AI Agent Application Service

Service layer for coordinating AI agent operations.
Bridges the gap between domain logic and infrastructure.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID

import structlog
from openai import AsyncOpenAI

from domain.entities.analysis import AgentType, AnalysisSession
from domain.entities.stock import Stock
from core.config import get_settings
from .streamlit_agent_adapter import StreamlitAgentAdapter

logger = structlog.get_logger(__name__)


class AgentService:
    """
    Application service for AI agent operations.
    
    Handles the execution of individual AI agents and manages
    their interaction with external AI services.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.streamlit_adapter = StreamlitAgentAdapter()
        
        # Agent prompts (migrated from legacy system)
        self.agent_prompts = {
            AgentType.COMPANY_ANALYST: self._get_company_analyst_prompt(),
            AgentType.INDUSTRY_EXPERT: self._get_industry_expert_prompt(),
            AgentType.MACROECONOMIST: self._get_macroeconomist_prompt(),
            AgentType.TECHNICAL_ANALYST: self._get_technical_analyst_prompt(),
            AgentType.RISK_MANAGER: self._get_risk_manager_prompt(),
            AgentType.MEDIATOR: self._get_mediator_prompt(),
        }
        
        # Map AgentType enum to streamlit agent types
        self.agent_type_map = {
            AgentType.COMPANY_ANALYST: "company_analyst",
            AgentType.INDUSTRY_EXPERT: "industry_expert",
            AgentType.MACROECONOMIST: "macroeconomist",
            AgentType.TECHNICAL_ANALYST: "technical_analyst",
            AgentType.RISK_MANAGER: "risk_manager",
            AgentType.MEDIATOR: "mediator",
        }
    
    async def execute_agent(
        self,
        agent_type: AgentType,
        stock: Stock,
        session: AnalysisSession,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific AI agent analysis.
        
        Args:
            agent_type: Type of agent to execute
            stock: Stock to analyze
            session: Analysis session context
            additional_context: Additional context for the agent
            
        Returns:
            Dictionary containing analysis result and metadata
        """
        logger.info(
            "Executing AI agent",
            agent_type=agent_type.value,
            stock_ticker=stock.ticker,
            session_id=session.id
        )
        
        try:
            # Determine if we should use Streamlit agent or OpenAI
            use_streamlit_agents = self.settings.use_streamlit_agents
            
            if use_streamlit_agents:
                # Use Streamlit agent adapter
                result = await self._execute_streamlit_agent(agent_type, stock, session, additional_context)
            else:
                # Use OpenAI directly
                # Prepare context for the agent
                context = await self._prepare_agent_context(stock, session, additional_context)
                
                # Get agent prompt
                prompt = self.agent_prompts[agent_type]
                
                # Format prompt with context
                formatted_prompt = await self._format_prompt(prompt, context)
                
                # Execute agent using OpenAI
                result = await self._execute_openai_agent(formatted_prompt, agent_type)
                
                # Process and validate result
                result = await self._process_agent_result(result, agent_type)
            
            logger.info(
                "Agent execution completed",
                agent_type=agent_type.value,
                stock_ticker=stock.ticker,
                confidence=result.get("confidence"),
                source=result.get("source", "openai")
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Agent execution failed",
                agent_type=agent_type.value,
                stock_ticker=stock.ticker,
                session_id=session.id,
                error=str(e),
                exc_info=e
            )
            raise
    
    async def _prepare_agent_context(
        self,
        stock: Stock,
        session: AnalysisSession,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare context information for the agent."""
        context = {
            "stock": {
                "ticker": stock.ticker,
                "name": stock.name,
                "market": stock.market,
                "sector": stock.sector,
                "industry": stock.industry,
                "exchange": stock.exchange,
                "currency": stock.currency
            },
            "analysis": {
                "period_months": session.analysis_period,
                "session_id": str(session.id),
                "started_at": session.started_at.isoformat()
            },
            "market_context": {
                "analysis_date": datetime.utcnow().isoformat(),
                "market_type": "한국 시장" if stock.is_korean_stock else "미국 시장"
            }
        }
        
        # Add additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # TODO: Fetch additional data from repositories
        # - Price history
        # - Financial data
        # - Economic indicators
        # This will be implemented when repository implementations are ready
        
        return context
    
    async def _format_prompt(self, prompt_template: str, context: Dict[str, Any]) -> str:
        """Format prompt template with context data."""
        try:
            return prompt_template.format(**context)
        except KeyError as e:
            logger.warning(
                "Missing context key in prompt formatting",
                missing_key=str(e),
                available_keys=list(context.keys())
            )
            # Return template with available context
            return prompt_template.format(**{k: v for k, v in context.items() if isinstance(v, (str, int, float))})
    
    async def _execute_openai_agent(self, prompt: str, agent_type: AgentType) -> str:
        """Execute agent using OpenAI API."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"당신은 전문적인 {agent_type.value}입니다. 정확하고 객관적인 분석을 제공해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.settings.openai_temperature,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(
                "OpenAI API call failed",
                agent_type=agent_type.value,
                error=str(e)
            )
            raise
    
    async def _process_agent_result(
        self,
        raw_result: str,
        agent_type: AgentType
    ) -> Dict[str, Any]:
        """Process and validate agent result."""
        # Basic processing
        content = raw_result.strip()
        
        # Calculate confidence based on content analysis
        confidence = self._calculate_confidence(content, agent_type)
        
        # TODO: Add more sophisticated result processing
        # - Extract structured data
        # - Validate recommendations
        # - Parse numerical values
        
        return {
            "content": content,
            "confidence": confidence,
            "agent_type": agent_type.value,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_confidence(self, content: str, agent_type: AgentType) -> Decimal:
        """Calculate confidence score based on content analysis."""
        # Simple heuristic-based confidence calculation
        confidence_indicators = {
            "확실": 0.9,
            "명확": 0.8,
            "가능성이 높": 0.7,
            "예상": 0.6,
            "추정": 0.5,
            "불확실": 0.3,
            "어려움": 0.2
        }
        
        content_lower = content.lower()
        confidence_scores = []
        
        for indicator, score in confidence_indicators.items():
            if indicator in content_lower:
                confidence_scores.append(score)
        
        if confidence_scores:
            # Average of found indicators
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            # Default confidence based on agent type
            default_confidences = {
                AgentType.COMPANY_ANALYST: 0.8,
                AgentType.INDUSTRY_EXPERT: 0.7,
                AgentType.MACROECONOMIST: 0.6,
                AgentType.TECHNICAL_ANALYST: 0.75,
                AgentType.RISK_MANAGER: 0.85,
                AgentType.MEDIATOR: 0.8,
            }
            avg_confidence = default_confidences.get(agent_type, 0.7)
        
        # Consider content length (longer analysis might be more thorough)
        length_bonus = min(0.1, len(content) / 5000)  # Up to 0.1 bonus for long content
        
        final_confidence = min(1.0, avg_confidence + length_bonus)
        return Decimal(str(round(final_confidence, 2)))
    
    # Agent prompt templates (migrated from legacy system)
    def _get_company_analyst_prompt(self) -> str:
        return """
        당신은 전문 기업분석가입니다. 다음 기업에 대한 종합적인 분석을 수행해주세요.

        기업 정보:
        - 티커: {stock[ticker]}
        - 기업명: {stock[name]}
        - 시장: {market_context[market_type]}
        - 섹터: {stock[sector]}
        - 산업: {stock[industry]}

        분석 기간: {analysis[period_months]}개월

        다음 관점에서 상세히 분석해주세요:
        1. 재무 건전성 (매출, 순이익, 부채비율, ROE 등)
        2. 성장성 (매출 성장률, 시장 점유율 확대)
        3. 수익성 (마진율, 효율성 지표)
        4. 경쟁 우위 (차별화 요소, 브랜드 파워)
        5. 경영진 및 거버넌스
        6. 향후 전망 및 리스크 요인

        최종적으로 투자 관점에서의 의견을 제시해주세요.
        """
    
    async def _execute_streamlit_agent(
        self,
        agent_type: AgentType,
        stock: Stock,
        session: AnalysisSession,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute agent using Streamlit adapter."""
        # Get streamlit agent type
        streamlit_agent_type = self.agent_type_map.get(agent_type)
        if not streamlit_agent_type:
            raise ValueError(f"No Streamlit agent mapping for {agent_type}")
        
        # Convert market format if needed
        market = stock.market
        if stock.market == "US":
            market = "미국장"
        elif stock.market == "KR":
            market = "한국장"
        
        # Execute agent
        result = await self.streamlit_adapter.execute_agent(
            agent_type=streamlit_agent_type,
            ticker=stock.ticker,
            industry=stock.industry or "Technology",
            market=market,
            additional_context=additional_context
        )
        
        # Format result to match expected structure
        if result.get("success"):
            return {
                "content": result.get("content", ""),
                "confidence": Decimal(str(result.get("confidence", 0.7))),
                "agent_type": agent_type.value,
                "processed_at": result.get("timestamp", datetime.utcnow().isoformat()),
                "recommendation": result.get("recommendation", "HOLD"),
                "source": "streamlit_agent"
            }
        else:
            # Handle failure
            raise Exception(f"Streamlit agent failed: {result.get('error', 'Unknown error')}")
    
    def _get_industry_expert_prompt(self) -> str:
        return """
        당신은 산업 전문가입니다. 다음 기업이 속한 산업에 대한 전문적인 분석을 제공해주세요.

        분석 대상:
        - 기업: {stock[name]} ({stock[ticker]})
        - 섹터: {stock[sector]}
        - 산업: {stock[industry]}
        - 시장: {market_context[market_type]}

        다음 관점에서 분석해주세요:
        1. 산업 현황 및 동향
        2. 성장 전망 및 시장 규모
        3. 주요 경쟁업체 분석
        4. 산업 내 해당 기업의 위치
        5. 기술 변화 및 혁신 동향
        6. 규제 환경 및 정책 영향
        7. 산업 리스크 요인

        산업 관점에서 해당 기업의 투자 매력도를 평가해주세요.
        """
    
    def _get_macroeconomist_prompt(self) -> str:
        return """
        당신은 거시경제 전문가입니다. 현재 경제 환경이 다음 기업에 미치는 영향을 분석해주세요.

        기업 정보:
        - 기업: {stock[name]} ({stock[ticker]})
        - 시장: {market_context[market_type]}
        - 섹터: {stock[sector]}

        다음 거시경제 요인들을 분석해주세요:
        1. 현재 경제 상황 (성장률, 인플레이션, 실업률)
        2. 통화정책 (금리 정책, 유동성)
        3. 재정정책 영향
        4. 환율 동향 (특히 미국-한국 관계)
        5. 국제 무역 및 지정학적 리스크
        6. 원자재 가격 동향
        7. 소비자 심리 및 기업 투자

        이러한 거시경제 환경이 해당 기업과 섹터에 미치는 영향을 평가하고,
        투자 관점에서의 시사점을 제시해주세요.
        """
    
    def _get_technical_analyst_prompt(self) -> str:
        return """
        당신은 기술적 분석 전문가입니다. 다음 종목에 대한 기술적 분석을 수행해주세요.

        종목 정보:
        - 티커: {stock[ticker]}
        - 기업명: {stock[name]}
        - 시장: {market_context[market_type]}

        다음 기술적 지표들을 분석해주세요:
        1. 가격 동향 및 추세선
        2. 이동평균선 분석 (단기, 중기, 장기)
        3. 거래량 분석
        4. 모멘텀 지표 (RSI, MACD, 스토캐스틱)
        5. 변동성 지표 (볼린저 밴드, ATR)
        6. 지지선과 저항선
        7. 차트 패턴 분석

        기술적 관점에서:
        - 현재 매매 타이밍 평가
        - 목표가 및 손절가 제시
        - 단기/중기 전망
        - 주요 변곡점 및 주의사항

        을 포함하여 분석해주세요.
        """
    
    def _get_risk_manager_prompt(self) -> str:
        return """
        당신은 리스크 관리 전문가입니다. 다음 투자에 대한 종합적인 리스크 분석을 수행해주세요.

        투자 대상:
        - 기업: {stock[name]} ({stock[ticker]})
        - 시장: {market_context[market_type]}
        - 섹터: {stock[sector]}

        다음 리스크 요인들을 평가해주세요:

        1. 기업 고유 리스크:
           - 재무 리스크 (부채, 유동성)
           - 운영 리스크 (사업 모델, 경쟁)
           - 거버넌스 리스크

        2. 산업 리스크:
           - 산업 주기성
           - 기술 변화 리스크
           - 규제 리스크

        3. 시장 리스크:
           - 주식시장 변동성
           - 금리 리스크
           - 환율 리스크

        4. 거시경제 리스크:
           - 경기 침체 리스크
           - 인플레이션 리스크
           - 지정학적 리스크

        각 리스크의 발생 가능성과 영향도를 평가하고,
        리스크 관리 방안 및 투자 권고사항을 제시해주세요.
        """
    
    def _get_mediator_prompt(self) -> str:
        return """
        당신은 투자 중재자입니다. 여러 전문가들의 분석을 종합하여 최종 투자 의견을 제시해주세요.

        분석 대상:
        - 기업: {stock[name]} ({stock[ticker]})
        - 시장: {market_context[market_type]}

        전문가들의 분석 결과:
        {agent_analyses}

        각 전문가의 의견을 종합적으로 검토하여:

        1. 주요 합의점과 이견 사항 정리
        2. 각 분석의 신뢰도 및 근거 평가
        3. 종합적인 투자 의견 도출:
           - 매수/보유/매도 권고
           - 목표가 (가능한 경우)
           - 투자 기간 권고
           - 리스크 수준 평가

        4. 투자 결정의 핵심 근거 및 주의사항

        최종 의견은 명확하고 실행 가능한 투자 권고안 형태로 제시해주세요.
        """