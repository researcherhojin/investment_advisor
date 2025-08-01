"""
Terminal Layout Manager

Bloomberg Terminal inspired layout with minimal, professional design.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from .terminal_styles import TerminalTheme


class TerminalLayoutManager:
    """Professional terminal-style layout manager."""
    
    def __init__(self):
        self.theme = TerminalTheme()
    
    def setup_page(self):
        """Setup page configuration and styling."""
        # Inject terminal styles
        self.theme.inject_terminal_styles()
    
    def render_header(self):
        """Render Bloomberg Terminal style header."""
        self.theme.create_terminal_header("AI INVESTMENT TERMINAL")
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render professional sidebar for inputs."""
        with st.sidebar:
            st.markdown('<div class="terminal-title">ANALYSIS CONFIG</div>', unsafe_allow_html=True)
            
            # Market selection
            market = st.selectbox(
                "MARKET",
                options=["미국장", "한국장"],
                index=0
            )
            
            # Ticker input
            ticker = st.text_input(
                "TICKER SYMBOL",
                placeholder="Enter ticker (e.g., AAPL, 005930)"
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
            
            industry = st.selectbox("SECTOR", options=industries)
            
            # Analysis period
            period = st.selectbox(
                "PERIOD (MONTHS)",
                options=[1, 3, 6, 12, 24],
                index=3
            )
            
            st.markdown("---")
            
            # Action buttons
            analyze_button = st.button("🔍 ANALYZE", type="primary", use_container_width=True)
            clear_button = st.button("🗑️ CLEAR", use_container_width=True)
            
            # Advanced options
            with st.expander("ADVANCED OPTIONS"):
                include_recommendations = st.checkbox("Include Recommendations", value=True)
                show_detailed_analysis = st.checkbox("Show Detailed Analysis", value=True)
                export_results = st.checkbox("Enable Export", value=False)
        
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
        # Create ticker display placeholder
        st.markdown("""
        <div class="ticker-display" style="color: #666666;">
            ENTER TICKER TO BEGIN ANALYSIS
        </div>
        """, unsafe_allow_html=True)
        
        # Terminal info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="analysis-section">
                <div class="analysis-header">SYSTEM STATUS</div>
                <div class="analysis-content">
                    AI AGENTS: READY<br>
                    DATA SOURCES: CONNECTED<br>
                    CACHE: ACTIVE<br>
                    VERSION: 2.0
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="analysis-section">
                <div class="analysis-header">SUPPORTED MARKETS</div>
                <div class="analysis-content">
                    US EQUITIES: NYSE, NASDAQ<br>
                    KR EQUITIES: KRX, KOSDAQ<br>
                    ANALYSIS PERIOD: 1M - 24M<br>
                    AI AGENTS: 6 SPECIALISTS
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="analysis-section">
                <div class="analysis-header">ANALYSIS FEATURES</div>
                <div class="analysis-content">
                    TECHNICAL ANALYSIS<br>
                    FUNDAMENTAL ANALYSIS<br>
                    RISK ASSESSMENT<br>
                    INVESTMENT RECOMMENDATION
                </div>
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
        """Display analysis results in terminal style."""
        
        # Display ticker prominently
        company_name = analysis_data.get('stock_info', {}).get('longName', '')
        self.theme.create_ticker_display(ticker, company_name)
        
        # Create main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Final Decision
            self._render_final_decision(final_decision)
            
            # Agent analyses
            self._render_agent_analyses(agent_results)
        
        with col2:
            # Stock info
            self._render_stock_info(analysis_data.get('stock_info', {}))
            
            # Key metrics
            self._render_key_metrics(analysis_data)
        
        # Price chart (full width)
        if not price_history.empty:
            self._render_price_chart(price_history, ticker)
    
    def _render_final_decision(self, decision: str):
        """Render final investment decision."""
        # Extract decision type and confidence
        decision_type = "HOLD"
        if "매수" in decision or "BUY" in decision.upper():
            decision_type = "BUY"
        elif "매도" in decision or "SELL" in decision.upper():
            decision_type = "SELL"
        
        # Status indicator
        status = "positive" if decision_type == "BUY" else "negative" if decision_type == "SELL" else "neutral"
        
        st.markdown(f"""
        <div class="analysis-section">
            <div class="analysis-header">INVESTMENT RECOMMENDATION</div>
            <div class="analysis-content">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <span class="status-indicator {status}"></span>
                    <span style="font-size: 18px; font-weight: bold;">{decision_type}</span>
                </div>
                {decision}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_agent_analyses(self, agent_results: Dict[str, str]):
        """Render AI agent analyses."""
        if not agent_results:
            return
        
        st.markdown('<div class="terminal-title">AGENT ANALYSES</div>', unsafe_allow_html=True)
        
        # Agent mapping for cleaner display
        agent_names = {
            "기업분석가": "COMPANY ANALYST",
            "산업전문가": "INDUSTRY EXPERT", 
            "거시경제전문가": "MACRO ECONOMIST",
            "기술분석가": "TECHNICAL ANALYST",
            "리스크관리자": "RISK MANAGER",
            "중재자": "MEDIATOR"
        }
        
        # Show analyses in tabs for cleaner display
        if len(agent_results) > 1:
            tabs = st.tabs([agent_names.get(agent, agent.upper()) for agent in agent_results.keys()])
            
            for i, (agent, analysis) in enumerate(agent_results.items()):
                with tabs[i]:
                    st.markdown(f"""
                    <div class="analysis-content" style="font-size: 13px; line-height: 1.5;">
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Single analysis
            for agent, analysis in agent_results.items():
                self.theme.create_analysis_section(
                    agent_names.get(agent, agent.upper()),
                    analysis
                )
    
    def _render_stock_info(self, stock_info: Dict[str, Any]):
        """Render stock information grid."""
        if not stock_info:
            return
        
        # Extract key data points
        data_points = {}
        
        # Price data
        if 'currentPrice' in stock_info:
            data_points['PRICE'] = f"${stock_info['currentPrice']:.2f}"
        
        # Valuation metrics
        if 'forwardPE' in stock_info:
            data_points['P/E FWD'] = f"{stock_info['forwardPE']:.1f}"
        if 'priceToBook' in stock_info:
            data_points['P/B'] = f"{stock_info['priceToBook']:.1f}"
        
        # Profitability
        if 'returnOnEquity' in stock_info:
            data_points['ROE'] = f"{stock_info['returnOnEquity']:.1%}"
        if 'profitMargins' in stock_info:
            data_points['MARGIN'] = f"{stock_info['profitMargins']:.1%}"
        
        # Market data
        if 'marketCap' in stock_info:
            market_cap = stock_info['marketCap']
            if market_cap > 1e12:
                data_points['MCAP'] = f"${market_cap/1e12:.1f}T"
            elif market_cap > 1e9:
                data_points['MCAP'] = f"${market_cap/1e9:.1f}B"
            else:
                data_points['MCAP'] = f"${market_cap/1e6:.1f}M"
        
        if data_points:
            self.theme.create_data_grid(data_points, "KEY DATA")
    
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
                metrics['MACD'] = signal
        
        # Fundamental scores
        if 'overall_score' in fundamental:
            score = fundamental['overall_score']
            if isinstance(score, (int, float)):
                metrics['FUND SCORE'] = f"{score:.1f}/10"
        
        if 'growth_score' in fundamental:
            score = fundamental['growth_score']
            if isinstance(score, (int, float)):
                metrics['GROWTH'] = f"{score:.1f}/10"
        
        if metrics:
            self.theme.create_data_grid(metrics, "ANALYSIS METRICS")
    
    def _render_price_chart(self, price_history: pd.DataFrame, ticker: str):
        """Render simple price chart."""
        st.markdown('<div class="terminal-title">PRICE HISTORY</div>', unsafe_allow_html=True)
        
        # Simple line chart with minimal styling
        chart_data = price_history[['Close']].copy()
        chart_data.columns = [ticker]
        
        st.line_chart(
            chart_data,
            height=300,
            use_container_width=True
        )
    
    def display_error(self, error_message: str):
        """Display error in terminal style."""
        st.markdown(f"""
        <div class="analysis-section" style="border-color: #FF4444;">
            <div class="analysis-header" style="background-color: #FF4444; color: #000000;">
                ERROR
            </div>
            <div class="analysis-content">
                {error_message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_warning(self, warning_message: str):
        """Display warning in terminal style."""
        st.markdown(f"""
        <div class="analysis-section" style="border-color: #FF8800;">
            <div class="analysis-header" style="background-color: #FF8800; color: #000000;">
                WARNING
            </div>
            <div class="analysis-content">
                {warning_message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_success(self, success_message: str):
        """Display success in terminal style."""
        st.markdown(f"""
        <div class="analysis-section" style="border-color: #00C851;">
            <div class="analysis-header" style="background-color: #00C851; color: #000000;">
                SUCCESS
            </div>
            <div class="analysis-content">
                {success_message}
            </div>
        </div>
        """, unsafe_allow_html=True)