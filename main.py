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

# Configure logging BEFORE importing other modules
from investment_advisor.utils.logging_config import configure_logging
configure_logging(log_level="INFO", suppress_external=True)

import streamlit as st
import pandas as pd
from datetime import datetime

# Import shared configuration
from shared_config import shared_config

# Set page config as the very first Streamlit command
st.set_page_config(
    page_title=shared_config.app_name,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-investment-advisor',
        'Report a bug': 'https://github.com/yourusername/ai-investment-advisor/issues',
        'About': f'{shared_config.app_name} v{shared_config.version}'
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
from investment_advisor.ui.card_layout import CardLayoutManager
from investment_advisor.ui.dashboard import DashboardManager
from investment_advisor.ui.themes import ThemeManager
from investment_advisor.ui.clean_modern_ui import CleanModernUI
from investment_advisor.data.stable_fetcher import StableFetcher
from investment_advisor.analysis import InvestmentDecisionSystem

# Set up logging
logger = setup_logging()


def main():
    """Main application entry point."""
    # Initialize UI components
    theme_manager = ThemeManager()
    layout_manager = CardLayoutManager()
    dashboard_manager = DashboardManager()
    clean_ui = CleanModernUI()
    stable_fetcher = StableFetcher()
    
    # Setup clean modern page styling
    clean_ui.setup_page()
    
    # Get user inputs from sidebar
    user_inputs = clean_ui.render_sidebar()
    
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
            st.error("종목 코드를 입력해주세요.")
            return
        
        # Validate ticker format
        ticker_validation = validator.validate_ticker(ticker, market)
        
        if not ticker_validation['valid']:
            st.error(f"❌ {ticker_validation['message']}")
            return
        
        # 분석 시작 메시지
        st.success(f"✅ {ticker.upper()} 분석을 시작합니다!")
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Start analysis
        run_analysis(
            ticker=ticker_validation['normalized_ticker'],
            market=market,
            industry=industry,
            period=period,
            advanced_options=user_inputs['advanced'],
            layout_manager=clean_ui,
            progress_bar=progress_bar,
            status_text=status_text
        )
    
    elif user_inputs['actions']['clear']:
        # Clear session state
        st.success("🗑️ 모든 데이터가 초기화되었습니다.")
        for key in list(st.session_state.keys()):
            if key.startswith('analysis') or key in ['last_technical_analysis']:
                del st.session_state[key]
        st.rerun()
    
    # Render main content
    if st.session_state.get('analysis_results') and not st.session_state.get('analysis_started', False):
        st.markdown("# 📊 분석 결과")
        display_clean_modern_results(
            st.session_state.analysis_results,
            clean_ui,
            stable_fetcher
        )
    else:
        # Display market indices
        try:
            with st.spinner("시장 지표를 불러오는 중..."):
                indices = stable_fetcher.fetch_market_indices()
                if indices:  # Only render if we have data
                    clean_ui.render_market_indices(indices)
        except Exception as e:
            logger.warning(f"Failed to fetch market indices: {e}")
        
        # Welcome screen
        clean_ui.render_welcome()


def run_analysis(
    ticker: str,
    market: str,
    industry: str,
    period: int,
    advanced_options: dict,
    layout_manager,
    progress_bar=None,
    status_text=None
):
    """Run the investment analysis."""
    try:
        # Set analysis started flag
        st.session_state.analysis_started = True
        
        # 진행 상황 업데이트 함수
        def update_progress(step: int, total: int, message: str):
            if progress_bar and status_text:
                progress = step / total
                progress_bar.progress(progress)
                status_text.text(f"📊 {message} ({step}/{total})")
        
        # 초기 진행 상황
        update_progress(1, 6, "시스템 초기화 중...")
        
        # Initialize decision system
        decision_system = InvestmentDecisionSystem()
        
        update_progress(2, 6, "데이터 수집 중...")
        
        # Progress callback - flexible to handle different parameter types/orders
        def progress_callback(*args, **kwargs):
            try:
                if len(args) >= 2:
                    # Try to determine which is message and which is progress
                    arg1, arg2 = args[0], args[1]
                    
                    if isinstance(arg1, str) and isinstance(arg2, (int, float)):
                        # (message, progress_percent)
                        message, progress_percent = arg1, int(arg2)
                    elif isinstance(arg2, str) and isinstance(arg1, (int, float)):
                        # (progress_percent, message)
                        progress_percent, message = int(arg1), arg2
                    else:
                        # Default fallback
                        message = str(arg1)
                        progress_percent = 50  # Default middle progress
                else:
                    message = str(args[0]) if args else "분석 진행 중..."
                    progress_percent = 50
                
                # Convert percentage to step (progress_percent is 0-100)
                step = 3 + int(progress_percent / 50)  # Steps 3-4 for agent analysis
                if step > 4:
                    step = 4
                update_progress(step, 6, message)
                
            except Exception as e:
                # Fallback for any callback issues
                logger.debug(f"Progress callback error: {e}")
                update_progress(3, 6, "AI 분석 진행 중...")
        
        # Run the complete analysis with progress updates
        final_decision, agent_results, analysis_data, price_history = decision_system.make_decision(
            ticker=ticker,
            industry=industry,
            market=market,
            analysis_period=period,
            progress_callback=progress_callback
        )
        
        update_progress(5, 6, "분석 완료, 결과 정리 중...")
        
        # Check for errors
        if final_decision is None or "error" in analysis_data:
            error_msg = analysis_data.get("error", "알 수 없는 오류가 발생했습니다.")
            st.error(f"❌ 분석 실패: {error_msg}")
            st.session_state.analysis_started = False
            if progress_bar:
                progress_bar.empty()
            if status_text:
                status_text.empty()
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
        analysis_results = {
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
        
        st.session_state.analysis_results = analysis_results
        
        # Store technical visualization data if available
        if analysis_data and 'technical_viz_data' in analysis_data:
            st.session_state.last_technical_analysis = analysis_data['technical_viz_data']
        
        update_progress(6, 6, "완료!")
        
        # Clean up progress indicators
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()
        
        # Reset analysis started flag
        st.session_state.analysis_started = False
        
        # Success message
        st.success(f"🎉 {ticker.upper()} 분석이 완료되었습니다!")
        
        # Rerun to display results in main area
        st.rerun()
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
        
        # Clean up progress indicators
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()
            
        st.session_state.analysis_started = False


def display_results(
    results: dict, 
    layout_manager: CardLayoutManager,
    dashboard_manager: DashboardManager
):
    """Display analysis results using modern components."""
    try:
        # Get company name
        company_name = results['analysis_data'].get('stock_info', {}).get('longName', '')
        
        # Render header
        layout_manager.render_header(
            ticker=results['ticker'],
            market=results['market'],
            company_name=company_name
        )
        
        # Render decision card
        layout_manager.render_decision_card(results['final_decision'])
        
        # Render metrics row
        layout_manager.render_metrics_row(
            stock_info=results['analysis_data'].get('stock_info', {}),
            technical_data=results['analysis_data'].get('technical_analysis', {})
        )
        
        # Render dashboard
        dashboard_manager.render_analysis_dashboard(
            ticker=results['ticker'],
            analysis_data=results['analysis_data'],
            price_history=results['price_history'],
            agent_results=results['agent_results']
        )
        
        # Show timestamp
        timestamp = results.get('timestamp', datetime.now())
        st.markdown(f"""
        <div style="text-align: center; color: #6B7280; font-size: 0.875rem; margin-top: 2rem; padding: 1rem;">
            분석 완료: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}", exc_info=True)
        layout_manager.display_error(f"결과 표시 오류: {str(e)}")


def display_clean_modern_results(
    results: dict,
    clean_ui: CleanModernUI,
    stable_fetcher: StableFetcher
):
    """Display results using clean modern UI."""
    try:
        # Get real-time data
        ticker = results['ticker']
        realtime_data = stable_fetcher.fetch_quote(ticker)
        
        # Calculate price change
        current_price = realtime_data.get('currentPrice', 0)
        prev_close = realtime_data.get('previousClose', current_price)
        price_change = current_price - prev_close
        price_change_pct = ((price_change) / prev_close * 100) if prev_close else 0
        
        # Render header
        clean_ui.render_header(
            ticker=ticker,
            company_name=realtime_data.get('longName', ticker),
            price=current_price,
            change=price_change,
            change_pct=price_change_pct
        )
        
        # Render market indices
        try:
            indices = stable_fetcher.fetch_market_indices()
            if indices:
                clean_ui.render_market_indices(indices)
        except:
            pass
        
        # Render key metrics
        clean_ui.render_key_metrics(realtime_data)
        
        # Final decision
        if 'final_decision' in results:
            clean_ui.render_decision(results['final_decision'])
        
        # AI Analysis Results (가격 차트는 기술분석 탭에 포함)
        if 'agent_results' in results:
            price_history = results.get('price_history', pd.DataFrame())
            clean_ui.render_analysis_results(
                results['agent_results'], 
                price_history=price_history, 
                ticker=ticker
            )
            
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}", exc_info=True)
        st.error(f"Error occurred: {str(e)}")




if __name__ == "__main__":
    main()