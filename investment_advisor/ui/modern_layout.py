"""
Modern Layout Manager

Clean, contemporary layout with minimal design and good typography.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from .modern_styles import ModernTheme


class ModernLayoutManager:
    """Modern minimal layout manager with clean design."""
    
    def __init__(self):
        self.theme = ModernTheme()
    
    def setup_page(self):
        """Setup page configuration and styling."""
        # Inject modern styles
        self.theme.inject_modern_styles()
    
    def render_header(self):
        """Render modern header."""
        self.theme.create_header(
            "AI 투자 분석",
            "데이터 기반 지능형 주식 분석"
        )
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render clean sidebar for inputs."""
        with st.sidebar:
            st.markdown("### 분석 설정")
            
            # Market selection
            market = st.selectbox(
                "시장",
                options=["미국장", "한국장"],
                index=0
            )
            
            # Ticker input
            ticker = st.text_input(
                "종목 코드",
                placeholder="종목 코드 입력 (예: AAPL, 005930)"
            ).upper().strip()
            
            # Industry selection
            if market == "미국장":
                industries = [
                    "Technology", "Healthcare", "Financials", "Consumer Discretionary",
                    "Communication Services", "Industrials", "Consumer Staples",
                    "Energy", "Utilities", "Real Estate", "Materials"
                ]
            else:
                industries = [
                    "반도체", "전자", "자동차", "화학", "금융", "통신서비스", 
                    "소프트웨어", "바이오", "에너지", "건설", "식품"
                ]
            
            industry = st.selectbox("산업 섹터", options=industries)
            
            # Analysis period
            period = st.selectbox(
                "분석 기간 (개월)",
                options=[1, 3, 6, 12, 24],
                index=3
            )
            
            st.markdown("---")
            
            # Action buttons
            analyze_button = st.button("🔍 주식 분석", type="primary", use_container_width=True)
            clear_button = st.button("결과 지우기", use_container_width=True)
            
            # Advanced options
            with st.expander("고급 옵션"):
                include_recommendations = st.checkbox("추천 종목 포함", value=True)
                show_detailed_analysis = st.checkbox("상세 분석 표시", value=True)
                export_results = st.checkbox("내보내기 활성화", value=False)
        
        return {
            'ticker': ticker,
            'market': market,
            'industry': industry,
            'period': period,
            'actions': {
                'analyze': analyze_button,
                'clear': clear_button
            },
            'advanced': {
                'include_recommendations': include_recommendations,
                'show_detailed_analysis': show_detailed_analysis,
                'export_results': export_results
            }
        }
    
    def render_main_content(self):
        """Render main content area when no analysis is running."""
        # Welcome message
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h2 style="color: #6C757D; font-weight: 400; margin-bottom: 1rem;">분석 준비 완료</h2>
            <p style="color: #ADB5BD; font-size: 1.1rem;">사이드바에 종목 코드를 입력하여 투자 분석을 시작하세요</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="modern-card">
                <h3 class="card-title">AI 에이전트</h3>
                <div class="card-content">투자의 다양한 측면을 분석하는 전문 AI 에이전트들</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="modern-card">
                <h3 class="card-title">시장 지원</h3>
                <div class="card-content">미국 (NYSE, NASDAQ)과 한국 (KRX, KOSDAQ) 주식 시장 지원</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="modern-card">
                <h3 class="card-title">종합 분석</h3>
                <div class="card-content">기술적 분석, 기본적 분석, 위험 평가를 한 곳에서</div>
            </div>
            """, unsafe_allow_html=True)
    
    def display_analysis_results(
        self,
        ticker: str,
        market: str,
        final_decision: str,
        agent_results: Dict[str, str],
        analysis_data: Dict[str, Any],
        price_history: pd.DataFrame
    ):
        """Display analysis results in modern style."""
        
        # Display ticker prominently
        company_name = analysis_data.get('stock_info', {}).get('longName', '')
        self.theme.create_ticker_display(ticker, company_name)
        
        # Main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Investment decision
            self._render_investment_decision(final_decision)
            
            # Agent analyses in clean tabs
            self._render_agent_analyses(agent_results)
        
        with col2:
            # Key metrics
            self._render_key_metrics(analysis_data)
            
            # Stock info
            self._render_stock_info(analysis_data.get('stock_info', {}))
        
        # Price chart (full width)
        if not price_history.empty:
            self._render_price_chart(price_history, ticker)
    
    def _render_investment_decision(self, decision: str):
        """Render investment decision with modern styling."""
        # Extract decision type
        decision_type = "HOLD"
        status_class = "hold"
        
        if "매수" in decision or "BUY" in decision.upper():
            decision_type = "BUY"
            status_class = "buy"
        elif "매도" in decision or "SELL" in decision.upper():
            decision_type = "SELL"
            status_class = "sell"
        
        # Create decision card with direct HTML
        status_badge_class = f"status-badge {status_class}"
        
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h3 class="card-title">투자 추천</h3>
                <span class="{status_badge_class}">{decision_type}</span>
            </div>
            <div class="card-content">{decision}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_agent_analyses(self, agent_results: Dict[str, str]):
        """Render AI agent analyses in clean tabs."""
        if not agent_results:
            return
        
        st.markdown("### 전문가 분석")
        
        # Agent name mapping
        agent_names = {
            "기업분석가": "기업 분석가",
            "산업전문가": "산업 전문가", 
            "거시경제전문가": "거시경제 전문가",
            "기술분석가": "기술 분석가",
            "리스크관리자": "리스크 관리자",
            "중재자": "중재자"
        }
        
        # Create tabs for different analyses
        if len(agent_results) > 1:
            tab_names = [agent_names.get(agent, agent) for agent in agent_results.keys()]
            tabs = st.tabs(tab_names)
            
            for i, (agent, analysis) in enumerate(agent_results.items()):
                with tabs[i]:
                    st.markdown(f"""
                    <div style="font-size: 0.95rem; line-height: 1.7; color: #495057; padding: 1rem 0;">
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Single analysis
            for agent, analysis in agent_results.items():
                agent_name = agent_names.get(agent, agent)
                st.markdown(f"""
                <div class="modern-card">
                    <h3 class="card-title">{agent_name}</h3>
                    <div class="card-content">{analysis}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]):
        """Render key analysis metrics."""
        technical = analysis_data.get('technical_analysis', {})
        fundamental = analysis_data.get('fundamental_analysis', {})
        
        metrics = {}
        
        # Technical indicators
        if 'rsi' in technical:
            rsi = technical['rsi']
            if isinstance(rsi, (int, float)):
                metrics['RSI'] = f"{rsi:.1f}"
        
        if 'macd_signal' in technical:
            signal = technical['macd_signal']
            if signal in ['BUY', 'SELL', 'HOLD']:
                metrics['MACD Signal'] = signal
        
        # Fundamental scores
        if 'overall_score' in fundamental:
            score = fundamental['overall_score']
            if isinstance(score, (int, float)):
                metrics['Fundamental Score'] = f"{score:.1f}/10"
        
        if 'growth_score' in fundamental:
            score = fundamental['growth_score']
            if isinstance(score, (int, float)):
                metrics['Growth Score'] = f"{score:.1f}/10"
        
        if metrics:
            self.theme.create_data_grid(metrics, "주요 지표")
    
    def _render_stock_info(self, stock_info: Dict[str, Any]):
        """Render stock information."""
        if not stock_info:
            return
        
        # Extract key data points
        data_points = {}
        
        # Price data
        if 'currentPrice' in stock_info:
            data_points['현재가'] = f"${stock_info['currentPrice']:.2f}"
        
        # Valuation metrics
        if 'forwardPE' in stock_info:
            data_points['P/E 비율'] = f"{stock_info['forwardPE']:.1f}"
        if 'priceToBook' in stock_info:
            data_points['P/B 비율'] = f"{stock_info['priceToBook']:.1f}"
        
        # Profitability
        if 'returnOnEquity' in stock_info:
            data_points['ROE'] = f"{stock_info['returnOnEquity']:.1%}"
        if 'profitMargins' in stock_info:
            data_points['순이익률'] = f"{stock_info['profitMargins']:.1%}"
        
        # Market cap
        if 'marketCap' in stock_info:
            market_cap = stock_info['marketCap']
            if market_cap > 1e12:
                data_points['시가총액'] = f"${market_cap/1e12:.1f}T"
            elif market_cap > 1e9:
                data_points['시가총액'] = f"${market_cap/1e9:.1f}B"
            else:
                data_points['시가총액'] = f"${market_cap/1e6:.1f}M"
        
        if data_points:
            self.theme.create_data_grid(data_points, "종목 정보")
    
    def _render_price_chart(self, price_history: pd.DataFrame, ticker: str):
        """Render clean price chart."""
        st.markdown("### 주가 차트")
        
        # Simple, clean line chart
        chart_data = price_history[['Close']].copy()
        chart_data.columns = [ticker]
        
        st.line_chart(
            chart_data,
            height=400,
            use_container_width=True
        )
    
    def display_error(self, error_message: str):
        """Display error message."""
        self.theme.create_alert(error_message, "error")
    
    def display_warning(self, warning_message: str):
        """Display warning message."""
        self.theme.create_alert(warning_message, "warning")
    
    def display_success(self, success_message: str):
        """Display success message."""
        self.theme.create_alert(success_message, "success")