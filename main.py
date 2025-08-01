"""
AI Investment Advisory System - Main Application

This is the main entry point for the Streamlit application.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config as the very first Streamlit command
st.set_page_config(
    page_title="AI 투자 자문 서비스",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-investment-advisor',
        'Report a bug': 'https://github.com/yourusername/ai-investment-advisor/issues',
        'About': 'AI 투자 자문 시스템 v2.0'
    }
)

# Now try to get config
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

# Now import other modules
from investment_advisor.utils import setup_logging, InputValidator
from investment_advisor.ui import LayoutManager, ChartGenerator, MetricsDisplay
from investment_advisor.analysis import InvestmentDecisionSystem

# Set up logging
logger = setup_logging()


def main():
    """Main application entry point."""
    # Initialize UI components
    layout_manager = LayoutManager()
    # Call setup_page to inject CSS
    layout_manager.setup_page()
    
    # Render header
    layout_manager.render_header()
    
    # Get user inputs from sidebar
    user_inputs = layout_manager.render_sidebar()
    
    # Initialize validator
    validator = InputValidator()
    
    # Handle main actions
    if user_inputs['actions']['analyze']:
        # Validate inputs
        ticker = user_inputs['ticker']
        market = user_inputs['market']
        industry = user_inputs['industry']
        period = user_inputs['period']
        
        if not ticker:
            layout_manager.display_error("티커를 입력해주세요.")
            return
        
        # Validate ticker format
        ticker_validation = validator.validate_ticker(ticker, market)
        if not ticker_validation['valid']:
            layout_manager.display_error(ticker_validation['message'])
            return
        
        # Start analysis
        run_analysis(
            ticker=ticker_validation['normalized_ticker'],
            market=market,
            industry=industry,
            period=period,
            advanced_options=user_inputs['advanced'],
            layout_manager=layout_manager
        )
    
    elif user_inputs['actions']['reset']:
        # Reset session state
        st.session_state.clear()
        st.rerun()
    
    elif user_inputs['actions']['export']:
        # Export results
        if st.session_state.analysis_results:
            export_results(st.session_state.analysis_results)
        else:
            layout_manager.display_warning("분석 결과가 없습니다.")
    
    # Render main content
    if st.session_state.get('analysis_results'):
        display_results(
            st.session_state.analysis_results,
            layout_manager,
            user_inputs['advanced']
        )
    else:
        layout_manager.render_main_content()


def run_analysis(
    ticker: str,
    market: str,
    industry: str,
    period: int,
    advanced_options: dict,
    layout_manager: LayoutManager
):
    """Run the investment analysis."""
    try:
        # Set analysis started flag
        st.session_state.analysis_started = True
        
        # Create progress placeholder
        progress_bar, status_text = layout_manager.display_progress(
            "분석을 시작합니다...", 0
        )
        
        # Initialize decision system
        decision_system = InvestmentDecisionSystem()
        
        # Define progress callback
        def progress_callback(message: str, progress: int):
            progress_bar.progress(progress / 100)
            status_text.text(message)
        
        # Run analysis
        with st.spinner("AI 에이전트들이 분석 중입니다..."):
            final_decision, agent_results, analysis_data, price_history = \
                decision_system.make_decision(
                    ticker=ticker,
                    industry=industry,
                    market=market,
                    analysis_period=period,
                    progress_callback=progress_callback
                )
        
        # Check for errors
        if final_decision is None or "error" in analysis_data:
            error_msg = analysis_data.get("error", "알 수 없는 오류가 발생했습니다.")
            layout_manager.display_error(f"분석 실패: {error_msg}")
            st.session_state.analysis_started = False
            return
        
        # Get recommendations if enabled
        recommendations = None
        if advanced_options.get('include_recommendations', True):
            recommendations = decision_system.get_recommendations(ticker, market)
        
        # Store results in session state
        st.session_state.analysis_results = {
            'ticker': ticker,
            'market': market,
            'industry': industry,
            'final_decision': final_decision,
            'agent_results': agent_results,
            'analysis_data': analysis_data,
            'price_history': price_history,
            'recommendations': recommendations,
            'timestamp': datetime.now()
        }
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Success message
        layout_manager.display_success("분석이 완료되었습니다!")
        
        # Reset analysis started flag
        st.session_state.analysis_started = False
        
        # Rerun to display results
        st.rerun()
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        layout_manager.display_error(f"분석 중 오류가 발생했습니다: {str(e)}")
        st.session_state.analysis_started = False


def display_results(results: dict, layout_manager: LayoutManager, advanced_options: dict):
    """Display analysis results."""
    # Initialize display components
    chart_generator = ChartGenerator()
    metrics_display = MetricsDisplay(results['market'])
    
    # Create tabs
    tab_names = [
        "📊 종합 분석",
        "📈 기술적 분석", 
        "📉 기본적 분석",
        "🤖 AI 전문가 의견",
        "📋 상세 지표"
    ]
    
    if results.get('recommendations') is not None and not results['recommendations'].empty:
        tab_names.append("💡 추천 종목")
    
    tabs = st.tabs(tab_names)
    
    # Tab 1: Overview
    with tabs[0]:
        display_overview_tab(results, metrics_display)
    
    # Tab 2: Technical Analysis
    with tabs[1]:
        display_technical_tab(results, chart_generator, metrics_display)
    
    # Tab 3: Fundamental Analysis
    with tabs[2]:
        display_fundamental_tab(results, metrics_display)
    
    # Tab 4: AI Expert Opinions
    with tabs[3]:
        display_ai_opinions_tab(results)
    
    # Tab 5: Detailed Metrics
    with tabs[4]:
        display_metrics_tab(results, metrics_display)
    
    # Tab 6: Recommendations (if available)
    if len(tabs) > 5:
        with tabs[5]:
            display_recommendations_tab(results, metrics_display)


def display_overview_tab(results: dict, metrics_display: MetricsDisplay):
    """Display overview tab."""
    st.header(f"{results['ticker']} 종합 투자 분석")
    
    # Display final decision
    st.markdown("### 🎯 최종 투자 의견")
    st.markdown(results['final_decision'])
    
    # Key metrics summary
    st.markdown("### 📊 주요 지표")
    stock_info = results['analysis_data'].get('stock_info', {})
    metrics_display.display_key_metrics(stock_info)
    
    # Analysis scores
    st.markdown("### 📈 분석 점수")
    technical_score = results['analysis_data'].get('technical_analysis', {}).get('technical_score', 50)
    fundamental_score = results['analysis_data'].get('fundamental_analysis', {}).get('fundamental_score', 50)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("기술적 분석", f"{technical_score}/100")
        st.progress(technical_score / 100)
    
    with col2:
        st.metric("기본적 분석", f"{fundamental_score}/100")
        st.progress(fundamental_score / 100)
    
    # Price targets
    price_targets = results['analysis_data'].get('price_targets', {})
    if price_targets:
        metrics_display.display_price_targets(price_targets)


def display_technical_tab(results: dict, chart_generator: ChartGenerator, metrics_display: MetricsDisplay):
    """Display technical analysis tab."""
    st.header("📈 기술적 분석")
    
    # Main chart
    price_history = results['price_history']
    technical_data = results['analysis_data'].get('technical_analysis', {})
    
    if not price_history.empty:
        fig = chart_generator.create_main_chart(
            price_history,
            results['ticker'],
            results['market'],
            technical_data
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Technical indicators
    metrics_display.display_technical_indicators(technical_data)
    
    # Technical analysis from agent
    tech_analysis = results['agent_results'].get('기술분석가', '')
    if tech_analysis:
        st.markdown("### 🤖 기술분석가 의견")
        st.markdown(tech_analysis)


def display_fundamental_tab(results: dict, metrics_display: MetricsDisplay):
    """Display fundamental analysis tab."""
    st.header("📉 기본적 분석")
    
    # Fundamental analysis results
    fundamental_data = results['analysis_data'].get('fundamental_analysis', {})
    metrics_display.display_fundamental_analysis(fundamental_data)
    
    # Company analyst opinion
    company_analysis = results['agent_results'].get('기업분석가', '')
    if company_analysis:
        st.markdown("### 🤖 기업분석가 의견")
        st.markdown(company_analysis)
    
    # Economic indicators
    economic_data = results['analysis_data'].get('economic_indicators', {})
    if economic_data:
        metrics_display.display_economic_indicators(economic_data)


def display_ai_opinions_tab(results: dict):
    """Display AI expert opinions tab."""
    st.header("🤖 AI 전문가 의견")
    
    # Display each agent's analysis
    agent_order = [
        "기업분석가",
        "산업전문가",
        "거시경제전문가",
        "기술분석가",
        "리스크관리자"
    ]
    
    for agent_name in agent_order:
        if agent_name in results['agent_results']:
            with st.expander(f"{agent_name} 분석", expanded=True):
                st.markdown(results['agent_results'][agent_name])


def display_metrics_tab(results: dict, metrics_display: MetricsDisplay):
    """Display detailed metrics tab."""
    st.header("📋 상세 지표")
    
    # Stock info
    stock_info = results['analysis_data'].get('stock_info', {})
    
    # Create tabs for different metric categories
    metric_tabs = st.tabs(["재무 정보", "기술 지표", "리스크 지표", "원시 데이터"])
    
    with metric_tabs[0]:
        st.subheader("재무 정보")
        financial_metrics = {k: v for k, v in stock_info.items() 
                           if k in ['PER', 'PBR', 'ROE', '배당수익률', 'EPS', 'Revenue']}
        if financial_metrics:
            df = pd.DataFrame(list(financial_metrics.items()), columns=['지표', '값'])
            st.dataframe(df, use_container_width=True)
    
    with metric_tabs[1]:
        st.subheader("기술 지표")
        technical_data = results['analysis_data'].get('technical_analysis', {})
        if technical_data:
            # Filter out complex objects
            simple_tech_data = {k: v for k, v in technical_data.items() 
                              if isinstance(v, (int, float, str))}
            df = pd.DataFrame(list(simple_tech_data.items()), columns=['지표', '값'])
            st.dataframe(df, use_container_width=True)
    
    with metric_tabs[2]:
        st.subheader("리스크 지표")
        risk_metrics = {k: v for k, v in stock_info.items() 
                       if k in ['베타', '52주 최고가', '52주 최저가']}
        if risk_metrics:
            df = pd.DataFrame(list(risk_metrics.items()), columns=['지표', '값'])
            st.dataframe(df, use_container_width=True)
    
    with metric_tabs[3]:
        st.subheader("원시 데이터")
        with st.expander("전체 분석 데이터 (JSON)"):
            st.json(results['analysis_data'])


def display_recommendations_tab(results: dict, metrics_display: MetricsDisplay):
    """Display recommendations tab."""
    st.header("💡 추천 종목")
    
    recommendations = results.get('recommendations')
    if recommendations is not None and not recommendations.empty:
        if results['market'] == "한국장":
            metrics_display.display_recommendations_table(
                recommendations,
                "📈 오늘의 추천 한국 주식"
            )
        else:
            metrics_display.display_recommendations_table(
                recommendations,
                "📊 섹터별 성과"
            )
    else:
        st.info("추천 종목 데이터가 없습니다.")


def export_results(results: dict):
    """Export analysis results."""
    try:
        # Create export data
        export_data = {
            'analysis_date': results['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'ticker': results['ticker'],
            'market': results['market'],
            'industry': results['industry'],
            'final_decision': results['final_decision'],
            'stock_info': results['analysis_data'].get('stock_info', {}),
            'technical_analysis': results['analysis_data'].get('technical_analysis', {}),
            'fundamental_analysis': results['analysis_data'].get('fundamental_analysis', {}),
        }
        
        # Convert to JSON
        import json
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        # Download button
        st.download_button(
            label="📥 JSON으로 다운로드",
            data=json_str,
            file_name=f"{results['ticker']}_analysis_{results['timestamp'].strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.success("분석 결과를 다운로드할 수 있습니다.")
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        st.error(f"내보내기 중 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    main()