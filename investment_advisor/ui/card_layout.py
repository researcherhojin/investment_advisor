"""
Modern Card-Based Layout Manager

Provides a clean, card-based UI design with better visual hierarchy and interactivity.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CardLayoutManager:
    """Modern card-based layout manager for better UX."""
    
    def __init__(self):
        self.theme = self._get_theme()
        
    def _get_theme(self) -> Dict[str, Any]:
        """Get current theme settings."""
        return {
            'primary': '#3B82F6',      # Blue
            'success': '#10B981',      # Green
            'danger': '#EF4444',       # Red
            'warning': '#F59E0B',      # Amber
            'neutral': '#6B7280',      # Gray
            'background': '#FFFFFF',
            'surface': '#F9FAFB',
            'card_bg': '#FFFFFF',
            'text_primary': '#111827',
            'text_secondary': '#6B7280',
            'border': '#E5E7EB',
            'shadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }
    
    def setup_page(self):
        """Setup modern page styling with animations."""
        st.markdown(f"""
        <style>
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}
        
        /* Smooth animations */
        * {{
            transition: all 0.3s ease;
        }}
        
        /* Hide default Streamlit elements */
        #MainMenu, footer, header {{
            visibility: hidden;
        }}
        
        /* Main container */
        .main .block-container {{
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Card styles */
        .analysis-card {{
            background: {self.theme['card_bg']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid {self.theme['border']};
            box-shadow: {self.theme['shadow']};
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .analysis-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        /* Header card */
        .header-card {{
            background: linear-gradient(135deg, {self.theme['primary']} 0%, #2563EB 100%);
            color: white;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
        }}
        
        /* Decision card */
        .decision-card {{
            background: white;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin: 1.5rem 0;
            border: 2px solid;
            position: relative;
            overflow: hidden;
        }}
        
        .decision-card.buy {{
            border-color: {self.theme['success']};
            background: linear-gradient(to bottom, #F0FDF4 0%, #FFFFFF 100%);
        }}
        
        .decision-card.sell {{
            border-color: {self.theme['danger']};
            background: linear-gradient(to bottom, #FEF2F2 0%, #FFFFFF 100%);
        }}
        
        .decision-card.hold {{
            border-color: {self.theme['warning']};
            background: linear-gradient(to bottom, #FFFBEB 0%, #FFFFFF 100%);
        }}
        
        /* Metric cards */
        .metric-card {{
            background: {self.theme['surface']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid {self.theme['border']};
            height: 100%;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 600;
            margin: 0.5rem 0;
        }}
        
        .metric-label {{
            color: {self.theme['text_secondary']};
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Agent cards */
        .agent-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid {self.theme['border']};
            position: relative;
        }}
        
        .agent-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }}
        
        .agent-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-right: 1rem;
        }}
        
        .confidence-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .confidence-high {{
            background: {self.theme['success']}20;
            color: {self.theme['success']};
        }}
        
        .confidence-medium {{
            background: {self.theme['warning']}20;
            color: {self.theme['warning']};
        }}
        
        .confidence-low {{
            background: {self.theme['danger']}20;
            color: {self.theme['danger']};
        }}
        
        /* Progress indicators */
        .progress-ring {{
            transform: rotate(-90deg);
        }}
        
        /* Tooltips */
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
        }}
        
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 0.5rem;
            border-radius: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem;
            }}
            
            .analysis-card, .agent-card {{
                padding: 1rem;
            }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, market: str, company_name: str):
        """Render modern header card."""
        flag = "🇺🇸" if market == "미국장" else "🇰🇷"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        st.markdown(f"""
        <div class="header-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">{ticker}</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.125rem;">{company_name}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{flag}</div>
                    <div style="opacity: 0.8; font-size: 0.875rem;">{market}</div>
                    <div style="opacity: 0.7; font-size: 0.75rem; margin-top: 0.5rem;">{current_time}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_decision_card(self, decision: str):
        """Render the main decision as a prominent card."""
        # Determine decision type and styling
        if "매수" in decision or "BUY" in decision.upper():
            decision_type = "매수"
            decision_class = "buy"
            icon = "📈"
            color = self.theme['success']
        elif "매도" in decision or "SELL" in decision.upper():
            decision_type = "매도"
            decision_class = "sell"
            icon = "📉"
            color = self.theme['danger']
        else:
            decision_type = "보유"
            decision_class = "hold"
            icon = "⏸️"
            color = self.theme['warning']
        
        st.markdown(f"""
        <div class="decision-card {decision_class}">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h2 style="color: {color}; margin: 0; font-size: 2.5rem; font-weight: 700;">
                {decision_type} 추천
            </h2>
            <p style="margin-top: 1rem; color: {self.theme['text_secondary']}; font-size: 1rem;">
                AI 에이전트들의 종합 분석 결과
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 상세 분석 보기", expanded=False):
            st.markdown(decision)
    
    def render_metrics_row(self, stock_info: Dict[str, Any], technical_data: Dict[str, Any]):
        """Render key metrics in a card-based row."""
        cols = st.columns(4)
        
        # Current Price
        with cols[0]:
            current_price = stock_info.get('currentPrice', 0)
            price_change = technical_data.get('returns_1d', 0) * 100 if technical_data else 0
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">현재가</div>
                <div class="metric-value">${current_price:.2f}</div>
                <div style="color: {'#10B981' if price_change >= 0 else '#EF4444'};">
                    {price_change:+.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # RSI
        with cols[1]:
            rsi = technical_data.get('rsi', 50) if technical_data else 50
            rsi_status = "과매수" if rsi > 70 else "과매도" if rsi < 30 else "정상"
            rsi_color = self.theme['danger'] if rsi > 70 else self.theme['success'] if rsi < 30 else self.theme['neutral']
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">RSI</div>
                <div class="metric-value">{rsi:.1f}</div>
                <div style="color: {rsi_color};">{rsi_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # PER
        with cols[2]:
            per = stock_info.get('PER', 'N/A')
            per_display = f"{per:.1f}" if isinstance(per, (int, float)) else per
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">PER</div>
                <div class="metric-value">{per_display}</div>
                <div style="color: {self.theme['text_secondary']};">수익성 지표</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Market Cap
        with cols[3]:
            market_cap = stock_info.get('marketCap', 0)
            if market_cap > 1e12:
                cap_display = f"${market_cap/1e12:.1f}T"
            elif market_cap > 1e9:
                cap_display = f"${market_cap/1e9:.1f}B"
            else:
                cap_display = f"${market_cap/1e6:.0f}M"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">시가총액</div>
                <div class="metric-value">{cap_display}</div>
                <div style="color: {self.theme['text_secondary']};">기업 규모</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_agent_card(self, agent_name: str, analysis: str, icon: str, confidence: str = "보통"):
        """Render individual agent analysis as a card."""
        # Determine confidence styling
        confidence_class = {
            "높음": "confidence-high",
            "보통": "confidence-medium", 
            "낮음": "confidence-low"
        }.get(confidence, "confidence-medium")
        
        # Agent icon background colors
        icon_colors = {
            "🏢": self.theme['primary'],
            "🏭": self.theme['warning'],
            "🌍": self.theme['success'],
            "📊": self.theme['danger'],
            "⚠️": self.theme['neutral']
        }
        
        icon_bg = icon_colors.get(icon, self.theme['primary'])
        
        with st.container():
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-header">
                    <div style="display: flex; align-items: center;">
                        <div class="agent-icon" style="background: {icon_bg}20;">
                            {icon}
                        </div>
                        <div>
                            <h3 style="margin: 0; font-weight: 600;">{agent_name}</h3>
                            <p style="margin: 0; color: {self.theme['text_secondary']}; font-size: 0.875rem;">
                                전문 분석 의견
                            </p>
                        </div>
                    </div>
                    <div class="{confidence_class} confidence-badge">
                        신뢰도: {confidence}
                    </div>
                </div>
                <div style="color: {self.theme['text_primary']}; line-height: 1.6;">
                    {self._clean_analysis_text(analysis)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_agent_analysis_grid(self, agent_results: Dict[str, str]):
        """Render all agent analyses in a responsive grid."""
        agent_configs = {
            "기업분석가": ("🏢", "기업 재무 및 경영 분석"),
            "산업전문가": ("🏭", "산업 동향 및 경쟁 분석"),
            "거시경제전문가": ("🌍", "거시경제 환경 분석"),
            "기술분석가": ("📊", "차트 및 기술적 지표 분석"),
            "리스크관리자": ("⚠️", "투자 위험 요소 평가")
        }
        
        # Filter out mediator
        filtered_results = {k: v for k, v in agent_results.items() if k != "중재자"}
        
        # Create a 2-column layout for agents
        col1, col2 = st.columns(2)
        
        for idx, (agent, analysis) in enumerate(filtered_results.items()):
            if analysis and analysis.strip():
                icon, description = agent_configs.get(agent, ("📋", "분석"))
                
                # Alternate between columns
                with col1 if idx % 2 == 0 else col2:
                    self.render_agent_card(agent, analysis, icon)
    
    def render_interactive_chart(self, price_history: pd.DataFrame, ticker: str):
        """Render an interactive price chart with modern styling."""
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=price_history.index,
            open=price_history['Open'],
            high=price_history['High'],
            low=price_history['Low'],
            close=price_history['Close'],
            name='주가',
            increasing_line_color=self.theme['success'],
            decreasing_line_color=self.theme['danger']
        ))
        
        # Add moving averages
        if len(price_history) >= 20:
            ma20 = price_history['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=price_history.index,
                y=ma20,
                name='MA20',
                line=dict(color=self.theme['primary'], width=2)
            ))
        
        if len(price_history) >= 50:
            ma50 = price_history['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(
                x=price_history.index,
                y=ma50,
                name='MA50',
                line=dict(color=self.theme['warning'], width=2)
            ))
        
        # Update layout with modern styling
        fig.update_layout(
            title=f"{ticker} 주가 차트",
            yaxis_title="가격 ($)",
            xaxis_title="날짜",
            height=500,
            template="plotly_white",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date'
            ),
            yaxis=dict(
                fixedrange=False
            )
        )
        
        # Add range selector buttons
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="전체")
                ]),
                bgcolor=self.theme['surface'],
                activecolor=self.theme['primary']
            )
        )
        
        return fig
    
    def _clean_analysis_text(self, text: str) -> str:
        """Clean and format analysis text for display."""
        # Remove redundant headers and metadata
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            # Skip headers with agent names
            if line.startswith('##') and ('분석' in line or '의견' in line):
                continue
            # Skip metadata lines
            if any(keyword in line for keyword in ['데이터 품질', '분석 시점', '신뢰도', '---']):
                continue
            
            cleaned.append(line)
        
        return '<br>'.join(cleaned).strip()
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render modern sidebar with better organization."""
        with st.sidebar:
            # Logo/Branding
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
                <h2 style="color: #3B82F6; margin: 0;">💎 Smart Stock AI</h2>
                <p style="color: #6B7280; margin: 0.5rem 0 0 0; font-size: 0.875rem;">
                    인공지능 투자 자문 서비스
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Market Selection
            st.markdown("### 📍 시장 선택")
            market = st.radio(
                "label",
                ["🇺🇸 미국 시장", "🇰🇷 한국 시장"],
                label_visibility="collapsed",
                horizontal=False
            )
            market = "미국장" if "미국" in market else "한국장"
            
            st.markdown("---")
            
            # Stock Input
            st.markdown("### 🔍 종목 검색")
            ticker = st.text_input(
                "종목 코드를 입력하세요",
                placeholder="예: AAPL, 005930",
                label_visibility="collapsed"
            ).upper().strip()
            
            # Industry Selection
            if market == "미국장":
                industries = ["Technology", "Healthcare", "Finance", "Consumer", "Energy"]
            else:
                industries = ["반도체", "전자", "금융", "바이오", "자동차"]
            
            industry = st.selectbox(
                "산업 분류",
                industries,
                help="해당 종목의 산업을 선택하세요"
            )
            
            # Analysis Period
            st.markdown("### ⏱️ 분석 기간")
            period = st.slider(
                "label",
                min_value=3,
                max_value=24,
                value=12,
                step=3,
                format="%d개월",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Action Buttons
            col1, col2 = st.columns(2)
            with col1:
                analyze_button = st.button(
                    "🚀 분석 시작",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                clear_button = False
                if st.session_state.get('analysis_results'):
                    clear_button = st.button(
                        "🔄 초기화",
                        use_container_width=True
                    )
            
            # Advanced Options (Collapsible)
            with st.expander("⚙️ 고급 설정", expanded=False):
                include_recommendations = st.checkbox("연관 종목 추천", value=True)
                show_detailed_analysis = st.checkbox("상세 분석 표시", value=True)
                enable_alerts = st.checkbox("가격 알림 설정", value=False)
            
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
                    'enable_alerts': enable_alerts
                }
            }
    
    def render_loading_state(self):
        """Render a modern loading state."""
        st.markdown("""
        <div style="text-align: center; padding: 4rem 0;">
            <div class="spinner" style="margin: 0 auto;">
                <div style="font-size: 3rem; animation: spin 2s linear infinite;">⚡</div>
            </div>
            <h3 style="margin-top: 1rem; color: #6B7280;">AI 에이전트가 분석 중입니다...</h3>
            <p style="color: #9CA3AF;">잠시만 기다려주세요</p>
        </div>
        
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def display_error(self, message: str):
        """Display error in a styled card."""
        st.markdown(f"""
        <div class="analysis-card" style="border-left: 4px solid {self.theme['danger']}; background: #FEF2F2;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 1rem;">❌</div>
                <div>
                    <h4 style="margin: 0; color: {self.theme['danger']};">오류 발생</h4>
                    <p style="margin: 0.5rem 0 0 0; color: {self.theme['text_primary']};">{message}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_success(self, message: str):
        """Display success in a styled card."""
        st.markdown(f"""
        <div class="analysis-card" style="border-left: 4px solid {self.theme['success']}; background: #F0FDF4;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 1rem;">✅</div>
                <div>
                    <h4 style="margin: 0; color: {self.theme['success']};">성공</h4>
                    <p style="margin: 0.5rem 0 0 0; color: {self.theme['text_primary']};">{message}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)