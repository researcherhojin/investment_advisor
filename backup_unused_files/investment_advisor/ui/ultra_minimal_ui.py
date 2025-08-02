"""
Ultra Minimal UI

극도로 미니멀한 디자인. Streamlit의 모든 기본 스타일을 제거하고
완전히 커스텀 CSS로 재구성.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime


class UltraMinimalUI:
    """극도로 미니멀한 UI."""
    
    def __init__(self):
        # 극도로 미니멀한 컬러 팔레트
        self.colors = {
            'bg': '#FFFFFF',
            'text': '#000000',
            'text_light': '#666666',
            'text_lighter': '#999999',
            'line': '#E5E5E5',
            'green': '#00C851',
            'red': '#FF3547',
            'accent': '#000000'
        }
    
    def setup_page(self):
        """극도로 미니멀한 페이지 설정."""
        st.markdown("""
        <style>
        /* 모든 기본 스타일 제거 */
        .stApp {
            background: #FFFFFF;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* Streamlit 기본 요소들 완전 제거 */
        #MainMenu, footer, header, .stDeployButton {display: none !important;}
        .stToolbar {display: none !important;}
        
        /* 메인 컨테이너 완전 리셋 */
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        /* 사이드바 완전 재설계 */
        section[data-testid="stSidebar"] {
            background: #FAFAFA;
            border: none;
            width: 260px !important;
            min-width: 260px !important;
        }
        
        section[data-testid="stSidebar"] > div {
            padding: 24px 20px;
        }
        
        /* 모든 텍스트 리셋 */
        * {
            color: #000000 !important;
            font-weight: 400 !important;
        }
        
        /* 헤더 스타일 */
        h1 {
            font-size: 32px !important;
            font-weight: 300 !important;
            margin: 0 0 4px 0 !important;
            letter-spacing: -0.5px !important;
        }
        
        h2 {
            font-size: 18px !important;
            font-weight: 400 !important;
            margin: 40px 0 16px 0 !important;
            letter-spacing: -0.2px !important;
        }
        
        /* 사이드바 제목 */
        .sidebar-title {
            font-size: 16px;
            font-weight: 500;
            margin: 0 0 24px 0;
            padding: 0 0 16px 0;
            border-bottom: 1px solid #E5E5E5;
        }
        
        /* 라벨 스타일 */
        .minimal-label {
            font-size: 12px;
            color: #666666 !important;
            margin: 0 0 6px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* 입력 필드 완전 재설계 */
        .stTextInput > div > div > input {
            background: #FFFFFF !important;
            border: 1px solid #E5E5E5 !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
            font-size: 14px !important;
            color: #000000 !important;
            margin: 0 !important;
        }
        
        .stTextInput > div > div > input:focus {
            border: 1px solid #000000 !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* 셀렉트박스 재설계 */
        .stSelectbox > div > div {
            border: 1px solid #E5E5E5 !important;
            border-radius: 4px !important;
            background: #FFFFFF !important;
        }
        
        /* 라디오 버튼 재설계 */
        .stRadio > div {
            gap: 8px !important;
            margin: 0 !important;
        }
        
        .stRadio > div > label {
            background: #FFFFFF !important;
            border: 1px solid #E5E5E5 !important;
            border-radius: 4px !important;
            padding: 6px 12px !important;
            margin: 0 !important;
            font-size: 13px !important;
            transition: all 0.2s ease !important;
        }
        
        .stRadio > div > label:hover {
            border-color: #000000 !important;
        }
        
        /* 버튼 완전 재설계 */
        .stButton > button {
            background: #000000 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 10px 16px !important;
            font-size: 13px !important;
            font-weight: 400 !important;
            width: 100% !important;
            margin: 8px 0 !important;
            transition: opacity 0.2s ease !important;
        }
        
        .stButton > button:hover {
            opacity: 0.8 !important;
            background: #000000 !important;
        }
        
        /* 세컨더리 버튼 */
        .stButton > button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #E5E5E5 !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: #FAFAFA !important;
            border-color: #000000 !important;
        }
        
        /* 메트릭 완전 재설계 */
        [data-testid="metric-container"] {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        
        [data-testid="metric-container"] > div {
            background: #FAFAFA !important;
            border: 1px solid #E5E5E5 !important;
            border-radius: 4px !important;
            padding: 16px !important;
        }
        
        [data-testid="metric-container"] label {
            font-size: 11px !important;
            color: #666666 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin: 0 !important;
        }
        
        [data-testid="metric-container"] > div > div {
            font-size: 18px !important;
            font-weight: 400 !important;
            color: #000000 !important;
            margin: 4px 0 0 0 !important;
        }
        
        /* 슬라이더 재설계 */
        .stSlider > div > div > div > div {
            background: #E5E5E5 !important;
        }
        
        /* 탭 재설계 */
        .stTabs [data-baseweb="tab-list"] {
            background: none !important;
            border-bottom: 1px solid #E5E5E5 !important;
            gap: 0 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: none !important;
            border: none !important;
            color: #666666 !important;
            font-size: 13px !important;
            padding: 8px 16px !important;
            margin: 0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            color: #000000 !important;
            border-bottom: 2px solid #000000 !important;
        }
        
        /* 시장 지표 그리드 */
        .market-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 12px;
            margin: 20px 0;
            padding: 20px;
            background: #FAFAFA;
            border: 1px solid #E5E5E5;
            border-radius: 4px;
        }
        
        .market-item {
            text-align: center;
            padding: 16px 8px;
            background: #FFFFFF;
            border: 1px solid #E5E5E5;
            border-radius: 4px;
        }
        
        .market-name {
            font-size: 11px;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .market-value {
            font-size: 16px;
            font-weight: 400;
            color: #000000;
            margin-bottom: 4px;
        }
        
        .market-change {
            font-size: 12px;
        }
        
        .market-change.positive { color: #00C851; }
        .market-change.negative { color: #FF3547; }
        
        /* 스피너 숨김 */
        .stSpinner {
            display: none !important;
        }
        
        /* 여백 조정 */
        .element-container {
            margin: 0 !important;
        }
        
        /* 컨테이너 패딩 */
        .main-content {
            padding: 32px 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, ticker: str, company_name: str, price: float, change: float, change_pct: float):
        """극도로 미니멀한 헤더."""
        # 심플한 헤더 - Streamlit 네이티브 컴포넌트 사용
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"# {ticker}")
            if company_name:
                st.caption(company_name)
        
        with col2:
            st.metric(
                label="현재가",
                value=f"${price:,.2f}",
                delta=f"{change:+.2f} ({change_pct:+.2f}%)"
            )
        
        with col3:
            market_open = 9 <= datetime.now().hour < 16
            status = "정규장" if market_open else "장마감"
            st.metric(
                label="거래 상태",
                value=status
            )
        
        # 구분선
        st.divider()
    
    def render_market_indices(self, indices: Dict[str, Any]):
        """극도로 미니멀한 시장 지표."""
        # Streamlit 네이티브 컬럼 사용
        cols = st.columns(len(indices))
        
        for idx, (name, data) in enumerate(indices.items()):
            with cols[idx]:
                current = data.get('current', 0)
                change = data.get('change', 0)
                
                if name == "VIX":
                    # VIX 특별 처리
                    fear_level = data.get('fear_level', '')
                    if current < 20:
                        st.success(f"**{name}**\n\n{current:.2f}\n\n{fear_level.split(' ')[0] if fear_level else ''}")
                    elif current < 30:
                        st.warning(f"**{name}**\n\n{current:.2f}\n\n{fear_level.split(' ')[0] if fear_level else ''}")
                    else:
                        st.error(f"**{name}**\n\n{current:.2f}\n\n{fear_level.split(' ')[0] if fear_level else ''}")
                else:
                    # 일반 지수
                    st.metric(
                        label=name,
                        value=f"{current:,.2f}",
                        delta=f"{change:+.2f}%"
                    )
    
    def render_key_metrics(self, metrics: Dict[str, Any]):
        """극도로 미니멀한 주요 지표."""
        st.markdown("## 주요 지표")
        
        # 2행 4열 레이아웃
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        st.write("")  # 간격 추가
        
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
        """극도로 미니멀한 가격 차트."""
        st.markdown("## 가격 차트")
        
        fig = go.Figure()
        
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
        
        fig.update_layout(
            template="plotly_white",
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                gridcolor='#F5F5F5',
                showgrid=True,
                zeroline=False,
                showline=True,
                linecolor='#E5E5E5'
            ),
            yaxis=dict(
                gridcolor='#F5F5F5',
                showgrid=True,
                zeroline=False,
                showline=True,
                linecolor='#E5E5E5',
                side='right'
            ),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font=dict(family="system-ui", size=11, color='#666666'),
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analysis_results(self, agent_results: Dict[str, str]):
        """극도로 미니멀한 AI 분석 결과."""
        st.markdown("## AI 분석")
        
        tabs = st.tabs(list(agent_results.keys()))
        
        for tab, (agent_name, result) in zip(tabs, agent_results.items()):
            with tab:
                # Streamlit 네이티브 컨테이너 사용
                with st.container():
                    st.info(result)
    
    def render_decision(self, decision: str):
        """극도로 미니멀한 투자 의견."""
        if "매수" in decision or "BUY" in decision:
            st.success(f"## 🟢 {decision}")
        elif "매도" in decision or "SELL" in decision:
            st.error(f"## 🔴 {decision}")
        else:
            st.warning(f"## 🟡 {decision}")
    
    def render_sidebar(self) -> Dict[str, Any]:
        """극도로 미니멀한 사이드바."""
        with st.sidebar:
            st.header("📈 AI 주식분석")
            
            st.subheader("시장")
            market = st.radio(
                "Market",
                options=["US", "KR"],
                format_func=lambda x: "미국" if x == "US" else "한국",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.subheader("종목코드")
            ticker = st.text_input(
                "Symbol",
                placeholder="AAPL",
                label_visibility="collapsed"
            ).upper().strip()
            
            st.subheader("산업")
            industries = ["기술", "의료", "금융", "소비재", "에너지"] if market == "US" else ["전자/IT", "바이오", "금융", "소비재", "에너지"]
            industry = st.selectbox(
                "Industry",
                options=industries,
                label_visibility="collapsed"
            )
            
            st.subheader("기간")
            period = st.select_slider(
                "Period",
                options=[3, 6, 12, 24],
                value=12,
                format_func=lambda x: f"{x}개월",
                label_visibility="collapsed"
            )
            
            st.write("")  # 간격
            
            analyze = st.button("분석", type="primary", use_container_width=True)
            clear = st.button("초기화", type="secondary", use_container_width=True)
            
            with st.expander("설정"):
                include_recs = st.checkbox("추천 포함", value=True)
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
        """극도로 미니멀한 환영 화면."""
        # 중앙 정렬된 제목
        st.markdown("# AI 주식 분석")
        st.markdown("### 인공지능 기반 주식 분석 플랫폼")
        
        st.write("")
        st.write("")
        
        # 기능 카드들
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**실시간 데이터**\n\n정확한 시장 정보")
        
        with col2:
            st.info("**AI 분석**\n\n6개 전문 에이전트")
        
        with col3:
            st.info("**투자 인사이트**\n\n데이터 기반 추천")
        
        st.write("")
        st.write("")
        
        # 안내 메시지
        st.info("💡 시장과 종목을 선택하여 분석을 시작하세요")
    
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