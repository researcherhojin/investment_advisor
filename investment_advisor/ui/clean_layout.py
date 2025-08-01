"""
Clean Layout Manager

Ultra-clean, professional layout with excellent UX design.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from .clean_styles import CleanTheme


class CleanLayoutManager:
    """Clean professional layout manager."""
    
    def __init__(self):
        self.theme = CleanTheme()
    
    def setup_page(self):
        """Setup page configuration and styling."""
        self.theme.inject_clean_styles()
    
    def render_header(self):
        """Render clean header."""
        self.theme.create_header(
            "AI 투자 분석",
            "데이터 기반 지능형 주식 분석 플랫폼"
        )
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render clean sidebar."""
        with st.sidebar:
            st.markdown("### 📊 분석 설정")
            st.markdown("---")
            
            # Market selection
            market = st.selectbox(
                "🌍 시장 선택",
                options=["미국장", "한국장"],
                index=0
            )
            
            # Ticker input
            ticker = st.text_input(
                "📈 종목 코드",
                placeholder="예: AAPL, TSLA, 005930"
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
            
            industry = st.selectbox("🏭 산업 분야", options=industries)
            
            # Analysis period
            period = st.selectbox(
                "📅 분석 기간",
                options=[1, 3, 6, 12, 24],
                index=3,
                format_func=lambda x: f"{x}개월"
            )
            
            st.markdown("---")
            
            # Action buttons
            analyze_button = st.button(
                "🔍 분석 시작", 
                type="primary", 
                use_container_width=True
            )
            
            if st.session_state.get('analysis_results'):
                clear_button = st.button(
                    "🗑️ 결과 지우기", 
                    use_container_width=True
                )
            else:
                clear_button = False
            
            # Advanced options
            with st.expander("⚙️ 고급 설정"):
                include_recommendations = st.checkbox("추천 종목 포함", value=True)
                show_detailed_analysis = st.checkbox("상세 분석 표시", value=True)
                export_results = st.checkbox("결과 내보내기", value=False)
        
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
        """Render main content when no analysis is running."""
        # Welcome section
        st.markdown("""
        <div class="welcome-section">
            <h2 class="welcome-title">분석할 준비가 완료되었습니다</h2>
            <p class="welcome-subtitle">왼쪽 사이드바에 종목 코드를 입력하고 분석을 시작하세요</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3 class="feature-title">🤖 AI 전문가</h3>
                <p class="feature-description">6명의 전문 AI 에이전트가 다각도로 투자를 분석합니다</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3 class="feature-title">🌐 글로벌 시장</h3>
                <p class="feature-description">미국과 한국 주식 시장을 모두 지원합니다</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3 class="feature-title">📊 종합 분석</h3>
                <p class="feature-description">기술적·기본적 분석과 리스크 평가를 한번에</p>
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
        """Display analysis results with clean design."""
        
        # Ticker display
        company_name = analysis_data.get('stock_info', {}).get('longName', '')
        if not company_name:
            company_name = analysis_data.get('stock_info', {}).get('회사명', '')
        self.theme.create_ticker_display(ticker, company_name)
        
        # Main layout - better proportions
        col1, col2 = st.columns([3, 2], gap="large")
        
        with col1:
            # Investment decision
            self._render_investment_decision(final_decision)
            
            # Agent analyses
            self._render_agent_analyses(agent_results)
        
        with col2:
            # Stock information
            self._render_stock_info(analysis_data.get('stock_info', {}))
            
            # Key metrics
            self._render_key_metrics(analysis_data)
        
        # Price chart (full width)
        if not price_history.empty:
            self._render_price_chart(price_history, ticker)
    
    def _render_investment_decision(self, decision: str):
        """Render investment decision card."""
        # Extract decision type
        decision_type = "HOLD"
        status_class = "hold"
        
        if "매수" in decision or "BUY" in decision.upper():
            decision_type = "매수"
            status_class = "buy"
        elif "매도" in decision or "SELL" in decision.upper():
            decision_type = "매도"
            status_class = "sell"
        elif "보유" in decision or "HOLD" in decision.upper():
            decision_type = "보유"
            status_class = "hold"
        
        st.markdown(f"""
        <div class="clean-card">
            <div class="card-header">
                <h3 class="card-title">💡 투자 추천</h3>
                <span class="status-badge {status_class}">{decision_type}</span>
            </div>
            <div class="card-content">{decision}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_agent_analyses(self, agent_results: Dict[str, str]):
        """Render agent analyses in tabs."""
        if not agent_results:
            return
        
        st.markdown("### 🧠 전문가 분석")
        
        # Agent name mapping
        agent_names = {
            "기업분석가": "📈 기업분석가",
            "산업전문가": "🏭 산업전문가",
            "거시경제전문가": "🌍 거시경제전문가",
            "기술분석가": "📊 기술분석가",
            "리스크관리자": "⚠️ 리스크관리자",
            "중재자": "⚖️ 종합판단"
        }
        
        # Create tabs
        if len(agent_results) > 1:
            tab_names = [agent_names.get(agent, agent) for agent in agent_results.keys()]
            tabs = st.tabs(tab_names)
            
            for i, (agent, analysis) in enumerate(agent_results.items()):
                with tabs[i]:
                    st.markdown(f"""
                    <div style="padding: 1rem 0; font-size: 14px; line-height: 1.8; color: #4A5568;">
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Single analysis
            for agent, analysis in agent_results.items():
                agent_name = agent_names.get(agent, agent)
                st.markdown(f"""
                <div class="clean-card">
                    <div class="card-header">
                        <h3 class="card-title">{agent_name}</h3>
                    </div>
                    <div class="card-content">{analysis}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_stock_info(self, stock_info: Dict[str, Any]):
        """Render stock information table."""
        if not stock_info:
            return
        
        # Extract key data points with Korean labels
        data_points = {}
        
        # Price data
        if 'currentPrice' in stock_info:
            data_points['현재가'] = f"${stock_info['currentPrice']:.2f}"
        elif '현재가' in stock_info and stock_info['현재가'] != "정보 없음":
            try:
                price = float(stock_info['현재가'])
                data_points['현재가'] = f"${price:.2f}"
            except:
                data_points['현재가'] = str(stock_info['현재가'])
        
        # Valuation metrics
        if 'forwardPE' in stock_info and stock_info['forwardPE']:
            data_points['PER'] = f"{stock_info['forwardPE']:.1f}"
        elif 'PER' in stock_info and stock_info['PER'] != "정보 없음":
            data_points['PER'] = str(stock_info['PER'])
        
        if 'priceToBook' in stock_info and stock_info['priceToBook']:
            data_points['PBR'] = f"{stock_info['priceToBook']:.1f}"
        elif 'PBR' in stock_info and stock_info['PBR'] != "정보 없음":
            data_points['PBR'] = str(stock_info['PBR'])
        
        # Profitability
        if 'returnOnEquity' in stock_info and stock_info['returnOnEquity']:
            data_points['ROE'] = f"{stock_info['returnOnEquity']:.1%}"
        elif 'ROE' in stock_info and stock_info['ROE'] != "정보 없음":
            data_points['ROE'] = str(stock_info['ROE'])
        
        # Market cap
        if 'marketCap' in stock_info and stock_info['marketCap']:
            market_cap = stock_info['marketCap']
            if isinstance(market_cap, (int, float)):
                if market_cap > 1e12:
                    data_points['시가총액'] = f"${market_cap/1e12:.1f}T"
                elif market_cap > 1e9:
                    data_points['시가총액'] = f"${market_cap/1e9:.1f}B"
                else:
                    data_points['시가총액'] = f"${market_cap/1e6:.1f}M"
        elif '시가총액' in stock_info and stock_info['시가총액'] != "정보 없음":
            data_points['시가총액'] = str(stock_info['시가총액'])
        
        # 52-week range
        if '52주 최고가' in stock_info and stock_info['52주 최고가'] != "정보 없음":
            try:
                high = float(stock_info['52주 최고가'])
                data_points['52주 최고'] = f"${high:.2f}"
            except:
                data_points['52주 최고'] = str(stock_info['52주 최고가'])
        
        if '52주 최저가' in stock_info and stock_info['52주 최저가'] != "정보 없음":
            try:
                low = float(stock_info['52주 최저가'])
                data_points['52주 최저'] = f"${low:.2f}"
            except:
                data_points['52주 최저'] = str(stock_info['52주 최저가'])
        
        if data_points:
            self.theme.create_data_table(data_points, "📋 종목 정보")
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]):
        """Render key analysis metrics."""
        technical = analysis_data.get('technical_analysis', {})
        fundamental = analysis_data.get('fundamental_analysis', {})
        
        metrics = {}
        
        # Technical indicators
        if 'rsi' in technical and isinstance(technical['rsi'], (int, float)):
            metrics['RSI'] = f"{technical['rsi']:.1f}"
        
        if 'macd_signal' in technical and technical['macd_signal'] in ['BUY', 'SELL', 'HOLD']:
            signal_map = {'BUY': '매수', 'SELL': '매도', 'HOLD': '보유'}
            metrics['MACD 신호'] = signal_map.get(technical['macd_signal'], technical['macd_signal'])
        
        # Fundamental scores
        if 'overall_score' in fundamental and isinstance(fundamental['overall_score'], (int, float)):
            metrics['종합 점수'] = f"{fundamental['overall_score']:.1f}/10"
        
        if 'growth_score' in fundamental and isinstance(fundamental['growth_score'], (int, float)):
            metrics['성장성 점수'] = f"{fundamental['growth_score']:.1f}/10"
        
        if metrics:
            self.theme.create_data_table(metrics, "📊 주요 지표")
        else:
            # Show placeholder if no metrics available
            placeholder_metrics = {
                'RSI': '분석중...',
                'MACD 신호': '계산중...',
                '종합 점수': '평가중...'
            }
            self.theme.create_data_table(placeholder_metrics, "📊 주요 지표")
    
    def _render_price_chart(self, price_history: pd.DataFrame, ticker: str):
        """Render price chart."""
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">📈 주가 차트</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean line chart
        if 'Close' in price_history.columns:
            chart_data = price_history[['Close']].copy()
            chart_data.columns = [ticker]
            
            st.line_chart(
                chart_data,
                height=400,
                use_container_width=True
            )
        else:
            st.info("📊 차트 데이터를 불러오는 중입니다...")
    
    def display_error(self, error_message: str):
        """Display error message."""
        self.theme.create_alert(error_message, "error")
    
    def display_warning(self, warning_message: str):
        """Display warning message."""
        self.theme.create_alert(warning_message, "warning")
    
    def display_success(self, success_message: str):
        """Display success message."""
        self.theme.create_alert(success_message, "success")