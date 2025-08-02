"""
Modern Minimal UI Theme

Clean, contemporary design with subtle visual elements.
Focuses on readability, whitespace, and modern typography.
"""

import streamlit as st


class ModernTheme:
    """Modern minimal theme with clean design principles."""
    
    # Modern color palette - clean and contemporary
    COLORS = {
        # Background colors
        'primary_bg': '#FFFFFF',
        'secondary_bg': '#F8F9FA',
        'card_bg': '#FFFFFF',
        'hover_bg': '#F5F5F5',
        
        # Text colors
        'text_primary': '#1A1A1A',
        'text_secondary': '#6C757D',
        'text_muted': '#ADB5BD',
        
        # Accent colors (subtle and modern)
        'accent_blue': '#007BFF',
        'accent_green': '#28A745',
        'accent_red': '#DC3545',
        'accent_orange': '#FD7E14',
        'accent_purple': '#6F42C1',
        
        # Borders and dividers
        'border_light': '#E9ECEF',
        'border_medium': '#DEE2E6',
        'border_strong': '#CED4DA',
        
        # Status colors (modern and subtle)
        'success': '#28A745',
        'warning': '#FFC107',
        'danger': '#DC3545',
        'info': '#17A2B8',
        
        # Gradients (very subtle)
        'gradient_light': 'linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%)',
        'gradient_blue': 'linear-gradient(135deg, #007BFF 0%, #0056B3 100%)',
    }
    
    @classmethod
    def inject_modern_styles(cls):
        """Inject modern minimal CSS styles."""
        st.markdown(f"""
        <style>
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Reset and base styles */
        .stApp {{
            background-color: {cls.COLORS['secondary_bg']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: {cls.COLORS['text_primary']};
            line-height: 1.6;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{visibility: hidden;}}
        
        /* Container and layout */
        .main .block-container {{
            padding: 2rem 1rem;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Modern header */
        .modern-header {{
            background: {cls.COLORS['primary_bg']};
            padding: 1.5rem 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            margin-bottom: 2rem;
            border: 1px solid {cls.COLORS['border_light']};
        }}
        
        .header-title {{
            font-size: 1.75rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin: 0;
            letter-spacing: -0.025em;
        }}
        
        .header-subtitle {{
            font-size: 0.95rem;
            color: {cls.COLORS['text_secondary']};
            margin: 0.25rem 0 0 0;
            font-weight: 400;
        }}
        
        /* Modern cards */
        .modern-card {{
            background: {cls.COLORS['card_bg']};
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid {cls.COLORS['border_light']};
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: box-shadow 0.2s ease;
        }}
        
        .modern-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .card-title {{
            font-size: 1rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin: 0 0 0.75rem 0;
            letter-spacing: -0.01em;
        }}
        
        .card-content {{
            font-size: 0.9rem;
            color: {cls.COLORS['text_secondary']};
            line-height: 1.6;
        }}
        
        /* Modern data grid */
        .data-grid {{
            background: {cls.COLORS['card_bg']};
            border-radius: 8px;
            border: 1px solid {cls.COLORS['border_light']};
            overflow: hidden;
        }}
        
        .grid-header {{
            background: {cls.COLORS['secondary_bg']};
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid {cls.COLORS['border_light']};
        }}
        
        .grid-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid {cls.COLORS['border_light']};
            font-size: 0.9rem;
        }}
        
        .grid-row:last-child {{
            border-bottom: none;
        }}
        
        .grid-row:hover {{
            background: {cls.COLORS['hover_bg']};
        }}
        
        .grid-label {{
            color: {cls.COLORS['text_secondary']};
            font-weight: 500;
        }}
        
        .grid-value {{
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
        }}
        
        .grid-value.positive {{
            color: {cls.COLORS['success']};
        }}
        
        .grid-value.negative {{
            color: {cls.COLORS['danger']};
        }}
        
        /* Modern ticker display */
        .ticker-display {{
            background: {cls.COLORS['card_bg']};
            border: 2px solid {cls.COLORS['accent_blue']};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            text-align: center;
            margin: 1.5rem 0;
        }}
        
        .ticker-symbol {{
            font-size: 2rem;
            font-weight: 700;
            color: {cls.COLORS['accent_blue']};
            margin: 0;
            letter-spacing: -0.02em;
        }}
        
        .ticker-name {{
            font-size: 0.95rem;
            color: {cls.COLORS['text_secondary']};
            margin: 0.25rem 0 0 0;
            font-weight: 500;
        }}
        
        /* Status indicators */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .status-badge.buy {{
            background: rgba(40, 167, 69, 0.1);
            color: {cls.COLORS['success']};
            border: 1px solid rgba(40, 167, 69, 0.2);
        }}
        
        .status-badge.sell {{
            background: rgba(220, 53, 69, 0.1);
            color: {cls.COLORS['danger']};
            border: 1px solid rgba(220, 53, 69, 0.2);
        }}
        
        .status-badge.hold {{
            background: rgba(108, 117, 125, 0.1);
            color: {cls.COLORS['text_secondary']};
            border: 1px solid rgba(108, 117, 125, 0.2);
        }}
        
        /* Modern buttons and inputs */
        .stButton > button {{
            background: {cls.COLORS['primary_bg']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border_medium']};
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: {cls.COLORS['accent_blue']};
            color: white;
            border-color: {cls.COLORS['accent_blue']};
            box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
        }}
        
        .stButton > button[kind="primary"] {{
            background: {cls.COLORS['accent_blue']};
            color: white;
            border-color: {cls.COLORS['accent_blue']};
        }}
        
        .stSelectbox > div > div {{
            background: {cls.COLORS['primary_bg']};
            border: 1px solid {cls.COLORS['border_medium']};
            border-radius: 6px;
        }}
        
        .stTextInput > div > div > input {{
            background: {cls.COLORS['primary_bg']};
            border: 1px solid {cls.COLORS['border_medium']};
            border-radius: 6px;
            font-size: 0.9rem;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background: {cls.COLORS['primary_bg']};
            border-right: 1px solid {cls.COLORS['border_light']};
        }}
        
        /* Section dividers */
        .section-divider {{
            height: 1px;
            background: {cls.COLORS['border_light']};
            margin: 2rem 0;
        }}
        
        /* Modern alerts */
        .modern-alert {{
            padding: 1rem 1.25rem;
            border-radius: 6px;
            margin: 1rem 0;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        .modern-alert.success {{
            background: rgba(40, 167, 69, 0.1);
            color: {cls.COLORS['success']};
            border: 1px solid rgba(40, 167, 69, 0.2);
        }}
        
        .modern-alert.error {{
            background: rgba(220, 53, 69, 0.1);
            color: {cls.COLORS['danger']};
            border: 1px solid rgba(220, 53, 69, 0.2);
        }}
        
        .modern-alert.warning {{
            background: rgba(255, 193, 7, 0.1);
            color: #856404;
            border: 1px solid rgba(255, 193, 7, 0.2);
        }}
        
        /* Typography improvements */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            line-height: 1.4;
            letter-spacing: -0.025em;
        }}
        
        /* Chart container */
        .chart-container {{
            background: {cls.COLORS['card_bg']};
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid {cls.COLORS['border_light']};
            margin: 1rem 0;
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: {cls.COLORS['secondary_bg']};
            border-radius: 6px 6px 0 0;
            border: 1px solid {cls.COLORS['border_light']};
            color: {cls.COLORS['text_secondary']};
            font-weight: 500;
            padding: 0.5rem 1rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {cls.COLORS['primary_bg']};
            color: {cls.COLORS['text_primary']};
            border-bottom-color: {cls.COLORS['primary_bg']};
        }}
        
        /* Remove animations for cleaner feel */
        * {{
            transition: none !important;
            animation: none !important;
        }}
        
        /* Re-enable subtle transitions for interactive elements */
        .modern-card, .stButton > button, .grid-row {{
            transition: all 0.2s ease !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_header(cls, title: str, subtitle: str = ""):
        """Create modern header."""
        subtitle_html = f'<p class="header-subtitle">{subtitle}</p>' if subtitle else ''
        
        st.markdown(f"""
        <div class="modern-header">
            <h1 class="header-title">{title}</h1>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_ticker_display(cls, ticker: str, company_name: str = ""):
        """Create modern ticker display."""
        name_html = f'<p class="ticker-name">{company_name}</p>' if company_name else ''
        
        st.markdown(f"""
        <div class="ticker-display">
            <h2 class="ticker-symbol">{ticker}</h2>
            {name_html}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_card(cls, title: str, content: str, status: str = ""):
        """Create modern card with optional status."""
        status_badge = ""
        if status:
            status_class = status.lower()
            status_badge = f'<span class="status-badge {status_class}">{status}</span>'
        
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h3 class="card-title">{title}</h3>
                {status_badge}
            </div>
            <div class="card-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_data_grid(cls, data_dict: dict, title: str = ""):
        """Create modern data grid."""
        header_html = f'<div class="grid-header">{title}</div>' if title else ''
        
        rows_html = ""
        for label, value in data_dict.items():
            # Determine value class
            value_class = "grid-value"
            if isinstance(value, str) and "%" in value:
                if value.startswith("-"):
                    value_class += " negative"
                elif not value.startswith("0"):
                    value_class += " positive"
            
            rows_html += f"""
            <div class="grid-row">
                <span class="grid-label">{label}</span>
                <span class="{value_class}">{value}</span>
            </div>
            """
        
        st.markdown(f"""
        <div class="data-grid">
            {header_html}
            {rows_html}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_alert(cls, message: str, alert_type: str = "info"):
        """Create modern alert."""
        st.markdown(f"""
        <div class="modern-alert {alert_type}">
            {message}
        </div>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_section_divider(cls):
        """Create subtle section divider."""
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)