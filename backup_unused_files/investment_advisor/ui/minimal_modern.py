"""
Minimal Modern UI Layout

Clean, professional design inspired by modern financial platforms.
Focus on readability and data clarity.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime

class MinimalModernLayout:
    """Minimal modern layout manager."""
    
    def __init__(self):
        self.colors = {
            'primary': '#000000',
            'secondary': '#6B7280',
            'background': '#FFFFFF',
            'surface': '#F9FAFB',
            'border': '#E5E7EB',
            'success': '#10B981',
            'danger': '#EF4444',
            'warning': '#F59E0B',
            'accent': '#3B82F6'
        }
    
    def apply_minimal_theme(self):
        """Apply minimal modern theme."""
        st.markdown("""
        <style>
        /* Import clean fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Remove Streamlit branding */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Main container */
        .main .block-container {
            padding: 2rem 1rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 600;
            color: #000000;
            margin-bottom: 1rem;
        }
        
        h1 { font-size: 2rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.25rem; }
        
        /* Remove default Streamlit styling */
        .stButton > button {
            background: #000000;
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-weight: 500;
            border-radius: 6px;
            transition: opacity 0.2s;
        }
        
        .stButton > button:hover {
            opacity: 0.8;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 0.75rem;
            font-size: 1rem;
        }
        
        /* Cards */
        .metric-card {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* Price display */
        .price-display {
            font-size: 2.5rem;
            font-weight: 700;
            color: #000000;
            margin: 0;
            line-height: 1.2;
        }
        
        .price-change {
            font-size: 1.25rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        
        .price-up { color: #10B981; }
        .price-down { color: #EF4444; }
        
        /* Data grid */
        .data-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #F3F4F6;
        }
        
        .data-label {
            color: #6B7280;
            font-size: 0.875rem;
        }
        
        .data-value {
            color: #000000;
            font-weight: 500;
        }
        
        /* Market indices */
        .index-card {
            background: #F9FAFB;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            transition: background 0.2s;
        }
        
        .index-card:hover {
            background: #F3F4F6;
        }
        
        .index-name {
            font-size: 0.875rem;
            color: #6B7280;
            margin-bottom: 0.5rem;
        }
        
        .index-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: #000000;
        }
        
        .index-change {
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        
        /* VIX special styling */
        .vix-card {
            background: #000000;
            color: white;
        }
        
        .vix-card .index-name,
        .vix-card .index-value {
            color: white;
        }
        
        /* Remove shadows and gradients */
        .element-container {
            box-shadow: none !important;
        }
        
        /* Clean sidebar */
        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E5E7EB;
        }
        
        section[data-testid="stSidebar"] > div {
            padding-top: 2rem;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 1px solid #E5E7EB;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            background: transparent;
            border: none;
            color: #6B7280;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            color: #000000;
            border-bottom: 2px solid #000000;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, company_name: str, current_price: float, price_change: float):
        """Render minimal header."""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="margin-bottom: 2rem;">
                <h1 style="margin: 0; font-size: 1.5rem; font-weight: 600;">{ticker}</h1>
                <p style="color: #6B7280; margin: 0.25rem 0;">{company_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
            change_class = "price-up" if price_change >= 0 else "price-down"
            change_symbol = "+" if price_change >= 0 else ""
            
            st.markdown(f"""
            <div>
                <p class="price-display">${current_price:,.2f}</p>
                <p class="price-change {change_class}">{change_symbol}{price_change:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """Render market indices in minimal style."""
        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">시장 지표</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for indices
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                change_color = "#10B981" if change >= 0 else "#EF4444"
                change_symbol = "+" if change >= 0 else ""
                
                # Special styling for VIX
                if name == "VIX":
                    if current < 20:
                        bg_color = "#10B981"  # Green for low volatility
                        text_color = "#FFFFFF"
                    elif current < 30:
                        bg_color = "#F59E0B"  # Amber for moderate
                        text_color = "#FFFFFF"
                    else:
                        bg_color = "#EF4444"  # Red for high volatility
                        text_color = "#FFFFFF"
                    fear_level = data.get('fear_level', '')
                else:
                    bg_color = "#F9FAFB"
                    text_color = "#000000"
                    fear_level = ""
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border-radius: 8px;
                    padding: 1rem;
                    text-align: center;
                    height: 100%;
                    transition: all 0.2s;
                ">
                    <div style="
                        font-size: 0.875rem;
                        color: {'#9CA3AF' if bg_color == '#F9FAFB' else '#FFFFFF'};
                        margin-bottom: 0.5rem;
                        font-weight: 500;
                    ">{name}</div>
                    <div style="
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: {text_color};
                        margin-bottom: 0.25rem;
                    ">{current:,.2f}</div>
                    <div style="
                        font-size: 0.875rem;
                        color: {change_color};
                        font-weight: 500;
                    ">{change_symbol}{change:.2f}%</div>
                    {f'<div style="font-size: 0.75rem; margin-top: 0.5rem; color: {text_color};">{fear_level}</div>' if fear_level else ''}
                </div>
                """, unsafe_allow_html=True)
    
    def render_key_metrics(self, metrics: Dict[str, Any]):
        """Render key metrics in clean grid."""
        st.markdown("<h3>주요 지표</h3>", unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        # Define metric groups
        metric_groups = [
            ('시가총액', self._format_market_cap(metrics.get('marketCap', 0))),
            ('PER', self._format_number(metrics.get('PER'))),
            ('PBR', self._format_number(metrics.get('PBR'))),
            ('배당수익률', self._format_percent(metrics.get('dividendYield'))),
            ('52주 최고', f"${metrics.get('52주최고', 0):,.2f}"),
            ('52주 최저', f"${metrics.get('52주최저', 0):,.2f}"),
            ('베타', self._format_number(metrics.get('beta'))),
            ('거래량', self._format_volume(metrics.get('volume', 0)))
        ]
        
        for label, value in metric_groups:
            st.markdown(f"""
            <div class="data-row">
                <span class="data-label">{label}</span>
                <span class="data-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_price_chart(self, price_data: pd.DataFrame, ticker: str):
        """Render minimal price chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=price_data.index,
            open=price_data['Open'],
            high=price_data['High'],
            low=price_data['Low'],
            close=price_data['Close'],
            name=ticker,
            increasing_line_color='#10B981',
            decreasing_line_color='#EF4444'
        ))
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=40, b=40),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Inter, -apple-system, sans-serif", size=12),
            xaxis=dict(
                gridcolor='#F3F4F6',
                zerolinecolor='#E5E7EB'
            ),
            yaxis=dict(
                gridcolor='#F3F4F6',
                zerolinecolor='#E5E7EB',
                side='right'
            ),
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analysis_results(self, agent_results: Dict[str, str]):
        """Render analysis results in clean tabs."""
        tabs = st.tabs(list(agent_results.keys()))
        
        for idx, (agent_name, result) in enumerate(agent_results.items()):
            with tabs[idx]:
                st.markdown(f"""
                <div style="padding: 1rem 0;">
                    {result}
                </div>
                """, unsafe_allow_html=True)
    
    def _format_market_cap(self, value: float) -> str:
        """Format market cap with appropriate units."""
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        elif value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.0f}"
    
    def _format_number(self, value: Any) -> str:
        """Format number or return dash for None."""
        if value is None or value == "정보 없음":
            return "—"
        try:
            return f"{float(value):.2f}"
        except:
            return str(value)
    
    def _format_percent(self, value: Any) -> str:
        """Format percentage."""
        if value is None or value == "정보 없음":
            return "—"
        try:
            return f"{float(value)*100:.2f}%"
        except:
            return str(value)
    
    def _format_volume(self, value: float) -> str:
        """Format volume with appropriate units."""
        if value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:,.0f}"
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render minimal sidebar for user inputs."""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding-bottom: 2rem; border-bottom: 1px solid #E5E7EB;">
                <h2 style="font-size: 1.5rem; margin: 0; font-weight: 700;">💎 AI 투자 분석</h2>
                <p style="color: #6B7280; font-size: 0.875rem; margin-top: 0.5rem;">Smart Stock AI</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Market selection
            market = st.radio(
                "시장 선택",
                options=["미국장", "한국장"],
                key="market_select",
                label_visibility="visible"
            )
            
            # Ticker input
            ticker = st.text_input(
                "종목 코드",
                placeholder="AAPL, 005930...",
                key="ticker_input",
                help="미국: AAPL, MSFT / 한국: 005930, 035420"
            ).upper().strip()
            
            # Industry selection
            if market == "미국장":
                industries = ["Technology", "Healthcare", "Finance", "Consumer", "Energy", "Industrial"]
            else:
                industries = ["전자/IT", "제약/바이오", "금융", "소비재", "에너지/화학", "산업재"]
            
            industry = st.selectbox(
                "산업 분류",
                options=industries,
                key="industry_select"
            )
            
            # Analysis period
            period = st.select_slider(
                "분석 기간",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}개월",
                key="period_select"
            )
            
            st.markdown("<hr style='margin: 2rem 0; border-color: #E5E7EB;'>", unsafe_allow_html=True)
            
            # Analysis button
            analyze_clicked = st.button(
                "분석 시작",
                type="primary",
                use_container_width=True,
                key="analyze_btn"
            )
            
            # Clear button
            clear_clicked = st.button(
                "초기화",
                use_container_width=True,
                key="clear_btn"
            )
            
            # Advanced options (collapsed by default)
            with st.expander("고급 설정"):
                include_recommendations = st.checkbox(
                    "연관 종목 추천",
                    value=True,
                    key="include_recs"
                )
                
                use_cache = st.checkbox(
                    "캐시 사용",
                    value=True,
                    key="use_cache"
                )
            
            return {
                'ticker': ticker,
                'market': market,
                'industry': industry,
                'period': period,
                'actions': {
                    'analyze': analyze_clicked,
                    'clear': clear_clicked
                },
                'advanced': {
                    'include_recommendations': include_recommendations,
                    'use_cache': use_cache
                }
            }