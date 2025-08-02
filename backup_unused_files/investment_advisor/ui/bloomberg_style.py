"""
Bloomberg Terminal Style UI

Professional financial terminal-inspired design.
Dark theme with high contrast for better readability.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime

class BloombergStyleUI:
    """Bloomberg Terminal inspired UI."""
    
    def __init__(self):
        self.colors = {
            'bg_primary': '#000000',
            'bg_secondary': '#0A0A0A',
            'bg_card': '#141414',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0',
            'text_muted': '#606060',
            'green': '#00FF41',
            'red': '#FF0033',
            'amber': '#FFB000',
            'blue': '#00A8FF',
            'border': '#303030'
        }
    
    def apply_theme(self):
        """Apply Bloomberg Terminal style theme."""
        st.markdown("""
        <style>
        /* Import monospace font */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        
        /* Global reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Main app background */
        .stApp {
            background-color: #000000;
        }
        
        /* All text should be monospace */
        * {
            font-family: 'IBM Plex Mono', 'Consolas', 'Monaco', monospace !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Main container */
        .main .block-container {
            padding: 1rem;
            max-width: 100%;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0A0A0A;
            border-right: 1px solid #303030;
        }
        
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #000000;
            color: #00FF41;
            border: 1px solid #00FF41;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #00FF41;
            color: #000000;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #000000;
            color: #00FF41;
            border: 1px solid #303030;
            font-family: 'IBM Plex Mono', monospace;
            text-transform: uppercase;
        }
        
        /* Radio buttons */
        .stRadio > div {
            background-color: transparent;
        }
        
        .stRadio label {
            color: #B0B0B0 !important;
            font-size: 0.875rem;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Data tables */
        .dataframe {
            background-color: #000000 !important;
            color: #00FF41 !important;
        }
        
        /* Remove all shadows */
        * {
            box-shadow: none !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #000000;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #303030;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #404040;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, company_name: str, price: float, change: float, change_pct: float):
        """Render Bloomberg-style header."""
        color = self.colors['green'] if change >= 0 else self.colors['red']
        arrow = "▲" if change >= 0 else "▼"
        
        st.markdown(f"""
        <div style="
            background: {self.colors['bg_card']};
            border: 1px solid {self.colors['border']};
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="
                        color: {self.colors['text_primary']};
                        font-size: 1.5rem;
                        margin: 0;
                    ">{ticker}</h1>
                    <p style="
                        color: {self.colors['text_secondary']};
                        font-size: 0.875rem;
                        margin: 0.25rem 0 0 0;
                    ">{company_name}</p>
                </div>
                <div style="text-align: right;">
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: {self.colors['text_primary']};
                    ">${price:,.2f}</div>
                    <div style="
                        font-size: 1rem;
                        color: {color};
                        margin-top: 0.25rem;
                    ">
                        {arrow} {abs(change):.2f} ({abs(change_pct):.2f}%)
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """Render market indices in Bloomberg style."""
        # Container for indices
        st.markdown(f"""
        <div style="
            background: {self.colors['bg_card']};
            border: 1px solid {self.colors['border']};
            padding: 1rem;
            margin-bottom: 1rem;
        ">
        """, unsafe_allow_html=True)
        
        # Create columns for each index
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                color = self.colors['green'] if change >= 0 else self.colors['red']
                arrow = "▲" if change >= 0 else "▼"
                
                # Special handling for VIX
                if name == "VIX":
                    if current < 20:
                        vix_bg = self.colors['green']
                        status = "LOW"
                    elif current < 30:
                        vix_bg = self.colors['amber']
                        status = "MED"
                    else:
                        vix_bg = self.colors['red']
                        status = "HIGH"
                    
                    # VIX special card
                    st.markdown(f"""
                    <div style="
                        background: {vix_bg};
                        color: {self.colors['bg_primary']};
                        padding: 0.75rem;
                        border-radius: 4px;
                        text-align: center;
                    ">
                        <div style="font-size: 0.75rem; font-weight: 600; margin-bottom: 0.25rem;">
                            {name}
                        </div>
                        <div style="font-size: 1.25rem; font-weight: 700;">
                            {current:.2f}
                        </div>
                        <div style="font-size: 0.625rem; margin-top: 0.25rem;">
                            {status}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Regular index card
                    st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem;">
                        <div style="
                            color: {self.colors['text_secondary']};
                            font-size: 0.75rem;
                            text-transform: uppercase;
                            margin-bottom: 0.25rem;
                        ">{name}</div>
                        <div style="
                            color: {self.colors['text_primary']};
                            font-size: 1.125rem;
                            font-weight: 600;
                        ">{current:,.2f}</div>
                        <div style="
                            color: {color};
                            font-size: 0.75rem;
                            margin-top: 0.25rem;
                        ">{arrow} {abs(change):.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_data_table(self, title: str, data: Dict[str, Any]):
        """Render data in Bloomberg table style."""
        st.markdown(f"""
        <div style="
            background: {self.colors['bg_card']};
            border: 1px solid {self.colors['border']};
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <h3 style="
                color: {self.colors['amber']};
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
                border-bottom: 1px solid {self.colors['border']};
                padding-bottom: 0.5rem;
            ">{title}</h3>
        """, unsafe_allow_html=True)
        
        for key, value in data.items():
            if value is None or value == "정보 없음":
                display_value = "N/A"
                value_color = self.colors['text_muted']
            else:
                display_value = self._format_value(key, value)
                value_color = self.colors['text_primary']
            
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid {self.colors['bg_secondary']};
            ">
                <span style="
                    color: {self.colors['text_secondary']};
                    font-size: 0.875rem;
                ">{key}</span>
                <span style="
                    color: {value_color};
                    font-size: 0.875rem;
                    font-weight: 500;
                ">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_chart(self, df: pd.DataFrame, title: str = "PRICE HISTORY"):
        """Render Bloomberg-style chart."""
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color=self.colors['green'],
            decreasing_line_color=self.colors['red'],
            increasing_fillcolor=self.colors['green'],
            decreasing_fillcolor=self.colors['red']
        ))
        
        # Volume bars
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=self.colors['text_muted'],
            yaxis='y2',
            opacity=0.3
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color=self.colors['amber'], size=14),
                x=0
            ),
            plot_bgcolor=self.colors['bg_primary'],
            paper_bgcolor=self.colors['bg_card'],
            font=dict(
                family="IBM Plex Mono, monospace",
                color=self.colors['text_secondary']
            ),
            xaxis=dict(
                gridcolor=self.colors['bg_secondary'],
                linecolor=self.colors['border'],
                zerolinecolor=self.colors['border']
            ),
            yaxis=dict(
                title="PRICE",
                gridcolor=self.colors['bg_secondary'],
                linecolor=self.colors['border'],
                zerolinecolor=self.colors['border'],
                side='right'
            ),
            yaxis2=dict(
                title="VOLUME",
                overlaying='y',
                side='left',
                gridcolor=self.colors['bg_secondary'],
                showgrid=False
            ),
            height=400,
            margin=dict(l=0, r=0, t=40, b=20),
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analysis_section(self, agent_name: str, content: str):
        """Render analysis section in Bloomberg style."""
        st.markdown(f"""
        <div style="
            background: {self.colors['bg_card']};
            border: 1px solid {self.colors['border']};
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <h3 style="
                color: {self.colors['blue']};
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
            ">[{agent_name}]</h3>
            <div style="
                color: {self.colors['text_primary']};
                font-size: 0.875rem;
                line-height: 1.6;
                white-space: pre-wrap;
            ">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render Bloomberg-style sidebar."""
        with st.sidebar:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 1rem 0;
                border-bottom: 1px solid {self.colors['border']};
                margin-bottom: 1rem;
            ">
                <div style="
                    color: {self.colors['amber']};
                    font-size: 1.25rem;
                    font-weight: 700;
                    letter-spacing: 0.1em;
                ">BLOOMBERG</div>
                <div style="
                    color: {self.colors['text_secondary']};
                    font-size: 0.75rem;
                    margin-top: 0.25rem;
                ">AI TERMINAL</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Market selection
            st.markdown(f"""
            <div style="color: {self.colors['text_secondary']}; font-size: 0.875rem; margin-bottom: 0.5rem;">
                MARKET
            </div>
            """, unsafe_allow_html=True)
            
            market = st.radio(
                "Market Selection",
                options=["US", "KR"],
                format_func=lambda x: "미국" if x == "US" else "한국",
                label_visibility="collapsed"
            )
            
            # Ticker input
            st.markdown(f"""
            <div style="color: {self.colors['text_secondary']}; font-size: 0.875rem; margin: 1rem 0 0.5rem 0;">
                TICKER
            </div>
            """, unsafe_allow_html=True)
            
            ticker = st.text_input(
                "Ticker Input",
                placeholder="AAPL",
                label_visibility="collapsed"
            ).upper()
            
            # Industry
            st.markdown(f"""
            <div style="color: {self.colors['text_secondary']}; font-size: 0.875rem; margin: 1rem 0 0.5rem 0;">
                SECTOR
            </div>
            """, unsafe_allow_html=True)
            
            industries = ["TECH", "HEALTH", "FIN", "CONS", "ENERGY", "IND"] if market == "US" else ["전자", "바이오", "금융", "소비재", "에너지", "산업재"]
            industry = st.selectbox("Sector Selection", industries, label_visibility="collapsed")
            
            # Period
            st.markdown(f"""
            <div style="color: {self.colors['text_secondary']}; font-size: 0.875rem; margin: 1rem 0 0.5rem 0;">
                PERIOD
            </div>
            """, unsafe_allow_html=True)
            
            period = st.select_slider(
                "Analysis Period",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}M",
                label_visibility="collapsed"
            )
            
            st.markdown("<hr style='border-color: #303030; margin: 2rem 0;'>", unsafe_allow_html=True)
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                analyze = st.button("ANALYZE", type="primary", use_container_width=True)
            with col2:
                clear = st.button("CLEAR", use_container_width=True)
            
            return {
                'ticker': ticker,
                'market': "미국장" if market == "US" else "한국장",
                'industry': industry,
                'period': period,
                'actions': {
                    'analyze': analyze,
                    'clear': clear
                },
                'advanced': {
                    'include_recommendations': True,
                    'use_cache': True
                }
            }
    
    def _format_value(self, key: str, value: Any) -> str:
        """Format value based on type."""
        if isinstance(value, (int, float)):
            if '시가총액' in key or 'Cap' in key:
                return self._format_market_cap(value)
            elif '수익률' in key or '%' in key:
                return f"{value:.2f}%"
            elif '거래량' in key or 'Volume' in key:
                return self._format_volume(value)
            elif any(k in key for k in ['PER', 'PBR', 'ROE', 'EPS', '베타']):
                return f"{value:.2f}"
            else:
                return f"{value:,.2f}"
        return str(value)
    
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