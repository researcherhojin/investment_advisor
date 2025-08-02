"""
Ultra Minimal Layout Manager

Clean, simple, and intuitive design focusing on essential information only.
Inspired by modern fintech apps like Robinhood and Webull.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
import plotly.graph_objects as go
import logging
import numpy as np

from ..visualization.technical_charts import TechnicalChartGenerator

logger = logging.getLogger(__name__)


class MinimalLayoutManager:
    """Ultra minimal and clean layout manager."""
    
    def __init__(self):
        self.tech_chart_generator = TechnicalChartGenerator()
    
    def setup_page(self):
        """Setup minimal page styling."""
        st.markdown("""
        <style>
        /* Clean font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Hide Streamlit elements */
        #MainMenu, footer, header, .stDeployButton {
            visibility: hidden;
        }
        
        /* Clean main area */
        .main .block-container {
            padding: 1rem 2rem;
            max-width: 1000px;
        }
        
        /* Clean sidebar */
        .css-1d391kg {
            background: #fafafa;
            border-right: 1px solid #e0e0e0;
        }
        
        /* Modern buttons */
        .stButton > button {
            border-radius: 6px;
            border: none;
            font-weight: 500;
            height: 2.5rem;
        }
        
        /* Remove extra spacing */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: #f5f5f5;
            border-radius: 4px;
            padding: 0.3rem 0.8rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Simple clean header."""
        st.markdown("""
        # 📊 Smart Stock
        *AI 주식 분석*
        """)
        st.divider()
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Clean minimal sidebar."""
        with st.sidebar:
            st.markdown("## 분석하기")
            
            # Market - simple radio
            market = st.radio(
                "시장", 
                ["🇺🇸 미국", "🇰🇷 한국"],
                horizontal=True,
                label_visibility="collapsed"
            )
            market = "미국장" if "미국" in market else "한국장"
            
            # Ticker - clean input
            ticker = st.text_input(
                "종목",
                placeholder="AAPL, MSFT, 삼성전자...",
                label_visibility="collapsed"
            ).upper().strip()
            
            # Industry - simplified
            if market == "미국장":
                industries = ["Tech", "Healthcare", "Finance", "Consumer", "Energy"]
            else:
                industries = ["반도체", "전자", "금융", "바이오", "자동차"]
            
            industry = st.selectbox("산업", industries, label_visibility="collapsed")
            
            # Period - simple
            period = st.selectbox(
                "기간", 
                [3, 6, 12], 
                index=2,
                format_func=lambda x: f"{x}개월",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Single action button
            analyze_button = st.button(
                "🚀 분석하기",
                type="primary",
                use_container_width=True
            )
            
            # Clear if needed
            clear_button = False
            if st.session_state.get('analysis_results'):
                clear_button = st.button("다시하기", use_container_width=True)
        
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
                'include_recommendations': True,
                'show_detailed_analysis': True,
                'export_results': False
            }
        }
    
    def render_main_content(self):
        """Simple welcome screen."""
        # Center content
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 4rem 0;">
                <h2 style="color: #666; font-weight: 400;">시작하기</h2>
                <p style="color: #999; margin: 1rem 0 2rem;">
                    왼쪽에 종목을 입력하고<br>
                    AI 분석을 받아보세요
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Simple feature cards
        col1, col2, col3 = st.columns(3)
        
        features = [
            ("🤖", "AI 분석", "5명의 전문가가 분석"),
            ("📈", "실시간", "최신 데이터 기반"),
            ("🎯", "명확한 결론", "매수/매도/보유")
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem 1rem; background: white; border-radius: 8px; border: 1px solid #f0f0f0;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <h4 style="margin: 0.5rem 0; color: #333;">{title}</h4>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">{desc}</p>
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
        """Display results in minimal clean format."""
        
        # Header
        self._render_ticker_header(ticker, market, analysis_data)
        
        # Main decision - big and clear
        self._render_decision(final_decision)
        
        # Key info + chart side by side
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_key_info(analysis_data.get('stock_info', {}))
        
        with col2:
            if not price_history.empty:
                self._render_chart(price_history, ticker)
        
        # Expert opinions - simple tabs
        self._render_expert_tabs(agent_results)
    
    def _render_ticker_header(self, ticker: str, market: str, analysis_data: Dict[str, Any]):
        """Clean ticker header."""
        company_name = self._get_company_name(analysis_data)
        flag = "🇺🇸" if market == "미국장" else "🇰🇷"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            # {ticker}
            {company_name}
            """)
        with col2:
            st.markdown(f"""
            <div style="text-align: right; padding-top: 1rem;">
                <div style="font-size: 1.5rem;">{flag}</div>
                <small style="color: #666;">{market}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_decision(self, decision: str):
        """Big clear decision display."""
        # Extract decision type
        if "매수" in decision or "BUY" in decision.upper():
            decision_type = "매수"
            color = "#22c55e"
            bg = "#f0fdf4"
            icon = "📈"
        elif "매도" in decision or "SELL" in decision.upper():
            decision_type = "매도"
            color = "#ef4444"
            bg = "#fef2f2"
            icon = "📉"
        else:
            decision_type = "보유"
            color = "#f59e0b"
            bg = "#fffbeb"
            icon = "⏸️"
        
        st.markdown(f"""
        <div style="
            background: {bg}; 
            border: 2px solid {color}; 
            border-radius: 12px; 
            padding: 2rem; 
            text-align: center; 
            margin: 2rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
            <h2 style="color: {color}; margin: 0; font-weight: 600;">{decision_type}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Details in expandable
        with st.expander("📋 상세 분석", expanded=False):
            st.write(decision)
    
    def _render_key_info(self, stock_info: Dict[str, Any]):
        """Essential stock info only."""
        st.markdown("### 핵심 정보")
        
        if not stock_info:
            st.info("정보 로딩중...")
            return
        
        # Current price
        if 'currentPrice' in stock_info:
            st.metric("현재가", f"${stock_info['currentPrice']:.2f}")
        elif '현재가' in stock_info and stock_info['현재가'] != "정보 없음":
            st.metric("현재가", str(stock_info['현재가']))
        
        # PER
        if 'PER' in stock_info and stock_info['PER'] != "정보 없음":
            st.metric("PER", str(stock_info['PER']))
        
        # Market Cap
        if 'marketCap' in stock_info and isinstance(stock_info['marketCap'], (int, float)):
            market_cap = stock_info['marketCap']
            if market_cap > 1e12:
                cap_display = f"${market_cap/1e12:.1f}T"
            elif market_cap > 1e9:
                cap_display = f"${market_cap/1e9:.1f}B"
            else:
                cap_display = f"${market_cap/1e6:.0f}M"
            st.metric("시가총액", cap_display)
    
    def _render_chart(self, price_history: pd.DataFrame, ticker: str):
        """Simple clean chart."""
        st.markdown("### 주가 차트")
        
        try:
            if 'Close' in price_history.columns:
                # Create minimal plotly chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=price_history.index,
                    y=price_history['Close'],
                    mode='lines',
                    line=dict(color='#3b82f6', width=2),
                    hovertemplate='%{y:.2f}<extra></extra>'
                ))
                
                fig.update_layout(
                    height=300,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis=dict(
                        showgrid=False,
                        showticklabels=False,
                        zeroline=False
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='#f0f0f0',
                        showticklabels=True,
                        zeroline=False
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.line_chart(price_history)
        except:
            st.line_chart(price_history.get('Close', price_history))
    
    def _render_expert_tabs(self, agent_results: Dict[str, str]):
        """Simple expert opinion tabs."""
        if not agent_results:
            return
        
        st.markdown("### 전문가 의견")
        
        # Clean agent names
        clean_names = {
            "기업분석가": "기업",
            "산업전문가": "산업",
            "거시경제전문가": "경제",
            "기술분석가": "기술",
            "리스크관리자": "리스크"
        }
        
        # Filter out mediator (already shown as main decision)
        filtered_results = {k: v for k, v in agent_results.items() if k != "중재자"}
        
        if filtered_results:
            tab_names = [clean_names.get(agent, agent) for agent in filtered_results.keys()]
            tabs = st.tabs(tab_names)
            
            for i, (agent, analysis) in enumerate(filtered_results.items()):
                with tabs[i]:
                    if analysis and analysis.strip():
                        # Special handling for technical analysis
                        # Agent name is "기술분석가" but tab name is "기술"
                        if agent == "기술분석가":
                            self._render_technical_analysis_with_charts(analysis)
                        else:
                            # Clean up analysis text
                            clean_text = self._clean_text(analysis)
                            st.markdown(clean_text)
                    else:
                        st.info("분석 준비중...")
    
    def _clean_text(self, text: str) -> str:
        """Clean up analysis text."""
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            # Skip headers with agent names
            if line.startswith('## ') and ('분석가' in line or '의견' in line):
                continue
            # Skip technical metadata
            if '데이터 품질' in line or '분석 시점' in line or '신뢰도' in line:
                continue
            # Skip footer
            if line.startswith('---') or 'AI 기반' in line:
                continue
            
            cleaned.append(line)
        
        return '\n'.join(cleaned).strip()
    
    def _get_company_name(self, analysis_data: Dict[str, Any]) -> str:
        """Get clean company name."""
        stock_info = analysis_data.get('stock_info', {})
        
        for field in ['longName', 'shortName', '회사명']:
            if field in stock_info and stock_info[field]:
                name = stock_info[field]
                if name not in ["정보 없음", "N/A", ""]:
                    return name
        
        return ""
    
    def display_error(self, error_message: str):
        """Clean error display."""
        st.error(f"❌ {error_message}")
    
    def display_warning(self, warning_message: str):
        """Clean warning display."""
        st.warning(f"⚠️ {warning_message}")
    
    def display_success(self, success_message: str):
        """Clean success display."""
        st.success(f"✅ {success_message}")
    
    def _render_technical_analysis_with_charts(self, analysis: str):
        """Render technical analysis with improved readability."""
        
        # Get current analysis results
        if hasattr(st.session_state, 'analysis_results'):
            results = st.session_state.analysis_results
            if 'price_history' in results and not results['price_history'].empty:
                price_history = results['price_history']
                ticker = results.get('ticker', '')
                
                try:
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # Calculate indicators first
                    current_price = price_history['Close'].iloc[-1]
                    prev_price = price_history['Close'].iloc[-2] if len(price_history) > 1 else current_price
                    price_change = ((current_price - prev_price) / prev_price) * 100
                    
                    # 1. 핵심 지표 카드 (최상단)
                    st.markdown("### 📈 핵심 기술적 지표")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            label="현재가",
                            value=f"${current_price:.2f}",
                            delta=f"{price_change:+.2f}%"
                        )
                    
                    # Calculate RSI
                    def calculate_rsi_series(prices, period=14):
                        delta = prices.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        return rsi
                    
                    rsi_series = calculate_rsi_series(price_history['Close'])
                    current_rsi = rsi_series.iloc[-1] if not pd.isna(rsi_series.iloc[-1]) else 50
                    
                    with col2:
                        rsi_status = "과매수" if current_rsi > 70 else "과매도" if current_rsi < 30 else "중립"
                        st.metric(
                            label="RSI (14)",
                            value=f"{current_rsi:.1f}",
                            delta=rsi_status
                        )
                    
                    # Calculate MACD
                    exp1 = price_history['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = price_history['Close'].ewm(span=26, adjust=False).mean()
                    macd = exp1 - exp2
                    signal = macd.ewm(span=9, adjust=False).mean()
                    histogram = macd - signal
                    current_macd = histogram.iloc[-1] if not pd.isna(histogram.iloc[-1]) else 0
                    
                    with col3:
                        macd_signal = "상승 신호" if current_macd > 0 else "하락 신호"
                        st.metric(
                            label="MACD",
                            value=f"{current_macd:.2f}",
                            delta=macd_signal
                        )
                    
                    # Volume
                    volume_avg = price_history['Volume'].rolling(window=20).mean().iloc[-1]
                    current_volume = price_history['Volume'].iloc[-1]
                    volume_ratio = (current_volume / volume_avg) * 100 if volume_avg > 0 else 100
                    
                    with col4:
                        st.metric(
                            label="거래량 비율",
                            value=f"{volume_ratio:.0f}%",
                            delta="20일 평균 대비"
                        )
                    
                    # 2. 메인 차트 (단순화)
                    st.markdown("### 📊 차트 패턴 및 추세 분석")
                    
                    # Create cleaner technical chart with only 3 panels
                    fig = make_subplots(
                        rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.6, 0.2, 0.2],
                        subplot_titles=(None, None, None)
                    )
                    
                    # Price chart with candlesticks
                    fig.add_trace(
                        go.Candlestick(
                            x=price_history.index,
                            open=price_history['Open'],
                            high=price_history['High'],
                            low=price_history['Low'],
                            close=price_history['Close'],
                            name='가격',
                            increasing_line_color='#26a69a',
                            decreasing_line_color='#ef5350'
                        ),
                        row=1, col=1
                    )
                    
                    # Add only essential moving averages
                    if len(price_history) >= 20:
                        sma20 = price_history['Close'].rolling(window=20).mean()
                        fig.add_trace(
                            go.Scatter(
                                x=price_history.index,
                                y=sma20,
                                name='SMA 20',
                                line=dict(color='#2196F3', width=2)
                            ),
                            row=1, col=1
                        )
                    
                    if len(price_history) >= 50:
                        sma50 = price_history['Close'].rolling(window=50).mean()
                        fig.add_trace(
                            go.Scatter(
                                x=price_history.index,
                                y=sma50,
                                name='SMA 50',
                                line=dict(color='#FF9800', width=2)
                            ),
                            row=1, col=1
                        )
                    
                    # RSI subplot
                    fig.add_trace(
                        go.Scatter(
                            x=price_history.index,
                            y=rsi_series,
                            name='RSI',
                            line=dict(color='#9C27B0', width=2)
                        ),
                        row=2, col=1
                    )
                    
                    # RSI levels
                    fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=1, row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=1, row=2, col=1)
                    
                    # Volume subplot
                    volume_colors = ['#ef5350' if price_history['Close'].iloc[i] < price_history['Open'].iloc[i] else '#26a69a' 
                                   for i in range(len(price_history))]
                    
                    fig.add_trace(
                        go.Bar(
                            x=price_history.index,
                            y=price_history['Volume'],
                            name='거래량',
                            marker_color=volume_colors,
                            showlegend=False
                        ),
                        row=3, col=1
                    )
                    
                    # Update layout - clean and simple
                    fig.update_layout(
                        height=700,
                        showlegend=True,
                        xaxis_rangeslider_visible=False,
                        template='plotly_white',
                        hovermode='x unified',
                        margin=dict(l=50, r=50, t=30, b=30),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    
                    # Update axes
                    fig.update_yaxes(title_text="가격", row=1, col=1)
                    fig.update_yaxes(title_text="RSI", row=2, col=1)
                    fig.update_yaxes(title_text="거래량", row=3, col=1)
                    fig.update_xaxes(title_text="날짜", row=3, col=1)
                    
                    # Add subplot titles
                    fig.add_annotation(
                        text=f"<b>{ticker} 가격 차트</b>",
                        xref="paper", yref="paper",
                        x=0, y=0.95, showarrow=False,
                        font=dict(size=16)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    
                    # 3. 상세 지표 분석 (간소화)
                    st.markdown("### 📊 기술적 신호 요약")
                    
                    # 종합 신호 계산
                    buy_signals = 0
                    sell_signals = 0
                    neutral_signals = 0
                    
                    # 이동평균선 신호
                    if len(price_history) >= 20:
                        if current_price > sma20.iloc[-1]:
                            buy_signals += 1
                        else:
                            sell_signals += 1
                    
                    if len(price_history) >= 50:
                        if current_price > sma50.iloc[-1]:
                            buy_signals += 1
                        else:
                            sell_signals += 1
                    
                    # RSI 신호
                    if current_rsi < 30:
                        buy_signals += 1
                    elif current_rsi > 70:
                        sell_signals += 1
                    else:
                        neutral_signals += 1
                    
                    # MACD 신호
                    if current_macd > 0:
                        buy_signals += 1
                    else:
                        sell_signals += 1
                    
                    # 신호 요약 표시
                    total_signals = buy_signals + sell_signals + neutral_signals
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "매수 신호",
                            f"{buy_signals}/{total_signals}",
                            f"{(buy_signals/total_signals*100):.0f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "중립 신호",
                            f"{neutral_signals}/{total_signals}",
                            f"{(neutral_signals/total_signals*100):.0f}%" if total_signals > 0 else "0%"
                        )
                    
                    with col3:
                        st.metric(
                            "매도 신호",
                            f"{sell_signals}/{total_signals}",
                            f"{(sell_signals/total_signals*100):.0f}%"
                        )
                    
                    # 4. AI 분석 결과 (간소화)
                    st.markdown("### 🤖 AI 기술적 분석")
                    
                    # 텍스트 분석 결과를 더 읽기 쉽게 표시
                    clean_text = self._clean_text(analysis)
                    with st.container():
                        st.markdown(clean_text)
                    
                except Exception as e:
                    st.error(f"차트 생성 중 오류: {str(e)}")
                    logger.error(f"Error creating technical chart: {e}")
            else:
                st.info("가격 데이터가 없어 차트를 표시할 수 없습니다.")
        
        return
    
    def _display_technical_key_levels(self, indicators: Dict[str, Any]):
        """Display key technical levels and signals."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "현재 추세",
                "상승" if indicators.get('macd_diff', 0) > 0 else "하락",
                f"{indicators.get('macd_diff', 0):.2f}"
            )
            
        with col2:
            st.metric(
                "지지/저항선",
                f"S: {indicators.get('support_level', 0):.2f}",
                f"R: {indicators.get('resistance_level', 0):.2f}"
            )
            
        with col3:
            rsi = indicators.get('rsi', 50)
            rsi_signal = "과매수" if rsi > 70 else "과매도" if rsi < 30 else "중립"
            st.metric(
                "RSI 신호",
                rsi_signal,
                f"{rsi:.1f}"
            )