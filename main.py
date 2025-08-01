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
from investment_advisor.ui.minimal_layout import MinimalLayoutManager
from investment_advisor.analysis import InvestmentDecisionSystem

# Set up logging
logger = setup_logging()


def main():
    """Main application entry point."""
    # Initialize minimal UI components
    layout_manager = MinimalLayoutManager()
    # Call setup_page to inject minimal CSS
    layout_manager.setup_page()
    
    # Render minimal header
    layout_manager.render_header()
    
    # Get user inputs from minimal sidebar
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
            layout_manager.display_error("종목 코드를 입력해주세요.")
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
    
    elif user_inputs['actions']['clear']:
        # Clear session state
        st.session_state.clear()
        st.rerun()
    
    # Render main content
    if st.session_state.get('analysis_results'):
        display_minimal_results(
            st.session_state.analysis_results,
            layout_manager
        )
    else:
        layout_manager.render_main_content()


def run_analysis(
    ticker: str,
    market: str,
    industry: str,
    period: int,
    advanced_options: dict,
    layout_manager: MinimalLayoutManager
):
    """Run the investment analysis."""
    try:
        # Set analysis started flag
        st.session_state.analysis_started = True
        
        # Initialize decision system
        decision_system = InvestmentDecisionSystem()
        
        # Run the complete analysis
        with st.spinner("AI 에이전트들이 종합 분석을 수행하고 있습니다..."):
            final_decision, agent_results, analysis_data, price_history = decision_system.make_decision(
                ticker=ticker,
                industry=industry,
                market=market,
                analysis_period=period,
                progress_callback=None  # Will add progress callback later
            )
        
        # Check for errors
        if final_decision is None or "error" in analysis_data:
            error_msg = analysis_data.get("error", "알 수 없는 오류가 발생했습니다.")
            layout_manager.display_error(f"분석 실패: {error_msg}")
            st.session_state.analysis_started = False
            return
        
        # Get recommendations if enabled (temporarily disabled due to API issues)
        recommendations = None
        if advanced_options.get('include_recommendations', True):
            try:
                recommendations = decision_system.get_recommendations(ticker, market)
            except Exception as rec_error:
                logger.warning(f"Failed to get recommendations: {rec_error}")
                recommendations = None
        
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


def display_minimal_results(results: dict, layout_manager: MinimalLayoutManager):
    """Display analysis results using minimal components."""
    try:
        layout_manager.display_analysis_results(
            ticker=results['ticker'],
            market=results['market'],
            final_decision=results['final_decision'],
            agent_results=results['agent_results'],
            analysis_data=results['analysis_data'],
            price_history=results['price_history']
        )
        
        # Show timestamp
        timestamp = results.get('timestamp', datetime.now())
        st.markdown(f"""
        <div style="text-align: center; color: #666666; font-family: 'Consolas', monospace; font-size: 11px; margin-top: 20px;">
            ANALYSIS COMPLETED: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}", exc_info=True)
        layout_manager.display_error(f"DISPLAY ERROR: {str(e)}")




if __name__ == "__main__":
    main()