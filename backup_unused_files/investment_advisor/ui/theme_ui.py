"""
Theme-based UI with Dark/Light Mode Toggle

Clean, professional UI with theme switching capability.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime


class ThemeUI:
    """Theme-based UI with dark/light mode support."""
    
    def __init__(self):
        # Initialize theme state
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        
        self.themes = {
            'light': {
                'bg_primary': '#FFFFFF',
                'bg_secondary': '#F8F9FA',
                'bg_card': '#FFFFFF',
                'text_primary': '#212529',
                'text_secondary': '#6C757D',
                'text_muted': '#ADB5BD',
                'border': '#DEE2E6',
                'shadow': '0 0.125rem 0.25rem rgba(0,0,0,0.075)',
                'green': '#198754',
                'red': '#DC3545',
                'blue': '#0D6EFD',
                'amber': '#FFC107',
                'plotly_template': 'plotly_white'
            },
            'dark': {
                'bg_primary': '#0E1117',
                'bg_secondary': '#1A1E29',
                'bg_card': '#262730',
                'text_primary': '#FFFFFF',
                'text_secondary': '#B1B6C1',
                'text_muted': '#6C757D',
                'border': '#393E4B',
                'shadow': '0 0.125rem 0.25rem rgba(0,0,0,0.5)',
                'green': '#00D26A',
                'red': '#F85149',
                'blue': '#58A6FF',
                'amber': '#FFA500',
                'plotly_template': 'plotly_dark'
            }
        }
    
    def get_theme(self):
        """Get current theme colors."""
        return self.themes[st.session_state.theme]
    
    def apply_theme(self):
        """Apply theme styling to the app."""
        theme = self.get_theme()
        
        st.markdown(f"""
        <style>
        /* Main app background */
        .stApp {{
            background-color: {theme['bg_primary']};
            color: {theme['text_primary']};
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {theme['bg_secondary']};
        }}
        
        /* Cards and containers */
        .element-container {{
            background-color: {theme['bg_card']};
            border-radius: 0.5rem;
        }}
        
        /* Metrics */
        [data-testid="metric-container"] {{
            background-color: {theme['bg_card']};
            border: 1px solid {theme['border']};
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: {theme['shadow']};
        }}
        
        /* Text colors */
        .stMarkdown, .stText {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {theme['bg_card']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
        }}
        
        .stButton > button:hover {{
            background-color: {theme['bg_secondary']};
            border-color: {theme['text_secondary']};
        }}
        
        /* Input fields */
        .stTextInput > div > div > input {{
            background-color: {theme['bg_card']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
        }}
        
        /* Select boxes */
        .stSelectbox > div > div > div {{
            background-color: {theme['bg_card']};
            color: {theme['text_primary']};
        }}
        
        /* Radio buttons */
        .stRadio > div {{
            background-color: transparent;
        }}
        
        .stRadio label {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {theme['bg_secondary']};
            border-radius: 0.5rem 0.5rem 0 0;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: {theme['text_secondary']};
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: {theme['text_primary']};
            background-color: {theme['bg_card']};
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Custom card style */
        .custom-card {{
            background-color: {theme['bg_card']};
            border: 1px solid {theme['border']};
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: {theme['shadow']};
        }}
        
        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 999;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def render_theme_toggle(self):
        """Render theme toggle button."""
        col1, col2, col3 = st.columns([8, 1, 1])
        with col3:
            if st.button("🌓", help="테마 전환"):
                st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
                st.rerun()
    
    def render_header(self, ticker: str, company_name: str, price: float, change: float, change_pct: float):
        """Render header with theme support."""
        theme = self.get_theme()
        
        # Theme toggle in header
        self.render_theme_toggle()
        
        # Company info
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.markdown(f"# {ticker}")
            st.markdown(f"##### {company_name}")
        
        with col2:
            color = theme['green'] if change >= 0 else theme['red']
            delta_str = f"{change:+.2f} ({change_pct:+.2f}%)"
            st.metric(
                label="현재가",
                value=f"${price:,.2f}",
                delta=delta_str
            )
        
        with col3:
            market_status = "정규장" if 9 <= datetime.now().hour < 16 else "장마감"
            st.metric(
                label="거래 상태",
                value=market_status,
                delta=None
            )
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """Render market indices with theme support."""
        theme = self.get_theme()
        
        st.markdown("### 📊 시장 지표")
        
        # Create card container
        st.markdown(f"""
        <div class="custom-card" style="background-color: {theme['bg_card']};">
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                
                if name == "VIX":
                    # VIX special handling
                    fear_level = data.get('fear_level', '')
                    if current < 20:
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                background-color: {theme['green']};
                                color: white;
                                padding: 1rem;
                                border-radius: 0.5rem;
                                text-align: center;
                            ">
                                <div style="font-weight: 600;">{name}</div>
                                <div style="font-size: 1.5rem; font-weight: 700;">{current:.2f}</div>
                                <div style="font-size: 0.875rem;">{fear_level}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    elif current < 30:
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                background-color: {theme['amber']};
                                color: {theme['text_primary']};
                                padding: 1rem;
                                border-radius: 0.5rem;
                                text-align: center;
                            ">
                                <div style="font-weight: 600;">{name}</div>
                                <div style="font-size: 1.5rem; font-weight: 700;">{current:.2f}</div>
                                <div style="font-size: 0.875rem;">{fear_level}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                background-color: {theme['red']};
                                color: white;
                                padding: 1rem;
                                border-radius: 0.5rem;
                                text-align: center;
                            ">
                                <div style="font-weight: 600;">{name}</div>
                                <div style="font-size: 1.5rem; font-weight: 700;">{current:.2f}</div>
                                <div style="font-size: 0.875rem;">{fear_level}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    # Regular indices
                    st.metric(
                        label=name,
                        value=f"{current:,.2f}",
                        delta=f"{change:+.2f}%"
                    )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_key_metrics(self, metrics: Dict[str, Any]):
        """Render key metrics with theme support."""
        st.markdown("### 📈 주요 지표")
        
        with st.container():
            # First row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("시가총액", self._format_market_cap(metrics.get('marketCap', 0)))
            with col2:
                per = metrics.get('PER')
                st.metric("PER", f"{per:.2f}" if per and per != 'N/A' else "N/A")
            with col3:
                pbr = metrics.get('PBR')
                st.metric("PBR", f"{pbr:.2f}" if pbr and pbr != 'N/A' else "N/A")
            with col4:
                div_yield = metrics.get('dividendYield')
                st.metric("배당수익률", f"{div_yield:.2f}%" if div_yield else "N/A")
            
            # Second row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                high_52 = metrics.get('52주최고', 0)
                st.metric("52주 최고", f"${high_52:,.2f}" if high_52 else "N/A")
            with col2:
                low_52 = metrics.get('52주최저', 0)
                st.metric("52주 최저", f"${low_52:,.2f}" if low_52 else "N/A")
            with col3:
                beta = metrics.get('beta')
                st.metric("베타", f"{beta:.2f}" if beta else "N/A")
            with col4:
                st.metric("거래량", self._format_volume(metrics.get('volume', 0)))
    
    def render_price_chart(self, df: pd.DataFrame, ticker: str):
        """Render price chart with theme support."""
        theme = self.get_theme()
        
        st.markdown("### 📉 가격 차트")
        
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color=theme['green'],
            decreasing_line_color=theme['red']
        ))
        
        # Volume bars
        colors = [theme['red'] if row['Open'] > row['Close'] else theme['green'] 
                 for _, row in df.iterrows()]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            yaxis='y2',
            opacity=0.3
        ))
        
        # Layout
        fig.update_layout(
            title=f"{ticker} 가격 추이",
            yaxis_title="가격 ($)",
            yaxis2=dict(
                title="거래량",
                overlaying='y',
                side='right'
            ),
            template=theme['plotly_template'],
            height=500,
            showlegend=False,
            hovermode='x unified',
            paper_bgcolor=theme['bg_card'],
            plot_bgcolor=theme['bg_card']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analysis_results(self, agent_results: Dict[str, str]):
        """Render AI analysis results with theme support."""
        theme = self.get_theme()
        
        st.markdown("### 🤖 AI 분석 결과")
        
        tabs = st.tabs(list(agent_results.keys()))
        
        for idx, (agent_name, result) in enumerate(agent_results.items()):
            with tabs[idx]:
                st.markdown(f"""
                <div class="custom-card">
                    {result}
                </div>
                """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render sidebar with theme support."""
        with st.sidebar:
            # Logo and title
            st.markdown("# 🎯 AI 투자 분석")
            st.markdown("##### Smart Stock AI")
            st.markdown("---")
            
            # Market selection
            market = st.radio(
                "📍 시장 선택",
                options=["미국", "한국"],
                horizontal=True
            )
            
            # Ticker input
            ticker = st.text_input(
                "🔤 종목 코드",
                placeholder="AAPL, 005930...",
                help="미국: AAPL, MSFT / 한국: 005930, 035420"
            ).upper().strip()
            
            # Industry
            st.markdown("🏭 **산업 분류**")
            industries = ["Technology", "Healthcare", "Finance", "Consumer", "Energy", "Industrial"] if market == "미국" else ["전자/IT", "제약/바이오", "금융", "소비재", "에너지/화학", "산업재"]
            industry = st.selectbox(
                "산업 선택",
                options=industries,
                label_visibility="collapsed"
            )
            
            # Period
            st.markdown("📅 **분석 기간**")
            period = st.select_slider(
                "기간 선택",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}개월",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                analyze = st.button("🔍 분석 시작", type="primary", use_container_width=True)
            with col2:
                clear = st.button("🗑️ 초기화", use_container_width=True)
            
            # Advanced options
            with st.expander("⚙️ 고급 설정"):
                include_recs = st.checkbox("연관 종목 추천", value=True)
                use_cache = st.checkbox("캐시 사용", value=True)
            
            # Theme info at bottom
            st.markdown("---")
            current_theme = "🌙 다크 모드" if st.session_state.theme == 'dark' else "☀️ 라이트 모드"
            st.markdown(f"<small>현재 테마: {current_theme}</small>", unsafe_allow_html=True)
            
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
        """Render welcome screen with theme support."""
        theme = self.get_theme()
        
        # Theme toggle at top
        self.render_theme_toggle()
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">
                🚀 AI 투자 분석 시스템
            </h1>
            <p style="font-size: 1.25rem; color: {theme['text_secondary']};">
                인공지능 기반 주식 분석 플랫폼
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Info cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <h3>📊 실시간 데이터</h3>
                <p style="color: {theme['text_secondary']};">
                    최신 시장 데이터와<br>실시간 가격 정보
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <h3>🤖 AI 분석</h3>
                <p style="color: {theme['text_secondary']};">
                    6개 전문 AI 에이전트의<br>종합적인 분석
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center;">
                <h3>💡 투자 인사이트</h3>
                <p style="color: {theme['text_secondary']};">
                    데이터 기반의<br>투자 의사결정 지원
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Instructions
        st.markdown(f"""
        <div class="custom-card" style="margin-top: 2rem;">
            <h3>📋 사용 방법</h3>
            <ol style="color: {theme['text_secondary']};">
                <li>왼쪽 사이드바에서 시장(미국/한국) 선택</li>
                <li>분석하고자 하는 종목 코드 입력</li>
                <li>산업 분류 및 분석 기간 설정</li>
                <li>[분석 시작] 버튼을 클릭하여 AI 분석 실행</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    def _format_market_cap(self, value: float) -> str:
        """Format market cap."""
        if not value or value == 0:
            return "N/A"
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
            return "N/A"
        if value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:,.0f}"