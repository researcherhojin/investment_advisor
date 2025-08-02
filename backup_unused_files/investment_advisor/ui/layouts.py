"""
Layout Management Module

Manages Streamlit UI layouts and page structure with professional design.
"""

import logging
from typing import Dict, Any, Optional, List
import streamlit as st
from datetime import datetime

from ..utils import get_config, InputValidator
from .styles import ProfessionalTheme, ComponentStyles

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
        # Inject professional CSS theme
        ProfessionalTheme.inject_styles()
    
    def render_header(self):
        """Render the application header with professional design."""
        # Create professional header
        ProfessionalTheme.create_professional_header(
            self.config.app_title,
            "전문가급 AI 에이전트들의 종합적인 투자 분석 플랫폼"
        )
        
        # Display status indicators
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            market_open = self.validator.is_market_hours(st.session_state.market)
            if market_open:
                ComponentStyles.create_status_indicator("success", "장 운영중")
            else:
                ComponentStyles.create_status_indicator("error", "장 마감")
        
        with col2:
            ComponentStyles.create_status_indicator("info", f"현재 시장: {st.session_state.market}")
        
        with col3:
            ComponentStyles.create_status_indicator("info", datetime.now().strftime('%H:%M'))
    
    def render_sidebar(self) -> Dict[str, Any]:
        """
        Render the sidebar and return user inputs.
        
        Returns:
            Dictionary with user inputs
        """
        with st.sidebar:
            st.header("분석 설정")
            
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
        """Render market selection buttons with professional design."""
        st.markdown("### 시장 선택")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "미국 시장",
                key="us_market_btn",
                help="미국 주식 시장 분석",
                disabled=st.session_state.analysis_started,
                type="primary" if st.session_state.market == "미국장" else "secondary"
            ):
                st.session_state.market = "미국장"
        
        with col2:
            if st.button(
                "한국 시장",
                key="kr_market_btn", 
                help="한국 주식 시장 분석",
                disabled=st.session_state.analysis_started,
                type="primary" if st.session_state.market == "한국장" else "secondary"
            ):
                st.session_state.market = "한국장"
        
        # Display selected market with professional indicator
        ComponentStyles.create_status_indicator("info", f"선택된 시장: {st.session_state.market}")
        
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
            "분석 시작",
            type="primary",
            use_container_width=True,
            key="analyze_btn",
            help="AI 에이전트들이 종합적인 투자 분석을 수행합니다"
        )
        
        # Secondary actions
        col1, col2 = st.columns(2)
        
        with col1:
            actions['reset'] = st.button(
                "초기화",
                use_container_width=True,
                key="reset_btn",
                help="모든 설정을 초기 상태로 되돌립니다"
            )
        
        with col2:
            actions['export'] = st.button(
                "결과 내보내기",
                use_container_width=True,
                key="export_btn",
                disabled=st.session_state.analysis_results is None,
                help="분석 결과를 JSON 파일로 다운로드합니다"
            )
        
        return actions
    
    def _render_info_section(self, market: str):
        """Render information section."""
        with st.expander("사용 방법", expanded=False):
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
            with st.expander("시스템 정보", expanded=False):
                st.json(self.config.to_dict())
    
    def _render_welcome_screen(self):
        """Render welcome screen when no analysis is active."""
        # Professional welcome message
        st.markdown("""
        <div class="professional-info-box fade-in" style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #2C3E50; margin-bottom: 1rem;">전문가급 투자 분석을 시작하세요</h2>
            <p style="color: #7F8C8D; font-size: 1.1rem; line-height: 1.6;">
                5명의 전문 AI 에이전트가 실시간 데이터를 바탕으로<br>
                종합적인 투자 인사이트를 제공합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Analysis capabilities grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="professional-info-box slide-up">
                <h4 style="color: #2C3E50; margin-bottom: 1rem;">분석 영역</h4>
                <ul style="color: #7F8C8D; line-height: 1.8;">
                    <li><strong>기술적 분석</strong> - 차트 패턴 및 지표 분석</li>
                    <li><strong>기본적 분석</strong> - 재무제표 및 가치평가</li>
                    <li><strong>기업 분석</strong> - 비즈니스 모델 및 경쟁력</li>
                    <li><strong>산업 분석</strong> - 업계 동향 및 전망</li>
                    <li><strong>거시경제 분석</strong> - 시장 환경 평가</li>
                    <li><strong>리스크 분석</strong> - 투자 위험 요소</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="professional-info-box slide-up">
                <h4 style="color: #2C3E50; margin-bottom: 1rem;">지원 시장</h4>
                <div style="margin-bottom: 1.5rem;">
                    <h5 style="color: #667eea;">미국 시장</h5>
                    <p style="color: #7F8C8D; font-size: 0.9rem;">
                        AAPL, MSFT, GOOGL, AMZN, TSLA 등<br>
                        주요 상장 기업 분석 지원
                    </p>
                </div>
                <div>
                    <h5 style="color: #667eea;">한국 시장</h5>
                    <p style="color: #7F8C8D; font-size: 0.9rem;">
                        삼성전자, SK하이닉스, 카카오, 네이버 등<br>
                        코스피/코스닥 상장 기업 분석
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Getting started guide
        st.markdown("""
        <div class="professional-info-box fade-in" style="margin-top: 2rem;">
            <h4 style="color: #2C3E50; margin-bottom: 1rem;">분석 시작하기</h4>
            <div style="color: #7F8C8D; line-height: 1.6;">
                <strong>1단계:</strong> 사이드바에서 분석하고자 하는 시장을 선택하세요<br>
                <strong>2단계:</strong> 종목 코드나 티커를 입력하세요<br>
                <strong>3단계:</strong> 해당 기업의 산업 분류를 선택하세요<br>
                <strong>4단계:</strong> '분석 시작' 버튼을 클릭하여 전문가 분석을 받으세요
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_analysis_results(self, results: Dict[str, Any]):
        """Render analysis results."""
        # This will be called from the main app
        # The actual rendering is handled by other UI components
        pass