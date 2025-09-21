"""
Minimal and Intuitive UI for AI Investment Advisory System

Focus on simplicity, clarity, and user guidance.
Clean design without gradients or excessive styling.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def apply_minimal_theme():
    """Apply minimal theme - simple and clean."""
    st.markdown("""
    <style>
        /* Reset and base styles */
        .main {
            background: #fafafa;
            padding: 0;
        }

        /* Remove Streamlit header */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        /* Clean container */
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 1200px !important;
        }

        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stDecoration"] {display: none !important;}

        /* Simple button */
        .stButton button {
            background: #2563eb;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 4px;
            font-weight: 500;
            transition: background 0.2s;
        }

        .stButton button:hover {
            background: #1d4ed8;
        }

        /* Clean input fields */
        .stTextInput input, .stSelectbox > div > div {
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 0.5rem;
        }

        .stTextInput input:focus {
            border-color: #2563eb;
            outline: none;
        }

        /* Radio button styling */
        .stRadio > div {
            flex-direction: row !important;
            gap: 1rem;
        }

        .stRadio label {
            font-weight: 500;
            margin-bottom: 0.25rem;
        }

        /* Simple metrics */
        [data-testid="metric-container"] {
            background: #f9fafb;
            padding: 1rem;
            border-radius: 4px;
            border: 1px solid #e5e7eb;
        }

        /* Typography */
        h1, h2, h3 {
            color: #111827;
            font-weight: 600;
        }

        /* Info boxes */
        .info-box {
            background: #f0f9ff;
            border-left: 4px solid #2563eb;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 4px 4px 0;
        }

        .help-text {
            color: #6b7280;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 2rem;
        }

        /* Progress text */
        div[data-testid="stText"] {
            font-size: 0.95rem;
            color: #374151;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Simple header with clear title and description."""
    st.markdown("# AI 투자 분석 시스템")
    st.markdown("6개의 전문 AI가 종목을 분석하여 투자 의견을 제공합니다")
    st.markdown("")  # spacing

def render_how_to_use():
    """Show how to use guide for first-time users."""
    with st.expander("ℹ️ 사용 방법", expanded=False):
        st.markdown("""
        **간단 가이드**
        1. 종목 코드 입력 (예: AAPL, 005930)
        2. 시장 선택 (미국장/한국장)
        3. 분석 시작 클릭
        4. 약 30초 후 결과 확인
        """)

def render_stock_input_section():
    """Stock input section with clear labels and help text."""
    # Create a single row for input elements
    col1, col2 = st.columns([3, 1.5])

    with col1:
        subcol1, subcol2 = st.columns([2, 1.2])

        with subcol1:
            ticker = st.text_input(
                "종목 코드",
                placeholder="AAPL 또는 005930",
                help="미국: AAPL, TSLA | 한국: 005930, 000660"
            )

        with subcol2:
            # Use radio buttons instead of selectbox for better visibility
            market = st.radio(
                "시장",
                options=["미국장", "한국장"],
                horizontal=True,
                label_visibility="visible"
            )

    with col2:
        # Add spacing to align with input fields
        st.markdown("<div style='height: 29px;'></div>", unsafe_allow_html=True)
        analyze_button = st.button("분석 시작", type="primary", use_container_width=True)

    if not ticker and analyze_button:
        st.warning("⚠️ 종목 코드를 입력해주세요")
        return None, None, False

    return ticker, market, analyze_button

def render_quick_stats(stock_data: Dict[str, Any]):
    """Display key metrics in a simple format."""
    st.markdown("### 📊 핵심 지표")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        price = stock_data.get("currentPrice", "N/A")
        change = stock_data.get("priceChange", 0)
        ticker = stock_data.get("ticker", "")

        if isinstance(price, (int, float)):
            # Check if it's a Korean stock (numeric ticker)
            if ticker and ticker.isdigit():
                price_str = f"₩{price:,.0f}" if price >= 1000 else f"₩{price:,.2f}"
            else:
                price_str = f"${price:,.2f}"
            
            st.metric(
                "현재가",
                price_str,
                f"{change:+.2f}%" if isinstance(change, float) else None
            )
        else:
            st.metric("현재가", "데이터 없음")

    with col2:
        per = stock_data.get("PER", "N/A")
        st.metric(
            "PER",
            f"{per:.2f}" if isinstance(per, (int, float)) else "N/A",
            help="낮을수록 저평가"
        )

    with col3:
        pbr = stock_data.get("PBR", "N/A")
        st.metric(
            "PBR",
            f"{pbr:.2f}" if isinstance(pbr, (int, float)) else "N/A",
            help="1 미만은 장부가치 대비 저평가"
        )

    with col4:
        # Try different volume keys
        volume = stock_data.get("volume", stock_data.get("거래량", stock_data.get("Volume", 0)))
        if isinstance(volume, (int, float)):
            if volume > 1000000:
                volume_str = f"{volume/1000000:.1f}M"
            elif volume > 1000:
                volume_str = f"{volume/1000:.1f}K"
            else:
                volume_str = f"{volume:,.0f}"
            st.metric("거래량", volume_str)
        else:
            st.metric("거래량", "N/A")

def render_analysis_results(analysis_results: Dict[str, Any]):
    """Display analysis results in a clear, organized way."""

    # Final decision at the top
    decision = analysis_results.get("final_decision", {})
    if decision:
        render_investment_decision(decision)

    # Detailed analysis in tabs
    st.markdown("### 🤖 AI 분석 상세")

    tab1, tab2, tab3, tab4 = st.tabs([
        "기업 분석",
        "기술적 분석",
        "리스크 평가",
        "산업 동향"
    ])

    with tab1:
        render_agent_analysis(
            analysis_results.get("company_analyst", {}),
            "기업의 재무 상태와 성장 가능성을 분석합니다"
        )

    with tab2:
        render_agent_analysis(
            analysis_results.get("technical_analyst", {}),
            "차트 패턴과 기술 지표를 분석합니다"
        )

    with tab3:
        render_agent_analysis(
            analysis_results.get("risk_manager", {}),
            "투자 리스크와 하방 위험을 평가합니다"
        )

    with tab4:
        render_agent_analysis(
            analysis_results.get("industry_expert", {}),
            "산업 전망과 경쟁 환경을 분석합니다"
        )

def render_investment_decision(decision: Dict[str, Any]):
    """Display the final investment decision clearly."""
    st.markdown("### 🎯 투자 결정")

    # Create info box for decision
    rating = decision.get("rating", "HOLD")
    confidence = decision.get("confidence", "보통")

    # Decision colors
    rating_colors = {
        "STRONG BUY": "#16a34a",
        "BUY": "#22c55e",
        "HOLD": "#eab308",
        "SELL": "#f97316",
        "STRONG SELL": "#dc2626"
    }

    # Decision box
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        color = rating_colors.get(rating, "#6b7280")
        st.markdown(f"""
        <div style='padding: 1rem; background: {color}15; border-left: 4px solid {color}; border-radius: 0 4px 4px 0;'>
            <div style='font-size: 0.875rem; color: #6b7280;'>AI 투자 의견</div>
            <div style='font-size: 1.5rem; font-weight: bold; color: {color};'>{rating}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='padding: 1rem; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px;'>
            <div style='font-size: 0.875rem; color: #6b7280;'>신뢰도</div>
            <div style='font-size: 1.25rem; font-weight: bold; color: #111827;'>{confidence}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        target_price = decision.get("target_price", "N/A")
        if isinstance(target_price, (int, float)):
            target_str = f"${target_price:,.0f}"
        else:
            target_str = "산출중"

        st.markdown(f"""
        <div style='padding: 1rem; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px;'>
            <div style='font-size: 0.875rem; color: #6b7280;'>목표가</div>
            <div style='font-size: 1.25rem; font-weight: bold; color: #111827;'>{target_str}</div>
        </div>
        """, unsafe_allow_html=True)

    # Key insights
    st.markdown("#### 💡 핵심 근거")
    key_points = decision.get("key_points", [])
    if key_points:
        for i, point in enumerate(key_points[:3], 1):
            st.markdown(f"{i}. {point}")
    else:
        st.info("분석 중입니다...")

def render_agent_analysis(analysis: Dict[str, Any], description: str):
    """Display individual agent analysis."""
    if not analysis:
        st.info("분석 대기 중...")
        return

    # Description
    st.markdown(f"*{description}*")
    st.markdown("")

    # Handle both dict and string formats
    if isinstance(analysis, str):
        # If it's a string, convert to dict format
        analysis = {
            'analysis': analysis,
            'confidence': '보통'
        }
    elif not isinstance(analysis, dict):
        analysis = {
            'analysis': str(analysis) if analysis else '분석 중...',
            'confidence': '보통'
        }

    # Confidence level
    confidence = analysis.get("confidence", "보통")
    conf_emoji = {"높음": "🟢", "보통": "🟡", "낮음": "🔴"}.get(confidence, "⚪")
    st.markdown(f"**신뢰도**: {conf_emoji} {confidence}")

    # Analysis content
    content = analysis.get("analysis", "")
    if content:
        # Clean format
        st.markdown("**분석 내용:**")
        st.markdown(content)

def render_price_chart(hist_data: pd.DataFrame, ticker: str):
    """Simple, clean price chart."""
    if hist_data.empty:
        st.info("차트 데이터를 불러올 수 없습니다")
        return

    # Create simple line chart
    fig = go.Figure()

    # Add price line
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        mode='lines',
        name='종가',
        line=dict(color='#2563eb', width=2)
    ))

    # Simple layout
    fig.update_layout(
        title=f"{ticker} 주가 추이",
        xaxis_title="날짜",
        yaxis_title="가격 ($)",
        template='simple_white',
        height=400,
        showlegend=False,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

def render_technical_chart(hist_data: pd.DataFrame):
    """Simple technical indicators."""
    if hist_data.empty:
        return

    # Calculate simple moving averages
    hist_data['MA20'] = hist_data['Close'].rolling(window=20).mean()
    hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()

    # Create chart
    fig = go.Figure()

    # Price
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        name='종가',
        line=dict(color='#111827', width=2)
    ))

    # Moving averages
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['MA20'],
        name='20일 이평',
        line=dict(color='#ef4444', width=1, dash='dot')
    ))

    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['MA50'],
        name='50일 이평',
        line=dict(color='#3b82f6', width=1, dash='dot')
    ))

    # Layout
    fig.update_layout(
        title="이동평균선",
        xaxis_title="날짜",
        yaxis_title="가격 ($)",
        template='simple_white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

def render_loading():
    """Simple loading message."""
    placeholder = st.empty()
    with placeholder.container():
        st.info("🔄 AI가 종목을 분석하고 있습니다... (약 30초 소요)")
        st.markdown("""
        분석 중인 항목:
        - 재무제표 분석
        - 기술적 지표 계산
        - 산업 동향 파악
        - 리스크 평가
        - 종합 의견 도출
        """)
    return placeholder

def render_error(error: str):
    """Simple error message."""
    st.error(f"""
    ❌ 오류가 발생했습니다

    {error}

    **해결 방법:**
    1. 종목 코드가 정확한지 확인하세요
    2. 인터넷 연결을 확인하세요
    3. 잠시 후 다시 시도해보세요
    """)

def render_footer():
    """Simple footer."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b7280; font-size: 0.875rem; padding: 1rem;'>
        <p>⚠️ 이 시스템은 투자 참고용입니다. 실제 투자는 본인의 판단과 책임하에 결정하세요.</p>
        <p>AI Investment Advisory System v0.2 (Beta)</p>
    </div>
    """, unsafe_allow_html=True)
