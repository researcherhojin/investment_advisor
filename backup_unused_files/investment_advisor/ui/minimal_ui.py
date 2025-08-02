"""
Minimal Modern UI

Clean, minimalist design with perfect spacing and typography.
Inspired by modern fintech apps like Robinhood, Cash App.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime


class MinimalUI:
    """Minimal modern UI with clean design."""
    
    def __init__(self):
        # Color palette - minimal and clean
        self.colors = {
            'background': '#FFFFFF',
            'surface': '#FAFAFA',
            'text': '#000000',
            'text_secondary': '#666666',
            'text_muted': '#999999',
            'border': '#E0E0E0',
            'success': '#00C853',
            'danger': '#FF1744',
            'warning': '#FFB300',
            'primary': '#000000',
            'accent': '#4285F4'
        }
    
    def setup_page(self):
        """Setup minimal page styling."""
        # Custom CSS for minimal design
        st.markdown("""
        <style>
        /* Import clean font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Remove default Streamlit styling */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container */
        .main > div {
            padding: 2rem 3rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #FAFAFA;
            border-right: 1px solid #E0E0E0;
            width: 280px !important;
        }
        
        section[data-testid="stSidebar"] > div {
            padding: 2rem 1.5rem;
        }
        
        /* Headers */
        h1 {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #000000 !important;
            margin: 0 0 0.5rem 0 !important;
            letter-spacing: -0.02em !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #000000 !important;
            margin: 2rem 0 1rem 0 !important;
            letter-spacing: -0.01em !important;
        }
        
        h3 {
            font-size: 1.125rem !important;
            font-weight: 600 !important;
            color: #000000 !important;
            margin: 1.5rem 0 0.75rem 0 !important;
        }
        
        /* Metrics container */
        [data-testid="metric-container"] {
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: none;
            transition: all 0.2s ease;
        }
        
        [data-testid="metric-container"]:hover {
            border-color: #000000;
        }
        
        /* Metric labels and values */
        [data-testid="metric-container"] label {
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: #666666 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        [data-testid="metric-container"] > div > div {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #000000 !important;
            margin-top: 0.25rem;
        }
        
        /* Delta values */
        [data-testid="metric-container"] [data-testid="stMetricDelta"] {
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            margin-top: 0.25rem;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #000000;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            font-size: 0.875rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background-color: #333333;
            transform: translateY(-1px);
        }
        
        /* Primary button */
        .stButton > button[kind="primary"] {
            background-color: #000000;
        }
        
        /* Secondary button */
        .stButton > button[kind="secondary"] {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #E0E0E0;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #FAFAFA;
            border-color: #000000;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.875rem;
            background-color: #FFFFFF;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #000000;
            box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
        }
        
        /* Select boxes */
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        
        /* Radio buttons */
        .stRadio > div {
            gap: 1rem;
        }
        
        .stRadio > div > label {
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }
        
        .stRadio > div > label:hover {
            border-color: #000000;
        }
        
        .stRadio > div > label[data-selected="true"] {
            background-color: #000000;
            color: #FFFFFF;
            border-color: #000000;
        }
        
        /* Tabs */
        .stTabs {
            border: none;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent;
            border-bottom: 1px solid #E0E0E0;
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border: none;
            color: #999999;
            font-weight: 500;
            padding: 0.75rem 0;
            font-size: 0.875rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        
        .stTabs [aria-selected="true"] {
            color: #000000;
            border-bottom: 2px solid #000000;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-weight: 500;
        }
        
        /* Success/Error/Warning boxes */
        .stAlert {
            border-radius: 8px;
            border: none;
            padding: 1rem;
        }
        
        /* Horizontal line */
        hr {
            border: none;
            border-top: 1px solid #E0E0E0;
            margin: 2rem 0;
        }
        
        /* Custom spacing utilities */
        .mt-1 { margin-top: 0.5rem !important; }
        .mt-2 { margin-top: 1rem !important; }
        .mt-3 { margin-top: 1.5rem !important; }
        .mt-4 { margin-top: 2rem !important; }
        .mb-1 { margin-bottom: 0.5rem !important; }
        .mb-2 { margin-bottom: 1rem !important; }
        .mb-3 { margin-bottom: 1.5rem !important; }
        .mb-4 { margin-bottom: 2rem !important; }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, company_name: str, price: float, change: float, change_pct: float):
        """Render minimal header."""
        # Main header row
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"# {ticker}")
            st.markdown(f"<p style='color: #666666; margin: 0;'>{company_name}</p>", unsafe_allow_html=True)
        
        with col2:
            st.metric(
                label="현재가",
                value=f"${price:,.2f}",
                delta=f"{change:+.2f} ({change_pct:+.2f}%)"
            )
        
        with col3:
            now = datetime.now()
            market_open = 9 <= now.hour < 16
            st.metric(
                label="거래 상태",
                value="정규장" if market_open else "장마감",
                delta=None
            )
        
        # Add clean separator
        st.markdown("<hr style='margin: 2rem 0 1.5rem 0;'>", unsafe_allow_html=True)
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """Render market indices in minimal style."""
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                
                # Special styling for VIX
                if name == "VIX":
                    fear_level = data.get('fear_level', '')
                    vix_status = "🟢" if current < 20 else "🟡" if current < 30 else "🔴"
                    
                    st.metric(
                        label=f"{name} {vix_status}",
                        value=f"{current:.2f}",
                        delta=f"{change:+.2f}%",
                        help=fear_level
                    )
                else:
                    st.metric(
                        label=name,
                        value=f"{current:,.2f}",
                        delta=f"{change:+.2f}%"
                    )
    
    def render_key_metrics(self, metrics: Dict[str, Any]):
        """Render key metrics in minimal grid."""
        st.markdown("## 주요 지표")
        
        # Create 4 columns for clean layout
        col1, col2, col3, col4 = st.columns(4)
        
        # Row 1
        with col1:
            value = metrics.get('marketCap', 0)
            st.metric("시가총액", self._format_market_cap(value))
        
        with col2:
            per = metrics.get('PER')
            st.metric("PER", f"{per:.2f}" if per and per != 'N/A' else "—")
        
        with col3:
            pbr = metrics.get('PBR')
            st.metric("PBR", f"{pbr:.2f}" if pbr and pbr != 'N/A' else "—")
        
        with col4:
            div_yield = metrics.get('dividendYield')
            st.metric("배당수익률", f"{div_yield:.2f}%" if div_yield else "—")
        
        # Add spacing
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # Row 2
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_52 = metrics.get('52주최고', 0)
            st.metric("52주 최고", f"${high_52:,.2f}" if high_52 else "—")
        
        with col2:
            low_52 = metrics.get('52주최저', 0)
            st.metric("52주 최저", f"${low_52:,.2f}" if low_52 else "—")
        
        with col3:
            beta = metrics.get('beta')
            st.metric("베타", f"{beta:.2f}" if beta else "—")
        
        with col4:
            volume = metrics.get('volume', 0)
            st.metric("거래량", self._format_volume(volume))
    
    def render_price_chart(self, df: pd.DataFrame, ticker: str):
        """Render minimal price chart."""
        st.markdown("## 가격 차트")
        
        # Create minimalist chart
        fig = go.Figure()
        
        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color='#00C853',
            decreasing_line_color='#FF1744',
            increasing_fillcolor='#00C853',
            decreasing_fillcolor='#FF1744'
        ))
        
        # Update layout for minimal look
        fig.update_layout(
            yaxis_title="가격 ($)",
            template="plotly_white",
            height=500,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                rangeslider=dict(visible=False),
                gridcolor='#F0F0F0',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                gridcolor='#F0F0F0',
                showgrid=True,
                zeroline=False,
                side='right'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter", size=12),
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analysis_results(self, agent_results: Dict[str, str]):
        """Render AI analysis results in minimal style."""
        st.markdown("## AI 분석 결과")
        
        # Use clean tabs
        agent_names = list(agent_results.keys())
        tabs = st.tabs(agent_names)
        
        for tab, (agent_name, result) in zip(tabs, agent_results.items()):
            with tab:
                # Clean content display
                st.markdown(f"""
                <div style='
                    background-color: #FAFAFA;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-top: 1rem;
                    line-height: 1.6;
                '>
                    {result}
                </div>
                """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render minimal sidebar."""
        with st.sidebar:
            # Clean logo
            st.markdown("""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h2 style='margin: 0; font-size: 1.5rem;'>📈 AI 주식분석</h2>
                <p style='margin: 0; color: #666666; font-size: 0.875rem;'>인공지능 투자분석</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Market selection with custom styling
            st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("**시장 선택**")
            market = st.radio(
                "Market",
                options=["US", "KR"],
                format_func=lambda x: "🇺🇸 미국" if x == "US" else "🇰🇷 한국",
                horizontal=True,
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Ticker input
            st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("**종목 코드**")
            ticker = st.text_input(
                "Symbol",
                placeholder="AAPL",
                label_visibility="collapsed",
                help="예시: AAPL, MSFT, GOOGL"
            ).upper().strip()
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Industry selection
            st.markdown("<div style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("**산업 분류**")
            industries = ["기술", "의료", "금융", "소비재", "에너지"] if market == "US" else ["전자/IT", "바이오", "금융", "소비재", "에너지"]
            industry = st.selectbox(
                "Industry",
                options=industries,
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Period selection
            st.markdown("<div style='margin-bottom: 2rem;'>", unsafe_allow_html=True)
            st.markdown("**분석 기간**")
            period = st.select_slider(
                "Period",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}개월",
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action buttons
            analyze = st.button("분석 시작", type="primary", use_container_width=True)
            clear = st.button("초기화", type="secondary", use_container_width=True)
            
            # Advanced options
            with st.expander("고급 설정"):
                include_recs = st.checkbox("추천 종목 포함", value=True)
                use_cache = st.checkbox("캐시 사용", value=True)
            
            return {
                'ticker': ticker,
                'market': market + "장",
                'industry': industry,
                'period': period,
                'actions': {
                    'analyze': analyze,
                    'clear': clear
                },
                'advanced': {
                    'include_recommendations': include_recs,
                    'use_cache': use_cache
                }
            }
    
    def render_welcome(self):
        """Render minimal welcome screen."""
        # Center content
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 4rem 0;'>
                <h1 style='font-size: 3rem; margin-bottom: 1rem;'>
                    AI 주식 분석
                </h1>
                <p style='font-size: 1.25rem; color: #666666; margin-bottom: 3rem;'>
                    인공지능 기반 전문 주식 분석 플랫폼
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Feature cards
            features = [
                ("실시간 데이터", "실시간 시장 가격과 지표"),
                ("AI 분석", "6개 전문 AI 에이전트"),
                ("스마트 인사이트", "데이터 기반 투자 추천")
            ]
            
            for title, desc in features:
                st.markdown(f"""
                <div style='
                    background-color: #FAFAFA;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                    text-align: center;
                '>
                    <h3 style='margin: 0 0 0.5rem 0;'>{title}</h3>
                    <p style='margin: 0; color: #666666;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Instructions
            st.markdown("""
            <div style='
                margin-top: 3rem;
                padding: 1.5rem;
                background-color: #F5F5F5;
                border-radius: 12px;
                text-align: center;
            '>
                <p style='margin: 0; color: #666666;'>
                    시장을 선택하고 종목 코드를 입력하여 분석을 시작하세요
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_decision(self, decision: str):
        """Render investment decision in minimal style."""
        # Determine decision type
        if "매수" in decision or "BUY" in decision:
            bg_color = "#E8F5E9"
            text_color = "#00C853"
            icon = "📈"
        elif "매도" in decision or "SELL" in decision:
            bg_color = "#FFEBEE"
            text_color = "#FF1744"
            icon = "📉"
        else:
            bg_color = "#FFF8E1"
            text_color = "#FFB300"
            icon = "⚖️"
        
        st.markdown(f"""
        <div style='
            background-color: {bg_color};
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin: 2rem 0;
        '>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>{icon}</div>
            <h2 style='color: {text_color}; margin: 0; font-size: 2rem;'>
                {decision}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    def _format_market_cap(self, value: float) -> str:
        """Format market cap."""
        if not value or value == 0:
            return "—"
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        elif value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.0f}"
    
    def _format_volume(self, value: float) -> str:
        """Format volume."""
        if not value or value == 0:
            return "—"
        if value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:,.0f}"