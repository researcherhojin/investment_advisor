"""
Bloomberg Terminal Style UI

Professional, minimal design inspired by financial terminals.
Removes all AI-generated appearance and focuses on data clarity.
"""

import streamlit as st


class TerminalTheme:
    """Bloomberg Terminal inspired professional theme."""
    
    # Professional color palette - no gradients, no AI styling
    COLORS = {
        # Terminal colors
        'terminal_bg': '#000000',
        'terminal_text': '#00FF00',
        'terminal_orange': '#FF8500',
        'terminal_blue': '#0080FF',
        'terminal_yellow': '#FFFF00',
        
        # Professional grays
        'dark_bg': '#1E1E1E',
        'medium_bg': '#2D2D2D',
        'light_bg': '#3C3C3C',
        'border': '#404040',
        
        # Text colors
        'text_primary': '#FFFFFF',
        'text_secondary': '#CCCCCC',
        'text_muted': '#999999',
        
        # Status colors (simple, no gradients)
        'positive': '#00C851',
        'negative': '#FF4444',
        'neutral': '#33B5E5',
        'warning': '#FF8800',
        
        # Professional blues
        'primary': '#0066CC',
        'accent': '#0080FF',
    }
    
    @classmethod
    def inject_terminal_styles(cls):
        """Inject Bloomberg Terminal inspired CSS."""
        st.markdown(f"""
        <style>
        /* Remove all Streamlit default styling */
        .stApp {{
            background-color: {cls.COLORS['dark_bg']};
            color: {cls.COLORS['text_primary']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        
        /* Hide Streamlit branding completely */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{visibility: hidden;}}
        
        /* Remove default padding and margins */
        .main .block-container {{
            padding: 0rem 1rem 0rem 1rem;
            max-width: none;
        }}
        
        /* Terminal Header */
        .terminal-header {{
            background-color: {cls.COLORS['terminal_bg']};
            color: {cls.COLORS['terminal_text']};
            padding: 8px 16px;
            font-family: 'Consolas', monospace;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid {cls.COLORS['terminal_text']};
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Data Grid Styling */
        .data-grid {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }}
        
        .data-row {{
            padding: 4px 8px;
            border-bottom: 1px solid {cls.COLORS['border']};
            display: flex;
            justify-content: space-between;
        }}
        
        .data-row:nth-child(even) {{
            background-color: {cls.COLORS['light_bg']};
        }}
        
        .data-label {{
            color: {cls.COLORS['text_secondary']};
            min-width: 120px;
        }}
        
        .data-value {{
            color: {cls.COLORS['text_primary']};
            font-weight: bold;
            text-align: right;
        }}
        
        .data-value.positive {{
            color: {cls.COLORS['positive']};
        }}
        
        .data-value.negative {{
            color: {cls.COLORS['negative']};
        }}
        
        /* Terminal Input Box */
        .terminal-input {{
            background-color: {cls.COLORS['terminal_bg']};
            color: {cls.COLORS['terminal_text']};
            border: 1px solid {cls.COLORS['terminal_text']};
            padding: 8px;
            font-family: 'Consolas', monospace;
            font-size: 14px;
            width: 100%;
        }}
        
        /* Professional Buttons */
        .terminal-button {{
            background-color: {cls.COLORS['medium_bg']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            padding: 8px 16px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .terminal-button:hover {{
            background-color: {cls.COLORS['light_bg']};
            border-color: {cls.COLORS['accent']};
        }}
        
        .terminal-button.primary {{
            background-color: {cls.COLORS['primary']};
            border-color: {cls.COLORS['primary']};
        }}
        
        /* Status Indicators */
        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-indicator.positive {{ background-color: {cls.COLORS['positive']}; }}
        .status-indicator.negative {{ background-color: {cls.COLORS['negative']}; }}
        .status-indicator.neutral {{ background-color: {cls.COLORS['neutral']}; }}
        .status-indicator.warning {{ background-color: {cls.COLORS['warning']}; }}
        
        /* Override Streamlit components */
        .stSelectbox > div > div {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
            color: {cls.COLORS['text_primary']};
        }}
        
        .stTextInput > div > div > input {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
            color: {cls.COLORS['text_primary']};
            font-family: 'Consolas', monospace;
        }}
        
        .stButton > button {{
            background-color: {cls.COLORS['medium_bg']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            font-family: 'Consolas', monospace;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stButton > button:hover {{
            background-color: {cls.COLORS['primary']};
            border-color: {cls.COLORS['primary']};
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: {cls.COLORS['medium_bg']};
            border-right: 1px solid {cls.COLORS['border']};
        }}
        
        /* Remove default margins from markdown */
        .stMarkdown {{
            padding: 0;
        }}
        
        /* Table styling */
        .stDataFrame {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
        }}
        
        .stDataFrame table {{
            color: {cls.COLORS['text_primary']};
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }}
        
        /* Metrics styling */
        .stMetric {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
            padding: 8px;
        }}
        
        .stMetric label {{
            color: {cls.COLORS['text_secondary']};
            font-family: 'Consolas', monospace;
            font-size: 11px;
            text-transform: uppercase;
        }}
        
        .stMetric div[data-testid="metric-value"] {{
            color: {cls.COLORS['text_primary']};
            font-family: 'Consolas', monospace;
            font-size: 18px;
            font-weight: bold;
        }}
        
        /* Alert styling */
        .stAlert {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Progress bar */
        .stProgress > div > div > div > div {{
            background-color: {cls.COLORS['positive']};
        }}
        
        /* Charts - minimal styling */
        .js-plotly-plot {{
            background-color: {cls.COLORS['medium_bg']};
        }}
        
        /* Terminal Title Bar */
        .terminal-title {{
            background-color: {cls.COLORS['terminal_bg']};
            color: {cls.COLORS['terminal_orange']};
            padding: 4px 8px;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid {cls.COLORS['terminal_orange']};
        }}
        
        /* Analysis Section */
        .analysis-section {{
            background-color: {cls.COLORS['medium_bg']};
            border: 1px solid {cls.COLORS['border']};
            margin: 8px 0;
        }}
        
        .analysis-header {{
            background-color: {cls.COLORS['light_bg']};
            color: {cls.COLORS['terminal_blue']};
            padding: 6px 12px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            border-bottom: 1px solid {cls.COLORS['border']};
        }}
        
        .analysis-content {{
            padding: 12px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            line-height: 1.4;
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Ticker Display */
        .ticker-display {{
            background-color: {cls.COLORS['terminal_bg']};
            color: {cls.COLORS['terminal_yellow']};
            padding: 12px 16px;
            font-family: 'Consolas', monospace;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            border: 2px solid {cls.COLORS['terminal_yellow']};
            margin: 16px 0;
            letter-spacing: 2px;
        }}
        
        /* Remove any animations or transitions */
        * {{
            transition: none !important;
            animation: none !important;
        }}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {cls.COLORS['dark_bg']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {cls.COLORS['border']};
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {cls.COLORS['text_muted']};
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_terminal_header(cls, title: str):
        """Create Bloomberg Terminal style header."""
        st.markdown(f"""
        <div class="terminal-header">
            BLOOMBERG PROFESSIONAL - {title.upper()}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_ticker_display(cls, ticker: str, company_name: str = ""):
        """Create prominent ticker display."""
        display_text = ticker
        if company_name:
            display_text += f" - {company_name[:20]}"
        
        st.markdown(f"""
        <div class="ticker-display">
            {display_text}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_data_grid(cls, data_dict: dict, title: str = ""):
        """Create terminal-style data grid."""
        if title:
            st.markdown(f"""
            <div class="terminal-title">{title}</div>
            """, unsafe_allow_html=True)
        
        grid_html = '<div class="data-grid">'
        
        for label, value in data_dict.items():
            # Determine value class based on content
            value_class = "data-value"
            if isinstance(value, str):
                if "%" in value and value.replace("%", "").replace("-", "").replace(".", "").isdigit():
                    if value.startswith("-"):
                        value_class += " negative"
                    else:
                        value_class += " positive"
            
            grid_html += f"""
            <div class="data-row">
                <span class="data-label">{label}</span>
                <span class="{value_class}">{value}</span>
            </div>
            """
        
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
    
    @classmethod
    def create_analysis_section(cls, title: str, content: str):
        """Create professional analysis section."""
        st.markdown(f"""
        <div class="analysis-section">
            <div class="analysis-header">{title}</div>
            <div class="analysis-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_status_indicator(cls, status: str, label: str):
        """Create simple status indicator."""
        status_class = {
            "positive": "positive",
            "negative": "negative", 
            "neutral": "neutral",
            "warning": "warning"
        }.get(status, "neutral")
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 4px 0;">
            <span class="status-indicator {status_class}"></span>
            <span style="font-family: 'Consolas', monospace; font-size: 12px;">{label}</span>
        </div>
        """, unsafe_allow_html=True)