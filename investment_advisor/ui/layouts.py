"""
Layout Management Module

Manages Streamlit UI layouts and page structure.
"""

import logging
from typing import Dict, Any, Optional, List
import streamlit as st
from datetime import datetime

from ..utils import get_config, InputValidator

logger = logging.getLogger(__name__)


class LayoutManager:
    """Manage Streamlit UI layouts and interactions."""
    
    def __init__(self):
        self.config = get_config()
        self.validator = InputValidator()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'market' not in st.session_state:
            st.session_state.market = self.config.default_market
        
        if 'analysis_started' not in st.session_state:
            st.session_state.analysis_started = False
        
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        
        if 'selected_tab' not in st.session_state:
            st.session_state.selected_tab = 0
    
    def setup_page(self):
        """Set up the Streamlit page configuration."""
        # Page config is now set in main.py before any imports
        # Only inject custom CSS here
        self._inject_custom_css()
    
    def render_header(self):
        """Render the application header."""
        st.title(self.config.app_title)
        st.markdown("---")
        
        # Display market status
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**다양한 AI 전문가의 종합적인 투자 분석**")
        
        with col2:
            market_open = self.validator.is_market_hours(st.session_state.market)
            status = "🟢 장 운영중" if market_open else "🔴 장 마감"
            st.markdown(f"**{status}**")
        
        with col3:
            st.markdown(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')}**")
    
    def render_sidebar(self) -> Dict[str, Any]:
        """
        Render the sidebar and return user inputs.
        
        Returns:
            Dictionary with user inputs
        """
        with st.sidebar:
            st.header("📊 분석 설정")
            
            # Market selection
            market = self._render_market_selection()
            
            # Ticker input
            ticker = self._render_ticker_input(market)
            
            # Industry selection
            industry = self._render_industry_selection()
            
            # Analysis period
            period = self._render_period_selection()
            
            # Advanced options
            advanced_options = self._render_advanced_options()
            
            # Action buttons
            actions = self._render_action_buttons()
            
            # Info section
            self._render_info_section(market)
            
            return {
                'market': market,
                'ticker': ticker,
                'industry': industry,
                'period': period,
                'advanced': advanced_options,
                'actions': actions
            }
    
    def render_main_content(self, analysis_results: Optional[Dict[str, Any]] = None):
        """Render the main content area."""
        if analysis_results is None and st.session_state.analysis_results is None:
            self._render_welcome_screen()
        else:
            self._render_analysis_results(
                analysis_results or st.session_state.analysis_results
            )
    
    def render_tabs(self, tab_names: List[str]) -> str:
        """
        Render tabs and return selected tab.
        
        Args:
            tab_names: List of tab names
            
        Returns:
            Selected tab name
        """
        tabs = st.tabs(tab_names)
        return tabs
    
    def display_progress(self, message: str, progress: float):
        """Display progress during analysis."""
        progress_bar = st.progress(progress / 100)
        status_text = st.empty()
        status_text.text(message)
        
        return progress_bar, status_text
    
    def display_error(self, error_message: str):
        """Display error message."""
        st.error(f"❌ {error_message}")
        
        # Log error details if in debug mode
        if self.config.debug_mode:
            with st.expander("오류 상세 정보"):
                st.code(error_message)
    
    def display_success(self, message: str):
        """Display success message."""
        st.success(f"✅ {message}")
    
    def display_info(self, message: str):
        """Display info message."""
        st.info(f"ℹ️ {message}")
    
    def display_warning(self, message: str):
        """Display warning message."""
        st.warning(f"⚠️ {message}")
    
    # Private helper methods
    
    def _inject_custom_css(self):
        """Inject custom CSS for styling."""
        st.markdown("""
        <style>
        /* Custom button styles */
        .stButton > button {
            width: 100%;
            border-radius: 20px;
            height: 3em;
            transition: all 0.3s ease-in-out;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.2);
        }
        
        /* Market selection buttons */
        .market-button {
            background-color: #f0f2f6;
            color: #262730;
            border: 2px solid transparent;
        }
        
        .market-button.selected {
            background-color: #ff4b4b;
            color: white;
            border-color: #ff4b4b;
        }
        
        /* Info boxes */
        .custom-info {
            background-color: #e1f5fe;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #03a9f4;
        }
        
        /* Metric containers */
        [data-testid="metric-container"] {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            background-color: #f0f2f6;
            border-radius: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ff4b4b;
            color: white;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_market_selection(self) -> str:
        """Render market selection buttons."""
        st.markdown("### 시장 선택")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "🇺🇸 미국장",
                key="us_market_btn",
                help="미국 주식 시장 선택",
                disabled=st.session_state.analysis_started
            ):
                st.session_state.market = "미국장"
        
        with col2:
            if st.button(
                "🇰🇷 한국장",
                key="kr_market_btn",
                help="한국 주식 시장 선택",
                disabled=st.session_state.analysis_started
            ):
                st.session_state.market = "한국장"
        
        # Display selected market
        st.info(f"선택된 시장: **{st.session_state.market}**")
        
        return st.session_state.market
    
    def _render_ticker_input(self, market: str) -> str:
        """Render ticker input field."""
        st.markdown("### 종목 코드")
        
        # Market-specific placeholder
        if market == "미국장":
            placeholder = "예: AAPL, MSFT, GOOGL"
            help_text = "미국 주식 티커를 입력하세요 (1-5자리 영문)"
        else:
            placeholder = "예: 005930, 000660, 035720"
            help_text = "한국 주식 종목코드를 입력하세요 (6자리 숫자)"
        
        ticker = st.text_input(
            "티커 입력",
            placeholder=placeholder,
            help=help_text,
            key="ticker_input"
        )
        
        # Validate ticker
        if ticker:
            validation = self.validator.validate_ticker(ticker, market)
            if validation['valid']:
                st.success(validation['message'])
                return validation['normalized_ticker']
            else:
                st.error(validation['message'])
                return ""
        
        return ticker
    
    def _render_industry_selection(self) -> str:
        """Render industry selection."""
        st.markdown("### 산업 분류")
        
        industries = self.validator.VALID_INDUSTRIES
        
        industry = st.selectbox(
            "산업 선택",
            options=industries,
            help="해당 기업이 속한 산업을 선택하세요",
            key="industry_select"
        )
        
        return industry
    
    def _render_period_selection(self) -> int:
        """Render analysis period selection."""
        st.markdown("### 분석 기간")
        
        period = st.slider(
            "분석 기간 (개월)",
            min_value=1,
            max_value=60,
            value=self.config.default_analysis_period,
            step=1,
            help="과거 데이터 분석 기간을 선택하세요",
            key="period_slider"
        )
        
        st.caption(f"약 {period * 30}일간의 데이터를 분석합니다")
        
        return period
    
    def _render_advanced_options(self) -> Dict[str, Any]:
        """Render advanced options."""
        options = {}
        
        with st.expander("고급 옵션", expanded=False):
            # Risk tolerance
            options['risk_tolerance'] = st.select_slider(
                "위험 성향",
                options=["보수적", "중립적", "공격적"],
                value="중립적",
                help="투자 위험 성향을 선택하세요"
            )
            
            # Investment horizon
            options['investment_horizon'] = st.radio(
                "투자 기간",
                options=["단기 (1-3개월)", "중기 (3-12개월)", "장기 (1년 이상)"],
                index=1,
                help="예상 투자 기간을 선택하세요"
            )
            
            # Analysis depth
            options['analysis_depth'] = st.checkbox(
                "심층 분석 수행",
                value=False,
                help="더 자세한 분석을 수행합니다 (시간이 더 걸립니다)"
            )
            
            # Include recommendations
            options['include_recommendations'] = st.checkbox(
                "추천 종목 포함",
                value=True,
                help="유사 종목 및 추천 종목을 포함합니다"
            )
        
        return options
    
    def _render_action_buttons(self) -> Dict[str, bool]:
        """Render action buttons."""
        actions = {}
        
        st.markdown("---")
        
        # Main analysis button
        actions['analyze'] = st.button(
            "🔍 분석 시작",
            type="primary",
            use_container_width=True,
            key="analyze_btn"
        )
        
        # Secondary actions
        col1, col2 = st.columns(2)
        
        with col1:
            actions['reset'] = st.button(
                "🔄 초기화",
                use_container_width=True,
                key="reset_btn"
            )
        
        with col2:
            actions['export'] = st.button(
                "📥 내보내기",
                use_container_width=True,
                key="export_btn",
                disabled=st.session_state.analysis_results is None
            )
        
        return actions
    
    def _render_info_section(self, market: str):
        """Render information section."""
        with st.expander("ℹ️ 사용 방법", expanded=False):
            st.markdown(f"""
            1. **시장 선택**: {market} 선택됨
            2. **티커 입력**: 분석할 종목의 티커를 입력
            3. **산업 선택**: 해당 기업의 산업 분류 선택
            4. **분석 기간**: 과거 데이터 분석 기간 설정
            5. **분석 시작**: 버튼을 클릭하여 AI 분석 시작
            
            **팁**: 
            - 티커를 모르시면 [여기서 검색](https://finance.yahoo.com/lookup)
            - 장 운영 시간에 분석하면 실시간 데이터 반영
            - 고급 옵션에서 상세 설정 가능
            """)
        
        # Feature flags info
        if self.config.debug_mode:
            with st.expander("🔧 디버그 정보", expanded=False):
                st.json(self.config.to_dict())
    
    def _render_welcome_screen(self):
        """Render welcome screen when no analysis is active."""
        st.markdown("""
        ## 환영합니다! 👋
        
        AI 투자 자문 시스템은 여러 전문가 AI의 분석을 종합하여 
        종합적인 투자 인사이트를 제공합니다.
        
        ### 제공되는 분석:
        - 📊 **기술적 분석**: 차트 패턴, 지표, 추세 분석
        - 📈 **기본적 분석**: 재무제표, 가치평가, 성장성 분석
        - 🏢 **기업 분석**: 비즈니스 모델, 경쟁력, 전망
        - 🏭 **산업 분석**: 산업 동향, 성장 전망, 규제 환경
        - 🌍 **거시경제 분석**: 경제 지표, 시장 환경
        - ⚠️ **리스크 분석**: 투자 위험 요소 평가
        
        ### 시작하기:
        왼쪽 사이드바에서 분석할 종목을 선택하고 '분석 시작' 버튼을 클릭하세요.
        """)
        
        # Show sample tickers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🇺🇸 인기 미국 주식**
            - AAPL (Apple)
            - MSFT (Microsoft)
            - GOOGL (Google)
            - AMZN (Amazon)
            - TSLA (Tesla)
            """)
        
        with col2:
            st.markdown("""
            **🇰🇷 인기 한국 주식**
            - 005930 (삼성전자)
            - 000660 (SK하이닉스)
            - 035720 (카카오)
            - 035420 (네이버)
            - 207940 (삼성바이오로직스)
            """)
    
    def _render_analysis_results(self, results: Dict[str, Any]):
        """Render analysis results."""
        # This will be called from the main app
        # The actual rendering is handled by other UI components
        pass