"""
Modern Clean UI

Clean, professional UI using Streamlit native components.
Minimal custom CSS for better compatibility.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime


class ModernCleanUI:
    """Modern clean UI using Streamlit native components."""
    
    def __init__(self):
        self.colors = {
            'green': '#10B981',
            'red': '#EF4444',
            'amber': '#F59E0B',
            'blue': '#3B82F6',
            'gray': '#6B7280'
        }
    
    def setup_page(self):
        """Setup page with minimal custom styling."""
        st.markdown("""
        <style>
        /* Dark theme override */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            background-color: #1F2937;
            border: 1px solid #374151;
        }
        
        .stButton > button:hover {
            background-color: #374151;
            border: 1px solid #4B5563;
        }
        
        /* Metric styling */
        [data-testid="metric-container"] {
            background-color: #1F2937;
            border: 1px solid #374151;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, company_name: str, price: float, change: float, change_pct: float):
        """Render header using native Streamlit components."""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"# {ticker}")
            st.markdown(f"##### {company_name}")
        
        with col2:
            st.metric(
                label="현재가",
                value=f"${price:,.2f}",
                delta=f"{change:+.2f} ({change_pct:+.2f}%)"
            )
        
        with col3:
            st.metric(
                label="거래 상태",
                value="정규장" if 9 <= datetime.now().hour < 16 else "장마감"
            )
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """Render market indices using Streamlit columns."""
        st.markdown("### 📊 시장 지표")
        
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                
                # Special handling for VIX
                if name == "VIX":
                    fear_level = data.get('fear_level', '')
                    if current < 20:
                        st.success(f"**{name}**\n\n{current:.2f}\n\n{fear_level}")
                    elif current < 30:
                        st.warning(f"**{name}**\n\n{current:.2f}\n\n{fear_level}")
                    else:
                        st.error(f"**{name}**\n\n{current:.2f}\n\n{fear_level}")
                else:
                    st.metric(
                        label=name,
                        value=f"{current:,.2f}",
                        delta=f"{change:+.2f}%"
                    )
    
    def render_key_metrics(self, metrics: Dict[str, Any]):
        """Render key metrics in a clean grid."""
        st.markdown("### 📈 주요 지표")
        
        # Create 4 columns
        col1, col2, col3, col4 = st.columns(4)
        
        # First row
        with col1:
            st.metric("시가총액", self._format_market_cap(metrics.get('marketCap', 0)))
        with col2:
            st.metric("PER", f"{metrics.get('PER', 'N/A')}")
        with col3:
            st.metric("PBR", f"{metrics.get('PBR', 'N/A')}")
        with col4:
            st.metric("배당수익률", f"{metrics.get('dividendYield', 'N/A')}%")
        
        # Second row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("52주 최고", f"${metrics.get('52주최고', 0):,.2f}")
        with col2:
            st.metric("52주 최저", f"${metrics.get('52주최저', 0):,.2f}")
        with col3:
            st.metric("베타", f"{metrics.get('beta', 'N/A')}")
        with col4:
            st.metric("거래량", self._format_volume(metrics.get('volume', 0)))
    
    def render_price_chart(self, df: pd.DataFrame, ticker: str):
        """Render price chart using Plotly."""
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
            increasing_line_color=self.colors['green'],
            decreasing_line_color=self.colors['red']
        ))
        
        # Volume
        colors = ['red' if row['Open'] > row['Close'] else 'green' for _, row in df.iterrows()]
        
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
            title=f"{ticker} Price History",
            yaxis_title="Price ($)",
            yaxis2=dict(
                title="Volume",
                overlaying='y',
                side='right'
            ),
            template="plotly_dark",
            height=500,
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analysis_results(self, agent_results: Dict[str, str]):
        """Render AI analysis results."""
        st.markdown("### 🤖 AI 분석 결과")
        
        tabs = st.tabs(list(agent_results.keys()))
        
        for idx, (agent_name, result) in enumerate(agent_results.items()):
            with tabs[idx]:
                st.markdown(result)
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render sidebar with inputs."""
        with st.sidebar:
            st.markdown("## 🎯 AI 투자 분석")
            st.markdown("---")
            
            # Market selection
            market = st.radio(
                "시장 선택",
                options=["미국", "한국"],
                horizontal=True
            )
            
            # Ticker input
            ticker = st.text_input(
                "종목 코드",
                placeholder="AAPL, 005930...",
                help="미국: AAPL, MSFT / 한국: 005930, 035420"
            ).upper().strip()
            
            # Industry
            industries = ["Technology", "Healthcare", "Finance", "Consumer", "Energy", "Industrial"] if market == "미국" else ["전자/IT", "제약/바이오", "금융", "소비재", "에너지/화학", "산업재"]
            
            industry = st.selectbox(
                "산업 분류",
                options=industries
            )
            
            # Period
            period = st.select_slider(
                "분석 기간",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}개월"
            )
            
            st.markdown("---")
            
            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                analyze = st.button("🔍 분석 시작", type="primary")
            with col2:
                clear = st.button("🗑️ 초기화")
            
            # Advanced options
            with st.expander("⚙️ 고급 설정"):
                include_recs = st.checkbox("연관 종목 추천", value=True)
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
        """Render welcome screen."""
        st.markdown("""
        # 🚀 AI 투자 분석 시스템
        
        ### 인공지능 기반 주식 분석 플랫폼
        
        왼쪽 사이드바에서 분석하고자 하는 종목을 선택해주세요.
        
        ---
        
        #### 📋 사용 방법
        
        1. **시장 선택**: 미국 또는 한국 시장 선택
        2. **종목 입력**: 분석할 종목 코드 입력
        3. **기간 설정**: 분석 기간 선택
        4. **분석 시작**: 버튼을 눌러 AI 분석 시작
        
        ---
        
        #### 🎯 주요 기능
        
        - ✅ **실시간 시장 데이터**
        - ✅ **AI 기반 종합 분석**
        - ✅ **기술적/기본적 분석**
        - ✅ **투자 의견 제공**
        - ✅ **리스크 평가**
        
        """)
    
    def _format_market_cap(self, value: float) -> str:
        """Format market cap."""
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
        if value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:,.0f}"