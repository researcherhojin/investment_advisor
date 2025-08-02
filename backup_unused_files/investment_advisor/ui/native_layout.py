"""
Native Streamlit Layout Manager

Uses only native Streamlit components for maximum compatibility.
Clean, professional design without custom HTML/CSS.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


class NativeLayoutManager:
    """Native Streamlit layout manager - no HTML/CSS."""
    
    def __init__(self):
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure Streamlit page."""
        pass  # Page config already set in main.py
    
    def setup_page(self):
        """Setup page styling with minimal custom CSS."""
        st.markdown("""
        <style>
        /* Minimal styling for better appearance */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        
        /* Better sidebar */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Render application header."""
        st.title("🤖 AI 투자 분석")
        st.caption("데이터 기반 지능형 주식 분석 플랫폼")
        st.divider()
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render sidebar with native components."""
        with st.sidebar:
            st.header("📊 분석 설정")
            
            # Market selection
            market = st.selectbox(
                "🌍 시장 선택",
                options=["미국장", "한국장"],
                index=0,
                help="분석할 주식 시장을 선택하세요"
            )
            
            # Ticker input
            ticker = st.text_input(
                "📈 종목 코드",
                placeholder="예: AAPL, TSLA, 005930",
                help="분석하고 싶은 종목의 코드를 입력하세요"
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
            
            industry = st.selectbox(
                "🏭 산업 분야", 
                options=industries,
                help="종목이 속한 산업 분야를 선택하세요"
            )
            
            # Analysis period
            period = st.selectbox(
                "📅 분석 기간",
                options=[1, 3, 6, 12, 24],
                index=3,
                format_func=lambda x: f"{x}개월",
                help="분석할 기간을 선택하세요"
            )
            
            st.divider()
            
            # Action buttons
            analyze_button = st.button(
                "🔍 분석 시작", 
                type="primary", 
                use_container_width=True,
                help="선택한 설정으로 AI 분석을 시작합니다"
            )
            
            clear_button = False
            if st.session_state.get('analysis_results'):
                clear_button = st.button(
                    "🗑️ 결과 지우기", 
                    use_container_width=True,
                    help="현재 분석 결과를 지웁니다"
                )
            
            # Advanced options
            with st.expander("⚙️ 고급 설정"):
                include_recommendations = st.checkbox(
                    "추천 종목 포함", 
                    value=True,
                    help="분석 결과에 추천 종목을 포함합니다"
                )
                show_detailed_analysis = st.checkbox(
                    "상세 분석 표시", 
                    value=True,
                    help="전문가 분석의 상세 내용을 표시합니다"
                )
                export_results = st.checkbox(
                    "결과 내보내기", 
                    value=False,
                    help="분석 결과를 파일로 내보낼 수 있습니다"
                )
        
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
        st.markdown("### 🚀 분석할 준비가 완료되었습니다")
        st.info("👈 왼쪽 사이드바에 종목 코드를 입력하고 **분석 시작** 버튼을 클릭하세요")
        
        # Feature highlights
        st.markdown("#### ✨ 주요 기능")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 AI 전문가 분석**
            - 기업분석가
            - 산업전문가  
            - 거시경제전문가
            - 기술분석가
            - 리스크관리자
            - 종합판단
            """)
        
        with col2:
            st.markdown("""
            **🌐 글로벌 시장 지원**
            - 미국 주식 (NYSE, NASDAQ)
            - 한국 주식 (KRX, KOSDAQ)
            - 실시간 데이터 연동
            - 다양한 분석 기간
            """)
        
        with col3:
            st.markdown("""
            **📊 종합 분석**
            - 기술적 분석
            - 기본적 분석  
            - 리스크 평가
            - 투자 추천
            """)
    
    def display_analysis_results(
        self,
        ticker: str,
        market: str,
        final_decision: str,
        agent_results: Dict[str, str],
        analysis_data: Dict[str, Any],
        price_history: pd.DataFrame
    ):
        """Display analysis results using native components."""
        
        # Header with ticker info
        company_name = self._get_company_name(analysis_data, ticker)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(f"📈 {ticker}")
            if company_name:
                st.caption(company_name)
        
        with col2:
            market_emoji = "🇺🇸" if market == "미국장" else "🇰🇷"
            st.metric("시장", f"{market_emoji} {market}")
            
            # Check data quality and show warning if needed
            stock_info = analysis_data.get('stock_info', {})
            data_source = stock_info.get('source', '')
            data_quality = stock_info.get('data_quality', '')
            
            if 'mock' in data_source.lower() or 'mock' in data_quality.lower():
                st.warning("⚠️ 일부 데이터는 시뮬레이션 데이터입니다")
        
        st.divider()
        
        # Main layout
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # Investment decision
            self._render_investment_decision(final_decision)
            
            # Agent analyses
            self._render_agent_analyses(agent_results)
        
        with right_col:
            # Stock information
            self._render_stock_info(analysis_data.get('stock_info', {}))
            
            # Key metrics
            self._render_key_metrics(analysis_data)
        
        # Price chart (full width)
        if not price_history.empty:
            self._render_price_chart(price_history, ticker)
        else:
            st.warning("📊 차트 데이터를 불러올 수 없습니다.")
    
    def _get_company_name(self, analysis_data: Dict[str, Any], ticker: str = "") -> str:
        """Extract company name from analysis data."""
        stock_info = analysis_data.get('stock_info', {})
        
        # Try various name fields
        for field in ['longName', 'shortName', '회사명', 'companyName']:
            if field in stock_info and stock_info[field]:
                name = stock_info[field]
                if name != "정보 없음" and name != ticker:
                    return name
        
        return ""
    
    def _render_investment_decision(self, decision: str):
        """Render investment decision."""
        st.markdown("### 💡 투자 추천")
        
        # Extract decision type and determine color
        decision_type = "보유"
        if "매수" in decision or "BUY" in decision.upper():
            decision_type = "매수"
            st.success(f"**추천: {decision_type}** ✅")
        elif "매도" in decision or "SELL" in decision.upper():
            decision_type = "매도"
            st.error(f"**추천: {decision_type}** ❌")
        else:
            st.warning(f"**추천: {decision_type}** ⚠️")
        
        # Decision details
        with st.expander("상세 분석 내용", expanded=True):
            st.write(decision)
    
    def _render_agent_analyses(self, agent_results: Dict[str, str]):
        """Render agent analyses in tabs."""
        if not agent_results:
            st.warning("전문가 분석 데이터가 없습니다.")
            return
        
        st.markdown("### 🧠 전문가 분석")
        
        # Agent name mapping with emojis
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
                    if analysis and analysis.strip():
                        st.write(analysis)
                    else:
                        st.info("분석 결과가 없습니다.")
        else:
            # Single analysis
            for agent, analysis in agent_results.items():
                agent_name = agent_names.get(agent, agent)
                st.markdown(f"#### {agent_name}")
                if analysis and analysis.strip():
                    st.write(analysis)
                else:
                    st.info("분석 결과가 없습니다.")
    
    def _render_stock_info(self, stock_info: Dict[str, Any]):
        """Render stock information."""
        st.markdown("### 📋 종목 정보")
        
        if not stock_info:
            st.info("종목 정보를 불러오는 중...")
            return
        
        # Extract and display key information
        info_data = []
        
        # Price data
        if 'currentPrice' in stock_info and stock_info['currentPrice']:
            info_data.append(["현재가", f"${stock_info['currentPrice']:.2f}"])
        elif '현재가' in stock_info and stock_info['현재가'] != "정보 없음":
            info_data.append(["현재가", str(stock_info['현재가'])])
        
        # Valuation metrics
        for korean_key, english_key in [('PER', 'forwardPE'), ('PBR', 'priceToBook')]:
            value = None
            if english_key in stock_info and stock_info[english_key]:
                value = f"{stock_info[english_key]:.1f}"
            elif korean_key in stock_info and stock_info[korean_key] != "정보 없음":
                value = str(stock_info[korean_key])
            
            if value:
                info_data.append([korean_key, value])
        
        # ROE
        if 'returnOnEquity' in stock_info and stock_info['returnOnEquity']:
            info_data.append(["ROE", f"{stock_info['returnOnEquity']:.1%}"])
        elif 'ROE' in stock_info and stock_info['ROE'] != "정보 없음":
            info_data.append(["ROE", str(stock_info['ROE'])])
        
        # Market cap
        if 'marketCap' in stock_info and stock_info['marketCap']:
            market_cap = stock_info['marketCap']
            if isinstance(market_cap, (int, float)):
                if market_cap > 1e12:
                    info_data.append(["시가총액", f"${market_cap/1e12:.1f}T"])
                elif market_cap > 1e9:
                    info_data.append(["시가총액", f"${market_cap/1e9:.1f}B"])
                else:
                    info_data.append(["시가총액", f"${market_cap/1e6:.1f}M"])
        elif '시가총액' in stock_info and stock_info['시가총액'] != "정보 없음":
            info_data.append(["시가총액", str(stock_info['시가총액'])])
        
        # 52-week range
        for label, key in [("52주 최고", "52주 최고가"), ("52주 최저", "52주 최저가")]:
            if key in stock_info and stock_info[key] != "정보 없음":
                try:
                    value = float(stock_info[key])
                    info_data.append([label, f"${value:.2f}"])
                except:
                    info_data.append([label, str(stock_info[key])])
        
        # Display as metrics
        if info_data:
            for i in range(0, len(info_data), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(info_data):
                        label, value = info_data[i + j]
                        with col:
                            st.metric(label, value)
        else:
            st.info("종목 정보를 불러오는 중...")
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]):
        """Render key analysis metrics."""
        st.markdown("### 📊 주요 지표")
        
        technical = analysis_data.get('technical_analysis', {})
        fundamental = analysis_data.get('fundamental_analysis', {})
        
        metrics_data = []
        
        # Technical indicators
        if 'rsi' in technical and isinstance(technical['rsi'], (int, float)):
            rsi = technical['rsi']
            color = "normal"
            if rsi > 70:
                color = "inverse"  # Overbought
            elif rsi < 30:
                color = "off"  # Oversold
            metrics_data.append(("RSI", f"{rsi:.1f}", color))
        
        if 'macd_signal' in technical and technical['macd_signal'] in ['BUY', 'SELL', 'HOLD']:
            signal = technical['macd_signal']
            signal_map = {'BUY': '매수', 'SELL': '매도', 'HOLD': '보유'}
            color = "normal" if signal == 'BUY' else "inverse" if signal == 'SELL' else "off"
            metrics_data.append(("MACD", signal_map.get(signal, signal), color))
        
        # Fundamental scores
        if 'overall_score' in fundamental and isinstance(fundamental['overall_score'], (int, float)):
            score = fundamental['overall_score']
            color = "normal" if score >= 7 else "off" if score >= 5 else "inverse"
            metrics_data.append(("종합점수", f"{score:.1f}/10", color))
        
        if 'growth_score' in fundamental and isinstance(fundamental['growth_score'], (int, float)):
            score = fundamental['growth_score']
            color = "normal" if score >= 7 else "off" if score >= 5 else "inverse"
            metrics_data.append(("성장성", f"{score:.1f}/10", color))
        
        # Display metrics
        if metrics_data:
            cols = st.columns(len(metrics_data))
            for i, (label, value, color) in enumerate(metrics_data):
                with cols[i]:
                    # Note: Streamlit doesn't support color parameter in st.metric in all versions
                    st.metric(label, value)
        else:
            st.info("지표를 계산하는 중...")
    
    def _render_price_chart(self, price_history: pd.DataFrame, ticker: str):
        """Render price chart using Plotly."""
        st.markdown("### 📈 주가 차트")
        
        try:
            if 'Close' in price_history.columns:
                # Create Plotly line chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=price_history.index,
                    y=price_history['Close'],
                    mode='lines',
                    name=ticker,
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.update_layout(
                    title=f"{ticker} 주가 추이",
                    xaxis_title="날짜",
                    yaxis_title="주가 ($)",
                    height=400,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback to simple line chart
                chart_data = price_history.copy()
                if not chart_data.empty:
                    st.line_chart(chart_data, height=400)
                else:
                    st.info("차트 데이터가 없습니다.")
        except Exception as e:
            st.warning(f"차트를 표시할 수 없습니다: {str(e)}")
            # Fallback to simple display
            if not price_history.empty:
                st.dataframe(price_history.tail(10))
    
    def display_error(self, error_message: str):
        """Display error message."""
        st.error(f"❌ {error_message}")
    
    def display_warning(self, warning_message: str):
        """Display warning message."""
        st.warning(f"⚠️ {warning_message}")
    
    def display_success(self, success_message: str):
        """Display success message."""
        st.success(f"✅ {success_message}")