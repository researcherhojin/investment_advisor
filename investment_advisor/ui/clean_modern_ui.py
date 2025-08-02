"""
Clean Modern UI

자연스럽고 직관적인 현대적 디자인.
AI 느낌 없이 전문적이고 깔끔한 금융 앱 느낌.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import shared configuration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared_config import shared_config, get_market_mapping, get_agent_colors


class CleanModernUI:
    """깔끔하고 현대적인 UI."""
    
    def __init__(self):
        # Use colors from shared config
        self.colors = {
            'primary': shared_config.theme_colors.get('dark', '#1f2937'),
            'secondary': shared_config.theme_colors.get('secondary', '#6b7280'),
            'light': shared_config.theme_colors.get('light', '#f9fafb'),
            'border': '#e5e7eb',
            'success': shared_config.theme_colors.get('success', '#059669'),
            'danger': shared_config.theme_colors.get('danger', '#dc2626'),
            'warning': shared_config.theme_colors.get('warning', '#d97706'),
            'info': shared_config.theme_colors.get('primary', '#2563eb')
        }
        
        # Load market mapping from shared config
        self.market_mapping = get_market_mapping()
        
        # Load agent colors from shared config
        self.agent_colors = get_agent_colors()
    
    def setup_page(self):
        """페이지 설정 - 전문적인 금융 터미널 스타일."""
        st.markdown("""
        <style>
        /* 전체 앱 스타일링 - 깔끔한 흰색 배경 */
        .stApp {
            background-color: #fafafa;
        }
        
        /* 메인 컨텐츠 영역 */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            background: #ffffff;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin: 1rem;
            max-width: 1200px;
        }
        
        /* 사이드바 개선 */
        section[data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
            width: 280px !important;
        }
        
        section[data-testid="stSidebar"] > div {
            padding: 1.5rem 1.25rem;
        }
        
        /* 버튼 스타일 개선 - 전문적이고 절제된 디자인 */
        .stButton > button[kind="primary"] {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            font-size: 14px;
            width: 100%;
            transition: background-color 0.15s ease;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: #1d4ed8;
        }
        
        .stButton > button[kind="secondary"] {
            background: white;
            color: #374151;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            font-size: 14px;
            width: 100%;
            transition: all 0.2s ease;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: #f9fafb;
            border-color: #9ca3af;
        }
        
        /* 메트릭 카드 개선 - 전문적인 금융 스타일 */
        [data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 1rem;
            box-shadow: none;
            transition: border-color 0.15s ease;
        }
        
        [data-testid="metric-container"]:hover {
            border-color: #d1d5db;
        }
        
        /* 입력 필드 개선 */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            padding: 0.75rem;
            font-size: 14px;
            transition: border-color 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* 셀렉트박스 개선 */
        .stSelectbox > div > div {
            border-radius: 8px;
            border: 1px solid #d1d5db;
        }
        
        /* 라디오 버튼 개선 */
        .stRadio > div {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.75rem;
        }
        
        /* 헤더 개선 */
        h1 {
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            font-weight: 600;
            color: #374151;
            margin: 1.5rem 0 1rem 0;
        }
        
        h3 {
            font-weight: 600;
            color: #4b5563;
            margin: 1rem 0 0.5rem 0;
        }
        
        /* 성공/경고/에러 메시지 개선 */
        .stSuccess, .stWarning, .stError, .stInfo {
            border-radius: 8px;
            border: none;
            font-weight: 500;
        }
        
        /* 탭 개선 */
        .stTabs [data-baseweb="tab-list"] {
            background: white;
            border-bottom: 2px solid #f3f4f6;
            border-radius: 8px 8px 0 0;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #6b7280;
            font-weight: 500;
            padding: 0.75rem 1.5rem;
        }
        
        .stTabs [aria-selected="true"] {
            color: #1f2937;
            border-bottom-color: #3b82f6;
        }
        
        /* 컨테이너 개선 */
        .main .block-container {
            padding: 2rem 2.5rem;
            max-width: 1200px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, company_name: str, price: float, change: float, change_pct: float):
        """깔끔한 헤더."""
        st.markdown(f"# {ticker}")
        if company_name:
            st.caption(f"📊 {company_name}")
        
        # 가격 정보
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.metric(
                label="💰 현재가",
                value=f"${price:,.2f}",
                delta=f"{change:+.2f} ({change_pct:+.2f}%)"
            )
        
        with col2:
            market_open = 9 <= datetime.now().hour < 16
            status = "🟢 정규장" if market_open else "🔴 장마감"
            st.metric(label="⏰ 거래 상태", value=status)
        
        with col3:
            st.metric(label="📅 업데이트", value=datetime.now().strftime("%H:%M"))
        
        st.divider()
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """시장 지표."""
        st.markdown("## 📊 글로벌 시장 현황")
        
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                
                if name == "VIX":
                    # VIX 공포지수
                    fear_level = data.get('fear_level', '')
                    if current < 20:
                        st.success(f"**{name} 📈**\n\n{current:.2f}\n\n😌 안정")
                    elif current < 30:
                        st.warning(f"**{name} ⚠️**\n\n{current:.2f}\n\n😐 보통")
                    else:
                        st.error(f"**{name} 📉**\n\n{current:.2f}\n\n😰 공포")
                else:
                    # 일반 지수
                    emoji = "📈" if change >= 0 else "📉"
                    st.metric(
                        label=f"{emoji} {name}",
                        value=f"{current:,.2f}",
                        delta=f"{change:+.2f}%"
                    )
    
    def render_key_metrics(self, metrics: Dict[str, Any]):
        """주요 지표."""
        st.markdown("## 📋 주요 재무 지표")
        
        # 첫 번째 줄
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            value = metrics.get('marketCap', 0)
            st.metric("🏢 시가총액", self._format_market_cap(value))
        
        with col2:
            per = metrics.get('PER')
            st.metric("📊 PER", f"{per:.2f}" if per and per != 'N/A' else "—")
        
        with col3:
            pbr = metrics.get('PBR')
            st.metric("📈 PBR", f"{pbr:.2f}" if pbr and pbr != 'N/A' else "—")
        
        with col4:
            div_yield = metrics.get('dividendYield')
            st.metric("💰 배당수익률", f"{div_yield:.2f}%" if div_yield else "—")
        
        st.write("")
        
        # 두 번째 줄
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_52 = metrics.get('52주최고', 0)
            st.metric("⬆️ 52주 최고", f"${high_52:,.2f}" if high_52 else "—")
        
        with col2:
            low_52 = metrics.get('52주최저', 0)
            st.metric("⬇️ 52주 최저", f"${low_52:,.2f}" if low_52 else "—")
        
        with col3:
            beta = metrics.get('beta')
            st.metric("📊 베타", f"{beta:.2f}" if beta else "—")
        
        with col4:
            volume = metrics.get('volume', 0)
            st.metric("📦 거래량", self._format_volume(volume))
    
    def render_technical_analysis_charts(self, df: pd.DataFrame, ticker: str):
        """전문적인 기술적 분석 차트 세트."""
        st.markdown("### Technical Analysis")
        
        # 기술적 지표 계산
        technical_data = self._calculate_technical_indicators(df)
        
        # 탭으로 구성
        tab1, tab2, tab3, tab4 = st.tabs(["Price & Volume", "Moving Averages", "RSI & MACD", "Bollinger Bands"])
        
        with tab1:
            self._render_price_volume_chart(df, technical_data, ticker)
        
        with tab2:
            self._render_moving_averages_chart(df, technical_data, ticker)
        
        with tab3:
            self._render_oscillators_chart(df, technical_data, ticker)
        
        with tab4:
            self._render_bollinger_bands_chart(df, technical_data, ticker)
    
    def _calculate_technical_indicators(self, df):
        """기술적 지표 계산."""
        import numpy as np
        
        # 이동평균
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # 지수이동평균
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 볼린저 밴드
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # 거래량 이동평균
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        
        return df
    
    def _render_price_volume_chart(self, df, technical_data, ticker):
        """가격과 거래량 차트."""
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('Price', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # 캔들스틱 차트
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#00C851',
                decreasing_line_color='#FF4444',
                increasing_fillcolor='#00C851',
                decreasing_fillcolor='#FF4444'
            ), row=1, col=1
        )
        
        # 거래량 바 차트
        colors = ['#00C851' if close >= open else '#FF4444' 
                 for close, open in zip(df['Close'], df['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ), row=2, col=1
        )
        
        # 거래량 이동평균
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Volume_SMA'],
                name='Volume MA(20)',
                line=dict(color='#FF8800', width=2),
                opacity=0.8
            ), row=2, col=1
        )
        
        fig.update_layout(
            template="plotly_white",
            height=600,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(family="system-ui", size=11)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 전문적인 해설
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        volume_ratio = df['Volume'].iloc[-1] / df['Volume_SMA'].iloc[-1]
        
        st.markdown("""
        **📊 Price & Volume Analysis:**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            trend = "상승" if current_price > prev_price else "하락"
            st.markdown(f"• **Price Movement**: {trend} (${current_price:.2f})")
            st.markdown(f"• **Daily Change**: {((current_price - prev_price) / prev_price * 100):+.2f}%")
        
        with col2:
            volume_analysis = "높음" if volume_ratio > 1.2 else "보통" if volume_ratio > 0.8 else "낮음"
            st.markdown(f"• **Volume**: {volume_analysis} (비율: {volume_ratio:.1f}x)")
            st.markdown(f"• **Volume Trend**: {'상승' if df['Volume'].iloc[-1] > df['Volume'].iloc[-5:].mean() else '하락'}")
    
    def _render_moving_averages_chart(self, df, technical_data, ticker):
        """이동평균 차트."""
        fig = go.Figure()
        
        # 가격
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            name='Close Price',
            line=dict(color='#333333', width=2)
        ))
        
        # 이동평균선들
        ma_lines = [
            ('SMA_20', '#FF6B6B', '20-day SMA'),
            ('SMA_50', '#4ECDC4', '50-day SMA'),
            ('SMA_200', '#45B7D1', '200-day SMA')
        ]
        
        for ma, color, name in ma_lines:
            if ma in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[ma],
                    name=name,
                    line=dict(color=color, width=2)
                ))
        
        fig.update_layout(
            template="plotly_white",
            height=500,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(x=0, y=1),
            font=dict(family="system-ui", size=11)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 이동평균 분석
        current_price = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1] if not pd.isna(df['SMA_20'].iloc[-1]) else None
        sma_50 = df['SMA_50'].iloc[-1] if not pd.isna(df['SMA_50'].iloc[-1]) else None
        sma_200 = df['SMA_200'].iloc[-1] if not pd.isna(df['SMA_200'].iloc[-1]) else None
        
        st.markdown("**📈 Moving Average Analysis:**")
        
        col1, col2 = st.columns(2)
        with col1:
            if sma_20:
                trend_20 = "상승" if current_price > sma_20 else "하락"
                st.markdown(f"• **vs 20-day SMA**: 가격이 이동평균 {trend_20}")
            if sma_50:
                trend_50 = "상승" if current_price > sma_50 else "하락"  
                st.markdown(f"• **vs 50-day SMA**: 가격이 이동평균 {trend_50}")
        
        with col2:
            if sma_200:
                trend_200 = "상승" if current_price > sma_200 else "하락"
                st.markdown(f"• **vs 200-day SMA**: 가격이 이동평균 {trend_200}")
            
            # 골든 크로스/데드 크로스 확인
            if sma_20 and sma_50:
                if sma_20 > sma_50:
                    st.markdown("• **Signal**: 단기 상승 모멘텀 (Golden Cross 가능성)")
                else:
                    st.markdown("• **Signal**: 단기 하락 모멘텀 (Dead Cross 가능성)")
    
    def _render_oscillators_chart(self, df, technical_data, ticker):
        """RSI와 MACD 차트."""
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price', 'RSI', 'MACD'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # 가격 차트
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='#333333')),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9C27B0')),
            row=2, col=1
        )
        
        # RSI 과매수/과매도 라인
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#2196F3')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='#FF9800')),
            row=3, col=1
        )
        
        # MACD 히스토그램
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
        fig.add_trace(
            go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram', 
                  marker_color=colors, opacity=0.6),
            row=3, col=1
        )
        
        fig.update_layout(
            template="plotly_white",
            height=700,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(family="system-ui", size=11)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 기술적 분석 해설
        current_rsi = df['RSI'].iloc[-1]
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_Signal'].iloc[-1]
        
        st.markdown("**🔄 Momentum Analysis:**")
        
        col1, col2 = st.columns(2)
        with col1:
            # RSI 분석
            if current_rsi > 70:
                rsi_status = "과매수 구간 (매도 고려)"
                rsi_color = "🔴"
            elif current_rsi < 30:
                rsi_status = "과매도 구간 (매수 고려)"
                rsi_color = "🟢"
            else:
                rsi_status = "중립 구간"
                rsi_color = "🟡"
            
            st.markdown(f"• **RSI ({current_rsi:.1f})**: {rsi_color} {rsi_status}")
        
        with col2:
            # MACD 분석
            if current_macd > current_signal:
                macd_status = "상승 모멘텀"
                macd_color = "🟢"
            else:
                macd_status = "하락 모멘텀"
                macd_color = "🔴"
            
            st.markdown(f"• **MACD**: {macd_color} {macd_status}")
    
    def _render_bollinger_bands_chart(self, df, technical_data, ticker):
        """볼린저 밴드 차트."""
        fig = go.Figure()
        
        # 볼린저 밴드 영역
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Upper'],
            name='Upper Band',
            line=dict(color='rgba(255,0,0,0)'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Lower'],
            name='Lower Band',
            fill='tonexty',
            fillcolor='rgba(68,138,255,0.1)',
            line=dict(color='rgba(255,0,0,0)'),
            showlegend=False
        ))
        
        # 중간선 (20일 이동평균)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Middle'],
            name='Middle Band (SMA 20)',
            line=dict(color='#448AFF', width=2, dash='dash')
        ))
        
        # 상단/하단 밴드
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Upper'],
            name='Upper Band (+2σ)',
            line=dict(color='#FF4444', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Lower'],
            name='Lower Band (-2σ)',
            line=dict(color='#FF4444', width=1)
        ))
        
        # 종가
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            name='Close Price',
            line=dict(color='#333333', width=2)
        ))
        
        fig.update_layout(
            template="plotly_white",
            height=500,
            legend=dict(x=0, y=1),
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(family="system-ui", size=11)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 볼린저 밴드 분석
        current_price = df['Close'].iloc[-1]
        upper_band = df['BB_Upper'].iloc[-1]
        lower_band = df['BB_Lower'].iloc[-1]
        middle_band = df['BB_Middle'].iloc[-1]
        
        # 밴드 위치 분석
        bb_position = (current_price - lower_band) / (upper_band - lower_band)
        
        st.markdown("**📊 Bollinger Bands Analysis:**")
        
        col1, col2 = st.columns(2)
        with col1:
            if bb_position > 0.8:
                position_status = "상단 밴드 근처 (과매수 가능성)"
                position_color = "🔴"
            elif bb_position < 0.2:
                position_status = "하단 밴드 근처 (과매도 가능성)"
                position_color = "🟢"
            else:
                position_status = "밴드 중앙 구간 (정상 범위)"
                position_color = "🟡"
            
            st.markdown(f"• **Band Position**: {position_color} {position_status}")
            st.markdown(f"• **Price vs Middle**: {'상회' if current_price > middle_band else '하회'}")
        
        with col2:
            # 밴드 폭 분석
            band_width = (upper_band - lower_band) / middle_band * 100
            volatility = "높음" if band_width > 10 else "보통" if band_width > 5 else "낮음"
            
            st.markdown(f"• **Volatility**: {volatility} (밴드폭 {band_width:.1f}%)")
            
            # 스퀴즈 상황 체크
            if band_width < 5:
                st.markdown("• **Signal**: 볼린저 밴드 스퀴즈 (변동성 확대 대기)")
    
    def render_price_chart(self, df: pd.DataFrame, ticker: str):
        """기존 가격 차트는 새로운 기술적 분석 차트로 대체."""
        self.render_technical_analysis_charts(df, ticker)
    
    def render_analysis_results(self, agent_results: Dict[str, str], price_history: pd.DataFrame = None, ticker: str = ""):
        """AI 분석 결과 - 전문적이고 시각적으로 개선된 리포트."""
        # 리포트 헤더
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
        ">
            <h2 style="margin: 0; font-weight: 700;">🤖 AI 전문가 분석 리포트</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">5개 전문 분야 AI 에이전트가 종합 분석한 결과입니다</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not agent_results:
            st.error("⚠️ 분석 결과를 불러올 수 없습니다. 다시 시도해주세요.")
            return
        
        # 분석 완료 개수 표시
        completed_analyses = sum(1 for result in agent_results.values() if result and result.strip())
        total_analyses = len(agent_results)
        
        progress_percent = (completed_analyses / total_analyses) * 100
        st.progress(progress_percent / 100)
        st.markdown(f"**분석 완료: {completed_analyses}/{total_analyses}개 전문가** ({progress_percent:.0f}%)")
        
        st.write("")
        
        # 전문적인 탭 제목과 아이콘
        tab_mapping = {
            "기업분석가": "🏢 기업분석",
            "산업전문가": "🏭 산업분석", 
            "거시경제전문가": "🌍 거시경제",
            "기술분석가": "📈 기술분석",
            "리스크관리자": "⚠️ 위험분석"
        }
        
        # 분석가별 색상 테마
        agent_colors = {
            "기업분석가": "#059669",
            "산업전문가": "#7c3aed", 
            "거시경제전문가": "#dc2626",
            "기술분석가": "#ea580c",
            "리스크관리자": "#1d4ed8"
        }
        
        # 탭 생성
        tab_names = [tab_mapping.get(name, f"📊 {name}") for name in agent_results.keys()]
        tabs = st.tabs(tab_names)
        
        for tab, (agent_name, result) in zip(tabs, agent_results.items()):
            with tab:
                agent_color = agent_colors.get(agent_name, "#6b7280")
                
                # 전문가 헤더
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {agent_color}15 0%, {agent_color}05 100%);
                    border-left: 4px solid {agent_color};
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                ">
                    <h3 style="margin: 0; color: {agent_color};">{tab_mapping.get(agent_name, agent_name)}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.9rem;">전문 분야별 심층 분석 결과</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 기술분석가 탭인 경우 가격 차트도 함께 표시
                if agent_name == "기술분석가" and price_history is not None and not price_history.empty:
                    st.markdown("#### 📊 가격 차트 및 기술적 지표")
                    self.render_price_chart(price_history, ticker)
                    st.markdown("---")
                
                if result and result.strip():
                    # 분석 결과를 더 읽기 쉽게 포맷팅
                    st.markdown("#### 📋 분석 내용")
                    
                    # 결과를 카드 형태로 표시
                    st.markdown(f"""
                    <div style="
                        background: white;
                        border: 1px solid #e5e7eb;
                        border-radius: 12px;
                        padding: 1.5rem;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        line-height: 1.7;
                    ">
                        {result.replace('\\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 분석 신뢰도 표시
                    confidence = "높음" if len(result) > 200 else "보통" if len(result) > 100 else "낮음"
                    confidence_color = "#16a34a" if confidence == "높음" else "#ea580c" if confidence == "보통" else "#dc2626"
                    
                    st.markdown(f"""
                    <div style="margin-top: 1rem; text-align: right;">
                        <span style="
                            background: {confidence_color}15;
                            color: {confidence_color};
                            padding: 0.25rem 0.75rem;
                            border-radius: 12px;
                            font-size: 0.85rem;
                            font-weight: 500;
                        ">
                            🎯 분석 신뢰도: {confidence}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    # 분석 실패 시 안내
                    st.markdown(f"""
                    <div style="
                        background: #fef2f2;
                        border: 1px solid #fecaca;
                        border-radius: 12px;
                        padding: 1.5rem;
                        text-align: center;
                    ">
                        <h4 style="color: #dc2626; margin: 0 0 0.5rem 0;">❌ 분석 데이터 부족</h4>
                        <p style="color: #7f1d1d; margin: 0;">{agent_name} 분석을 완료하지 못했습니다.<br>
                        데이터 부족 또는 네트워크 오류가 원인일 수 있습니다.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
    
    def render_decision(self, decision: str):
        """투자 의견 - 전문적이고 시각적으로 매력적인 디자인."""
        st.markdown("## 🎯 최종 투자 의견")
        
        # 투자 의견 파싱
        if "매수" in decision or "BUY" in decision.upper():
            recommendation = "매수"
            color = "#16a34a"  # 녹색
            icon = "📈"
            bg_color = "#dcfce7"
            badge_color = "#15803d"
        elif "매도" in decision or "SELL" in decision.upper():
            recommendation = "매도"
            color = "#dc2626"  # 빨간색
            icon = "📉"
            bg_color = "#fef2f2"
            badge_color = "#b91c1c"
        else:
            recommendation = "보유"
            color = "#ea580c"  # 주황색
            icon = "⚖️"
            bg_color = "#fff7ed"
            badge_color = "#c2410c"
        
        # 전문적인 투자 의견 카드
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {bg_color} 0%, #ffffff 100%);
            border: 2px solid {color};
            border-radius: 16px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="
                    background: {badge_color};
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 1.1rem;
                    margin-right: 1rem;
                ">
                    {icon} {recommendation.upper()}
                </div>
                <div style="
                    color: {color};
                    font-size: 1.2rem;
                    font-weight: 600;
                ">
                    투자 추천 등급
                </div>
            </div>
            <div style="
                color: #374151;
                font-size: 1rem;
                line-height: 1.6;
                background: rgba(255,255,255,0.8);
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid {color};
            ">
                {decision}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 투자 지표 요약
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if recommendation == "매수":
                st.metric("📊 투자 신호", "긍정적", delta="상승 추세")
            elif recommendation == "매도":
                st.metric("📊 투자 신호", "부정적", delta="하락 우려")
            else:
                st.metric("📊 투자 신호", "중립", delta="관망 필요")
        
        with col2:
            confidence_level = "높음" if len(decision) > 100 else "보통"
            st.metric("🎯 신뢰도", confidence_level, delta="AI 분석 기반")
        
        with col3:
            time_horizon = "중장기" if "장기" in decision else "단기"
            st.metric("⏰ 투자 기간", time_horizon, delta="권장 보유 기간")
        
        # 추가 조언
        st.markdown("### 💡 투자 시 고려사항")
        
        if recommendation == "매수":
            st.info("""
            **✅ 매수 시 참고사항:**
            - 분할 매수를 통한 리스크 분산을 고려하세요
            - 시장 상황과 개인 투자 목표를 종합적으로 판단하세요
            - 정기적인 포트폴리오 리밸런싱을 권장합니다
            """)
        elif recommendation == "매도":
            st.warning("""
            **⚠️ 매도 시 참고사항:**
            - 세금 효율성을 고려한 매도 시점을 선택하세요
            - 다른 투자 기회와 비교 검토하세요
            - 부분 매도를 통한 점진적 포지션 조정을 고려하세요
            """)
        else:
            st.info("""
            **📋 보유 시 참고사항:**
            - 정기적인 재평가를 통해 투자 논리를 점검하세요
            - 시장 변화에 따른 전략 조정을 준비하세요
            - 다양한 정보원을 통해 지속적으로 모니터링하세요
            """)
        
        # 추가 분석 링크 (절제된 방식)
        if recommendation == "매수":
            st.info("💡 Consider portfolio diversification and risk management strategies.")
    
    def render_sidebar(self) -> Dict[str, Any]:
        """사이드바."""
        with st.sidebar:
            # 간단한 제목
            st.markdown("# Analysis Tools")
            st.markdown("##### 전문 주식 분석 서비스")
            st.markdown("---")
            
            # 시장 선택
            st.markdown("### 🌍 시장 선택")
            market = st.radio(
                "시장",
                options=["US", "KR"],
                format_func=lambda x: "🇺🇸 미국 시장" if x == "US" else "🇰🇷 한국 시장",
                horizontal=False,
                label_visibility="collapsed"
            )
            
            # 종목 입력
            st.markdown("### 🔤 종목 코드")
            ticker = st.text_input(
                "종목 코드",
                placeholder="예: AAPL, MSFT",
                help="분석하고 싶은 종목의 티커를 입력하세요",
                label_visibility="collapsed"
            ).upper().strip()
            
            # 산업 선택
            st.markdown("### 🏭 산업 분류")
            industries = [
                "기술", "의료", "금융", "소비재", "에너지", "통신", "산업재", "유틸리티"
            ] if market == "US" else [
                "전자/IT", "바이오", "금융", "소비재", "에너지", "통신", "산업재", "건설"
            ]
            
            industry = st.selectbox(
                "산업",
                options=industries,
                label_visibility="collapsed"
            )
            
            # 분석 기간
            st.markdown("### 📅 분석 기간")
            period = st.select_slider(
                "기간",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}개월",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # 분석 버튼 (더 눈에 띄게)
            st.markdown("### 🚀 분석 시작")
            
            # 입력 검증
            can_analyze = bool(ticker) and market and industry
            
            if not can_analyze:
                st.warning("⚠️ 종목 코드를 입력해주세요")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                analyze = st.button(
                    "📊 종합 분석 시작",
                    type="primary",
                    use_container_width=True,
                    help="AI가 선택한 종목을 종합적으로 분석합니다",
                    disabled=not can_analyze
                )
            
            with col2:
                clear = st.button(
                    "🗑️",
                    type="secondary",
                    help="입력 초기화"
                )
            
            # 고급 설정
            with st.expander("⚙️ 고급 설정"):
                include_recs = st.checkbox("📈 연관 종목 추천", value=True)
                use_cache = st.checkbox("⚡ 빠른 캐시 로딩", value=True)
                detailed_analysis = st.checkbox("🔍 상세 분석 모드", value=False)
            
            # 도움말
            st.markdown("---")
            st.markdown("#### 💡 사용 팁")
            st.info("""
            **빠른 시작:**
            1. 시장 선택 (미국/한국)
            2. 종목 코드 입력
            3. 분석 시작 버튼 클릭
            
            **인기 종목:**
            - 🇺🇸 AAPL, MSFT, GOOGL
            - 🇰🇷 005930, 000660
            """)
            
            # 시장 이름 정규화
            market_mapping = {
                "US": "미국장",
                "KR": "한국장"
            }
            
            return {
                'ticker': ticker,
                'market': market_mapping.get(market, market + "장"),
                'industry': industry,
                'period': period,
                'actions': {
                    'analyze': analyze,
                    'clear': clear
                },
                'advanced': {
                    'include_recommendations': include_recs,
                    'use_cache': use_cache,
                    'detailed_analysis': detailed_analysis
                }
            }
    
    def render_welcome(self):
        """환영 화면 - 전문적인 금융 분석 플랫폼 스타일."""
        
        # 간단하고 전문적인 헤더
        st.markdown("""
        <div style="
            padding: 2rem 0 1rem 0;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 2rem;
        ">
            <h1 style="
                font-size: 2.25rem; 
                font-weight: 600; 
                color: #111827; 
                margin: 0 0 0.5rem 0;
                letter-spacing: -0.025em;
            ">
                Investment Analysis Platform
            </h1>
            <p style="
                font-size: 1.125rem; 
                color: #6b7280; 
                margin: 0;
                font-weight: 400;
            ">
                Professional stock analysis powered by advanced algorithms
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 간단한 사용법 안내
        st.markdown("### Quick Start")
        
        st.markdown("""
        <div style="
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 1.5rem;
            margin: 1rem 0;
        ">
            <div style="
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 2rem;
                text-align: center;
            ">
                <div>
                    <div style="
                        background: #2563eb;
                        color: white;
                        width: 2rem;
                        height: 2rem;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 0.75rem auto;
                        font-weight: 600;
                        font-size: 0.875rem;
                    ">1</div>
                    <h4 style="color: #374151; margin-bottom: 0.5rem; font-size: 1rem;">Select Market</h4>
                    <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">US or Korean markets</p>
                </div>
                <div>
                    <div style="
                        background: #2563eb;
                        color: white;
                        width: 2rem;
                        height: 2rem;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 0.75rem auto;
                        font-weight: 600;
                        font-size: 0.875rem;
                    ">2</div>
                    <h4 style="color: #374151; margin-bottom: 0.5rem; font-size: 1rem;">Enter Symbol</h4>
                    <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Stock ticker or code</p>
                </div>
                <div>
                    <div style="
                        background: #2563eb;
                        color: white;
                        width: 2rem;
                        height: 2rem;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 0.75rem auto;
                        font-weight: 600;
                        font-size: 0.875rem;
                    ">3</div>
                    <h4 style="color: #374151; margin-bottom: 0.5rem; font-size: 1rem;">Run Analysis</h4>
                    <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Get comprehensive report</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        # 마켓 오버뷰
        st.markdown("### Market Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 1.25rem;
                margin-bottom: 1rem;
            ">
                <h4 style="color: #374151; margin-bottom: 1rem; font-size: 1.125rem; font-weight: 600;">US Equities</h4>
                <div style="display: grid; gap: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">AAPL</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">Apple Inc.</span>
                        </div>
                        <span style="color: #059669; font-size: 0.875rem;">+1.2%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">MSFT</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">Microsoft</span>
                        </div>
                        <span style="color: #059669; font-size: 0.875rem;">+0.8%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">NVDA</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">NVIDIA</span>
                        </div>
                        <span style="color: #dc2626; font-size: 0.875rem;">-2.1%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">TSLA</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">Tesla</span>
                        </div>
                        <span style="color: #059669; font-size: 0.875rem;">+3.4%</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 1.25rem;
                margin-bottom: 1rem;
            ">
                <h4 style="color: #374151; margin-bottom: 1rem; font-size: 1.125rem; font-weight: 600;">Korean Equities</h4>
                <div style="display: grid; gap: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">005930</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">삼성전자</span>
                        </div>
                        <span style="color: #059669; font-size: 0.875rem;">+0.5%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">000660</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">SK하이닉스</span>
                        </div>
                        <span style="color: #dc2626; font-size: 0.875rem;">-1.3%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">207940</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">삼성바이오</span>
                        </div>
                        <span style="color: #059669; font-size: 0.875rem;">+2.1%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
                        <div>
                            <span style="font-weight: 500; color: #111827;">051910</span>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">LG화학</span>
                        </div>
                        <span style="color: #6b7280; font-size: 0.875rem;">0.0%</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        
        # 간단한 주요 지수 정보
        st.markdown("### Market Indices")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("S&P 500", "4,567.23", "+12.45 (0.27%)")
        
        with col2:
            st.metric("NASDAQ", "14,321.90", "-23.67 (-0.16%)")
        
        with col3:
            st.metric("KOSPI", "2,593.47", "+5.23 (0.20%)")
        
        with col4:
            st.metric("VIX", "14.88", "-0.32")
    
    def _format_market_cap(self, value: float) -> str:
        """시가총액 포맷."""
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
        """거래량 포맷."""
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