"""
Clean Professional UI Theme

Ultra-minimal, clean design with excellent typography and spacing.
Focuses on clarity, readability, and professional appearance.
"""

import streamlit as st


class CleanTheme:
    """Clean professional theme with excellent UX."""
    
    # Clean, professional color palette
    COLORS = {
        # Main backgrounds
        'app_bg': '#FAFBFC',
        'content_bg': '#FFFFFF', 
        'card_bg': '#FFFFFF',
        'sidebar_bg': '#F8F9FA',
        
        # Text colors
        'text_primary': '#2D3748',
        'text_secondary': '#4A5568',
        'text_muted': '#718096',
        'text_light': '#A0AEC0',
        
        # Brand colors (subtle)
        'primary': '#3182CE',
        'primary_light': '#EBF8FF',
        'success': '#38A169',
        'success_light': '#F0FFF4',
        'warning': '#D69E2E',
        'warning_light': '#FFFBEB',
        'danger': '#E53E3E',
        'danger_light': '#FED7D7',
        
        # Borders and dividers
        'border': '#E2E8F0',
        'border_light': '#F7FAFC',
        'divider': '#EDF2F7',
        
        # Interactive states
        'hover': '#F7FAFC',
        'active': '#EDF2F7',
    }
    
    @classmethod
    def inject_clean_styles(cls):
        """Inject clean professional CSS."""
        st.markdown(f"""
        <style>
        /* Import clean typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Base application styles */
        .stApp {{
            background-color: {cls.COLORS['app_bg']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: {cls.COLORS['text_primary']};
            font-size: 14px;
            line-height: 1.6;
        }}
        
        /* Hide Streamlit elements */
        #MainMenu, footer, header, .stDeployButton {{
            visibility: hidden;
        }}
        
        /* Main container */
        .main .block-container {{
            padding: 1.5rem 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Header styling */
        .app-header {{
            background: {cls.COLORS['content_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .app-title {{
            font-size: 2rem;
            font-weight: 700;
            color: {cls.COLORS['text_primary']};
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
        }}
        
        .app-subtitle {{
            font-size: 1rem;
            color: {cls.COLORS['text_secondary']};
            margin: 0;
            font-weight: 400;
        }}
        
        /* Sidebar improvements */
        .css-1d391kg {{
            background-color: {cls.COLORS['sidebar_bg']};
            border-right: 1px solid {cls.COLORS['border']};
            padding: 1.5rem 1rem;
        }}
        
        /* Form elements */
        .stSelectbox > div > div {{
            background-color: {cls.COLORS['content_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            font-size: 14px;
        }}
        
        .stTextInput > div > div > input {{
            background-color: {cls.COLORS['content_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            font-size: 14px;
            padding: 0.75rem;
        }}
        
        .stButton > button {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            padding: 0.75rem 1.5rem;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background-color: #2C5282;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(49, 130, 206, 0.3);
        }}
        
        /* Clean cards */
        .clean-card {{
            background: {cls.COLORS['card_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }}
        
        .clean-card:hover {{
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid {cls.COLORS['border_light']};
        }}
        
        .card-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin: 0;
        }}
        
        .card-content {{
            font-size: 14px;
            line-height: 1.7;
            color: {cls.COLORS['text_secondary']};
        }}
        
        /* Status badges */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.375rem 0.875rem;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .status-badge.buy {{
            background-color: {cls.COLORS['success_light']};
            color: {cls.COLORS['success']};
            border: 1px solid rgba(56, 161, 105, 0.2);
        }}
        
        .status-badge.sell {{
            background-color: {cls.COLORS['danger_light']};
            color: {cls.COLORS['danger']};
            border: 1px solid rgba(229, 62, 62, 0.2);
        }}
        
        .status-badge.hold {{
            background-color: {cls.COLORS['warning_light']};
            color: {cls.COLORS['warning']};
            border: 1px solid rgba(214, 158, 46, 0.2);
        }}
        
        /* Ticker display */
        .ticker-display {{
            background: linear-gradient(135deg, {cls.COLORS['primary_light']} 0%, {cls.COLORS['content_bg']} 100%);
            border: 2px solid {cls.COLORS['primary']};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin: 1.5rem 0;
        }}
        
        .ticker-symbol {{
            font-size: 2.5rem;
            font-weight: 800;
            color: {cls.COLORS['primary']};
            margin: 0;
            letter-spacing: -0.02em;
        }}
        
        .ticker-name {{
            font-size: 1rem;
            color: {cls.COLORS['text_secondary']};
            margin: 0.5rem 0 0 0;
            font-weight: 500;
        }}
        
        /* Data table */
        .data-table {{
            background: {cls.COLORS['content_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .table-header {{
            background: {cls.COLORS['sidebar_bg']};
            padding: 1rem 1.25rem;
            border-bottom: 1px solid {cls.COLORS['border']};
        }}
        
        .table-title {{
            font-size: 0.875rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 0;
        }}
        
        .table-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.875rem 1.25rem;
            border-bottom: 1px solid {cls.COLORS['border_light']};
            transition: background-color 0.15s ease;
        }}
        
        .table-row:last-child {{
            border-bottom: none;
        }}
        
        .table-row:hover {{
            background-color: {cls.COLORS['hover']};
        }}
        
        .table-label {{
            font-size: 14px;
            color: {cls.COLORS['text_secondary']};
            font-weight: 500;
        }}
        
        .table-value {{
            font-size: 14px;
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        .table-value.positive {{
            color: {cls.COLORS['success']};
        }}
        
        .table-value.negative {{
            color: {cls.COLORS['danger']};
        }}
        
        /* Welcome section */
        .welcome-section {{
            text-align: center;
            padding: 4rem 2rem;
        }}
        
        .welcome-title {{
            font-size: 1.75rem;
            font-weight: 400;
            color: {cls.COLORS['text_muted']};
            margin-bottom: 1rem;
        }}
        
        .welcome-subtitle {{
            font-size: 1.125rem;
            color: {cls.COLORS['text_light']};
            font-weight: 400;
        }}
        
        /* Feature cards */
        .feature-card {{
            background: {cls.COLORS['content_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            height: 100%;
            transition: all 0.2s ease;
        }}
        
        .feature-card:hover {{
            border-color: {cls.COLORS['primary']};
            box-shadow: 0 4px 12px rgba(49, 130, 206, 0.1);
        }}
        
        .feature-title {{
            font-size: 1rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin-bottom: 0.75rem;
        }}
        
        .feature-description {{
            font-size: 14px;
            color: {cls.COLORS['text_secondary']};
            line-height: 1.6;
        }}
        
        /* Alerts */
        .alert {{
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .alert.success {{
            background-color: {cls.COLORS['success_light']};
            color: {cls.COLORS['success']};
            border: 1px solid rgba(56, 161, 105, 0.2);
        }}
        
        .alert.error {{
            background-color: {cls.COLORS['danger_light']};
            color: {cls.COLORS['danger']};
            border: 1px solid rgba(229, 62, 62, 0.2);
        }}
        
        .alert.warning {{
            background-color: {cls.COLORS['warning_light']};
            color: {cls.COLORS['warning']};
            border: 1px solid rgba(214, 158, 46, 0.2);
        }}
        
        /* Tab improvements */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: {cls.COLORS['sidebar_bg']};
            padding: 4px;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 6px;
            color: {cls.COLORS['text_secondary']};
            font-weight: 500;
            padding: 0.75rem 1rem;
            border: none;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {cls.COLORS['content_bg']};
            color: {cls.COLORS['text_primary']};
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        /* Chart container */
        .chart-container {{
            background: {cls.COLORS['content_bg']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }}
        
        .chart-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin-bottom: 1rem;
            text-align: center;
        }}
        
        /* Remove default animations */
        * {{
            transition: none !important;
            animation: none !important;
        }}
        
        /* Re-enable smooth transitions for interactive elements */
        .clean-card, .feature-card, .table-row, .status-badge, .stButton > button {{
            transition: all 0.2s ease !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_header(cls, title: str, subtitle: str = ""):
        """Create clean application header."""
        subtitle_html = f'<p class="app-subtitle">{subtitle}</p>' if subtitle else ''
        
        st.markdown(f"""
        <div class="app-header">
            <h1 class="app-title">{title}</h1>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_ticker_display(cls, ticker: str, company_name: str = ""):
        """Create prominent ticker display."""
        name_html = f'<p class="ticker-name">{company_name}</p>' if company_name else ''
        
        st.markdown(f"""
        <div class="ticker-display">
            <h2 class="ticker-symbol">{ticker}</h2>
            {name_html}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_data_table(cls, data_dict: dict, title: str = ""):
        """Create clean data table."""
        header_html = f'<div class="table-header"><h3 class="table-title">{title}</h3></div>' if title else ''
        
        rows_html = ""
        for label, value in data_dict.items():
            # Determine value class
            value_class = "table-value"
            if isinstance(value, str) and "%" in value:
                if value.startswith("-"):
                    value_class += " negative"
                elif not value.startswith("0"):
                    value_class += " positive"
            
            rows_html += f"""
            <div class="table-row">
                <span class="table-label">{label}</span>
                <span class="{value_class}">{value}</span>
            </div>
            """
        
        st.markdown(f"""
        <div class="data-table">
            {header_html}
            {rows_html}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_alert(cls, message: str, alert_type: str = "info"):
        """Create clean alert."""
        st.markdown(f"""
        <div class="alert {alert_type}">
            {message}
        </div>
        """, unsafe_allow_html=True)