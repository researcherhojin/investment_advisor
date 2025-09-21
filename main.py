"""
AI Investment Advisory System - Simple Main Application

Simplified and intuitive UI for better user experience.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging BEFORE importing other modules
from investment_advisor.utils.logging_config import configure_logging
configure_logging(log_level="INFO", suppress_external=True)

import streamlit as st
from datetime import datetime

# Import shared configuration
from shared_config import shared_config

# Set page config as the very first Streamlit command
st.set_page_config(
    page_title="AI 투자 자문 시스템",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-investment-advisor',
        'Report a bug': 'https://github.com/yourusername/ai-investment-advisor/issues',
        'About': f'AI Investment Advisory System v2.0'
    }
)

# Try to get config
try:
    from investment_advisor.utils import get_config
    config = get_config()
except Exception as e:
    st.error(f"""
    ⚠️ 설정 오류가 발생했습니다.

    {str(e)}

    환경 설정을 확인해주세요.
    """)
    st.stop()

# Import necessary modules
from investment_advisor.ui.minimal_ui import (
    apply_minimal_theme,
    render_header,
    render_how_to_use,
    render_stock_input_section,
    render_quick_stats,
    render_analysis_results,
    render_price_chart,
    render_technical_chart,
    render_loading,
    render_error,
    render_footer
)
from investment_advisor.data.stable_fetcher import StableFetcher
from investment_advisor.analysis import InvestmentDecisionSystem

# Set up logging
logger = logging.getLogger(__name__)


def main():
    """Main application entry point with simplified UI."""

    # Apply minimal theme
    apply_minimal_theme()

    # Render header
    render_header()

    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzing' not in st.session_state:
        st.session_state.analyzing = False
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

    # Show how to use guide for first visit
    if st.session_state.first_visit:
        render_how_to_use()
        st.session_state.first_visit = False

    # Stock input section
    ticker, market, analyze_button = render_stock_input_section()

    # Handle analysis
    if analyze_button and ticker and not st.session_state.analyzing:
        st.session_state.analyzing = True
        st.session_state.analysis_results = None

        # Create placeholder for results
        results_container = st.container()

        with results_container:
            # Show loading message
            loading_placeholder = render_loading()
            try:
                # Initialize systems
                decision_system = InvestmentDecisionSystem()

                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Update progress
                def update_progress(step: int, total: int, message: str):
                    progress = step / total
                    progress_bar.progress(progress)
                    status_text.text(f"📊 {message} ({step}/{total})")

                # Perform analysis steps
                update_progress(1, 5, "데이터 수집 중...")
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)

                # Use decision_system to fetch data (it will try Yahoo Finance first)
                stock_data, price_history = decision_system.fetch_stock_data(ticker, start_date, end_date)

                update_progress(2, 5, "가격 데이터 분석 중...")

                update_progress(3, 5, "AI 에이전트 분석 중...")

                # Progress callback for decision system
                def progress_callback(message: str, progress_percent: int = 50):
                    # Map progress from 60% to 90%
                    mapped_progress = 3 + (progress_percent / 100) * 1.5
                    # Don't show the step counter here - just the message
                    status_text.text(f"📊 {message}")

                # Run comprehensive analysis
                # Get industry from stock data or default
                industry = stock_data.get('sector', 'Technology')
                final_decision, agent_results, analysis_data, price_hist = decision_system.make_decision(
                    ticker=ticker,
                    industry=industry,
                    market=market,
                    progress_callback=progress_callback
                )

                # Format results for display
                # Parse final decision string to extract rating and details
                decision_dict = {
                    'rating': 'HOLD',  # Default rating
                    'confidence': '보통',
                    'summary': final_decision if final_decision else '분석 중...',
                    'key_points': []
                }

                # Try to extract rating from the final decision text
                if final_decision:
                    decision_upper = final_decision.upper()
                    if 'STRONG BUY' in decision_upper or '강력 매수' in final_decision:
                        decision_dict['rating'] = 'STRONG BUY'
                    elif 'BUY' in decision_upper or '매수' in final_decision:
                        decision_dict['rating'] = 'BUY'
                    elif 'SELL' in decision_upper or '매도' in final_decision:
                        decision_dict['rating'] = 'SELL'
                    elif 'STRONG SELL' in decision_upper or '강력 매도' in final_decision:
                        decision_dict['rating'] = 'STRONG SELL'

                    # Extract confidence level
                    if '높음' in final_decision or '강한' in final_decision:
                        decision_dict['confidence'] = '높음'
                    elif '낮음' in final_decision or '약한' in final_decision:
                        decision_dict['confidence'] = '낮음'

                # Helper function to format agent result
                def format_agent_result(agent_text):
                    if isinstance(agent_text, dict):
                        return agent_text
                    if isinstance(agent_text, str) and agent_text:
                        # Remove header and footer if present
                        content = agent_text

                        # Remove the header part (## 에이전트이름의 분석...)
                        if "## " in content and "의 분석" in content:
                            header_end = content.find("\n", content.find("의 분석"))
                            if header_end != -1:
                                # Skip past the data quality and timestamp lines too
                                content_start = content.find("\n\n", header_end)
                                if content_start != -1:
                                    content = content[content_start:].strip()

                        # Remove the footer part (---\n*에이전트이름...)
                        if "\n---\n" in content:
                            content = content[:content.rfind("\n---\n")].strip()

                        # Extract confidence from original text
                        confidence = '보통'
                        if '높음 신뢰도' in agent_text:
                            confidence = '높음'
                        elif '낮음 신뢰도' in agent_text:
                            confidence = '낮음'

                        return {
                            'analysis': content if content else agent_text,
                            'confidence': confidence
                        }
                    return {'analysis': '분석 대기 중...', 'confidence': '보통'}

                analysis_results = {
                    'final_decision': decision_dict,
                    'company_analyst': format_agent_result(agent_results.get('기업분석가', '')),
                    'technical_analyst': format_agent_result(agent_results.get('기술분석가', '')),
                    'risk_manager': format_agent_result(agent_results.get('리스크관리자', '')),
                    'industry_expert': format_agent_result(agent_results.get('산업전문가', ''))
                }

                update_progress(5, 5, "분석 완료!")

                # Store results
                st.session_state.analysis_results = {
                    'ticker': ticker,
                    'market': market,
                    'stock_data': stock_data,
                    'price_history': price_history,
                    'analysis': analysis_results
                }

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                # Success message
                st.success(f"✅ {ticker} 분석이 완료되었습니다!")

                # Clear loading
                loading_placeholder.empty()

            except Exception as e:
                logger.error(f"Analysis error: {e}")
                loading_placeholder.empty()
                render_error(str(e))
            finally:
                st.session_state.analyzing = False

    # Display results if available
    if st.session_state.analysis_results and not st.session_state.analyzing:
        results = st.session_state.analysis_results

        st.markdown("---")

        # Quick stats section
        if results.get('stock_data'):
            render_quick_stats(results['stock_data'])

        # Charts section
        if results.get('price_history') is not None and not results['price_history'].empty:
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📈 가격 차트")
                render_price_chart(results['price_history'], results['ticker'])

            with col2:
                st.markdown("### 📊 기술적 지표")
                render_technical_chart(results['price_history'])

        # Analysis results section
        if results.get('analysis'):
            st.markdown("---")
            render_analysis_results(results['analysis'])

    # Footer
    render_footer()

    # Sidebar with help and settings
    with st.sidebar:
        with st.expander("📚 도움말", expanded=False):
            st.markdown("""
            **사용 방법:**
            1. 종목 코드 입력
            2. 시장 선택 (미국/한국)
            3. 분석 시작 클릭

            **종목 코드 예시:**
            - 미국: AAPL, GOOGL, TSLA
            - 한국: 005930, 000660, 035720
            """)

        st.markdown("---")

        if st.session_state.analysis_results:
            if st.button("🗑️ 결과 초기화", use_container_width=True):
                st.session_state.analysis_results = None
                st.session_state.analyzing = False
                st.rerun()


if __name__ == "__main__":
    main()
