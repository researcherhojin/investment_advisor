"""
Professional UI Styles for Investment Advisor

Modern, minimal design with glassmorphism effects and professional gradients.
"""

import streamlit as st


class ProfessionalTheme:
    """Professional theme with glassmorphism and modern UI elements."""
    
    # Color palette
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent': '#4ECDC4',
        'success': '#26C6DA',
        'warning': '#FFB74D',
        'error': '#FF5722',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
        'background': '#F8FAFC',
        'surface': 'rgba(255, 255, 255, 0.9)',
        'glass': 'rgba(255, 255, 255, 0.1)',
        'glass_border': 'rgba(255, 255, 255, 0.2)',
    }
    
    @classmethod
    def inject_styles(cls):
        """Inject professional CSS styles."""
        st.markdown(f"""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Reset and base styles */
        .stApp {{
            background: linear-gradient(135deg, {cls.COLORS['primary']} 0%, {cls.COLORS['secondary']} 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Main container glassmorphism */
        .main .block-container {{
            background: {cls.COLORS['glass']};
            backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid {cls.COLORS['glass_border']};
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            padding: 2rem;
            margin-top: 2rem;
            max-width: 1200px;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background: {cls.COLORS['glass']};
            backdrop-filter: blur(20px);
            border-radius: 0 24px 24px 0;
            border: 1px solid {cls.COLORS['glass_border']};
        }}
        
        /* Headers */
        h1 {{
            color: white;
            font-weight: 700;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        h2 {{
            color: white;
            font-weight: 600;
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }}
        
        h3 {{
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
            font-size: 1.4rem;
            margin-bottom: 0.8rem;
        }}
        
        /* Custom buttons */
        .stButton > button {{
            background: linear-gradient(45deg, {cls.COLORS['accent']}, {cls.COLORS['success']});
            border: none;
            border-radius: 16px;
            color: white;
            font-weight: 600;
            font-size: 16px;
            padding: 12px 24px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px 0 rgba(78, 205, 196, 0.4);
            width: 100%;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 25px 0 rgba(78, 205, 196, 0.6);
            background: linear-gradient(45deg, {cls.COLORS['success']}, {cls.COLORS['accent']});
        }}
        
        .stButton > button:active {{
            transform: translateY(0) scale(0.98);
            box-shadow: 0 4px 15px 0 rgba(78, 205, 196, 0.4);
        }}
        
        /* Primary button styling */
        div[data-testid="stButton"] button[kind="primary"] {{
            background: linear-gradient(45deg, {cls.COLORS['primary']}, {cls.COLORS['secondary']});
            box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
        }}
        
        div[data-testid="stButton"] button[kind="primary"]:hover {{
            box-shadow: 0 8px 25px 0 rgba(102, 126, 234, 0.6);
        }}
        
        /* Market selection buttons */
        .market-btn {{
            background: {cls.COLORS['surface']};
            border: 2px solid {cls.COLORS['glass_border']};
            color: {cls.COLORS['text_primary']};
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .market-btn:hover {{
            background: {cls.COLORS['accent']};
            color: white;
            border-color: {cls.COLORS['accent']};
            transform: translateY(-2px);
        }}
        
        .market-btn.selected {{
            background: linear-gradient(45deg, {cls.COLORS['primary']}, {cls.COLORS['secondary']});
            color: white;
            border-color: {cls.COLORS['primary']};
        }}
        
        /* Advanced metric cards */
        [data-testid="metric-container"] {{
            background: {cls.COLORS['surface']};
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid {cls.COLORS['glass_border']};
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        [data-testid="metric-container"]:before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {cls.COLORS['accent']}, {cls.COLORS['success']});
        }}
        
        [data-testid="metric-container"]:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        }}
        
        [data-testid="metric-container"] [data-testid="metric-label"] {{
            color: {cls.COLORS['text_secondary']};
            font-weight: 500;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            color: {cls.COLORS['text_primary']};
            font-weight: 700;
            font-size: 2rem;
        }}
        
        /* Custom tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background: {cls.COLORS['glass']};
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 8px;
            border: 1px solid {cls.COLORS['glass_border']};
            gap: 4px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 12px;
            color: white;
            font-weight: 500;
            padding: 12px 20px;
            transition: all 0.3s ease;
            border: none;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            backdrop-filter: blur(20px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        /* Input fields */
        .stTextInput > div > div > input {{
            background: {cls.COLORS['surface']};
            border: 2px solid {cls.COLORS['glass_border']};
            border-radius: 12px;
            padding: 12px 16px;
            font-weight: 500;
            color: {cls.COLORS['text_primary']};
            transition: all 0.3s ease;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {cls.COLORS['accent']};
            box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
        }}
        
        /* Select boxes */
        .stSelectbox > div > div {{
            background: {cls.COLORS['surface']};
            border: 2px solid {cls.COLORS['glass_border']};
            border-radius: 12px;
        }}
        
        /* Sliders */
        .stSlider > div > div > div > div {{
            background: linear-gradient(90deg, {cls.COLORS['accent']}, {cls.COLORS['success']});
        }}
        
        .stSlider > div > div > div > div > div {{
            background: white;
            border: 3px solid {cls.COLORS['accent']};
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}
        
        /* Progress bars */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {cls.COLORS['accent']}, {cls.COLORS['success']});
            border-radius: 10px;
            height: 12px;
            animation: progressAnimation 2s ease-in-out;
        }}
        
        @keyframes progressAnimation {{
            0% {{ width: 0%; }}
            100% {{ width: var(--progress-width); }}
        }}
        
        /* Alert messages */
        .stAlert {{
            border-radius: 12px;
            border: none;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .stSuccess {{
            background: linear-gradient(45deg, rgba(38, 198, 218, 0.1), rgba(76, 175, 80, 0.1));
            border-left: 4px solid {cls.COLORS['success']};
        }}
        
        .stError {{
            background: linear-gradient(45deg, rgba(255, 87, 34, 0.1), rgba(244, 67, 54, 0.1));
            border-left: 4px solid {cls.COLORS['error']};
        }}
        
        .stWarning {{
            background: linear-gradient(45deg, rgba(255, 183, 77, 0.1), rgba(255, 152, 0, 0.1));
            border-left: 4px solid {cls.COLORS['warning']};
        }}
        
        .stInfo {{
            background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-left: 4px solid {cls.COLORS['primary']};
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: {cls.COLORS['surface']};
            border-radius: 12px;
            border: 1px solid {cls.COLORS['glass_border']};
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            transition: all 0.3s ease;
        }}
        
        .streamlit-expanderHeader:hover {{
            background: {cls.COLORS['glass']};
            transform: translateY(-1px);
        }}
        
        .streamlit-expanderContent {{
            background: {cls.COLORS['surface']};
            border-radius: 0 0 12px 12px;
            border: 1px solid {cls.COLORS['glass_border']};
            border-top: none;
        }}
        
        /* Sidebar specific styles */
        .css-1d391kg {{
            padding-top: 2rem;
        }}
        
        .css-1d391kg h2 {{
            color: white;
            text-align: center;
            font-weight: 600;
            margin-bottom: 2rem;
        }}
        
        .css-1d391kg h3 {{
            color: white;
            font-weight: 600;
            font-size: 1.1rem;
            margin: 1.5rem 0 0.5rem 0;
        }}
        
        /* Data tables */
        .stDataFrame {{
            background: {cls.COLORS['surface']};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid {cls.COLORS['glass_border']};
        }}
        
        /* Charts container */
        .js-plotly-plot {{
            background: {cls.COLORS['surface']};
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid {cls.COLORS['glass_border']};
            overflow: hidden;
        }}
        
        /* Custom info boxes */
        .professional-info-box {{
            background: {cls.COLORS['surface']};
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid {cls.COLORS['glass_border']};
            margin: 16px 0;
            position: relative;
        }}
        
        .professional-info-box:before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {cls.COLORS['primary']}, {cls.COLORS['secondary']});
            border-radius: 16px 16px 0 0;
        }}
        
        .professional-info-box h4 {{
            color: {cls.COLORS['text_primary']};
            margin: 0 0 12px 0;
            font-weight: 600;
        }}
        
        .professional-info-box p {{
            color: {cls.COLORS['text_secondary']};
            margin: 0;
            line-height: 1.6;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Loading spinner */
        .stSpinner > div {{
            border-top-color: {cls.COLORS['accent']};
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem;
                margin-top: 1rem;
                border-radius: 16px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .stButton > button {{
                padding: 10px 20px;
                font-size: 14px;
            }}
            
            [data-testid="metric-container"] {{
                padding: 16px;
            }}
        }}
        
        /* Animation utilities */
        .fade-in {{
            animation: fadeIn 0.6s ease-in-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .slide-up {{
            animation: slideUp 0.5s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(30px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @classmethod
    def create_professional_header(cls, title: str, subtitle: str = None):
        """Create a professional header with glassmorphism effect."""
        header_html = f"""
        <div class="professional-info-box fade-in" style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: {cls.COLORS['text_primary']}; margin-bottom: 0.5rem; font-size: 2.5rem;">
                {title}
            </h1>
        """
        
        if subtitle:
            header_html += f"""
            <p style="color: {cls.COLORS['text_secondary']}; font-size: 1.1rem; margin: 0;">
                {subtitle}
            </p>
            """
        
        header_html += """
        </div>
        """
        
        st.markdown(header_html, unsafe_allow_html=True)
    
    @classmethod
    def create_metric_card(cls, title: str, value: str, delta: str = None, icon: str = None):
        """Create a professional metric card."""
        delta_html = ""
        if delta:
            delta_color = cls.COLORS['success'] if delta.startswith("+") else cls.COLORS['error']
            delta_html = f"""
            <div style="color: {delta_color}; font-size: 14px; font-weight: 600; margin-top: 8px;">
                {delta}
            </div>
            """
        
        icon_html = ""
        if icon:
            icon_html = f"""
            <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
            """
        
        card_html = f"""
        <div class="professional-info-box slide-up" style="text-align: center;">
            {icon_html}
            <h4 style="margin-bottom: 12px; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">
                {title}
            </h4>
            <div style="font-size: 2rem; font-weight: 700; color: {cls.COLORS['text_primary']};">
                {value}
            </div>
            {delta_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    @classmethod
    def create_analysis_card(cls, title: str, content: str, agent_type: str = ""):
        """Create a professional analysis card for AI agent results."""
        # Choose icon based on agent type
        icons = {
            "기업분석가": "🏢",
            "산업전문가": "🏭", 
            "거시경제전문가": "🌍",
            "기술분석가": "📊",
            "리스크관리자": "⚠️"
        }
        
        icon = icons.get(agent_type, "🤖")
        
        card_html = f"""
        <div class="professional-info-box fade-in">
            <div style="display: flex; align-items: center; margin-bottom: 16px;">
                <div style="font-size: 24px; margin-right: 12px;">{icon}</div>
                <h4 style="margin: 0; color: {cls.COLORS['text_primary']};">{title}</h4>
            </div>
            <div style="color: {cls.COLORS['text_secondary']}; line-height: 1.6;">
                {content}
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)


class ComponentStyles:
    """Reusable UI component styles."""
    
    @staticmethod
    def create_status_indicator(status: str, label: str):
        """Create a status indicator."""
        colors = {
            "success": "#26C6DA",
            "warning": "#FFB74D", 
            "error": "#FF5722",
            "info": "#667eea"
        }
        
        color = colors.get(status, colors["info"])
        
        indicator_html = f"""
        <div style="
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 16px;
            border-radius: 20px;
            border-left: 4px solid {color};
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 4px;
        ">
            <div style="
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: {color};
                margin-right: 8px;
            "></div>
            <span style="font-weight: 500; color: #2C3E50;">{label}</span>
        </div>
        """
        
        st.markdown(indicator_html, unsafe_allow_html=True)
    
    @staticmethod
    def create_progress_ring(percentage: float, label: str):
        """Create a progress ring component."""
        # Calculate circumference and offset
        radius = 45
        circumference = 2 * 3.14159 * radius
        offset = circumference - (percentage / 100) * circumference
        
        ring_html = f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin: 20px;">
            <svg width="120" height="120" style="transform: rotate(-90deg);">
                <circle 
                    cx="60" cy="60" r="{radius}"
                    stroke="rgba(255, 255, 255, 0.2)"
                    stroke-width="8"
                    fill="transparent"
                />
                <circle 
                    cx="60" cy="60" r="{radius}"
                    stroke="url(#gradient{hash(label)})"
                    stroke-width="8"
                    fill="transparent"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    stroke-linecap="round"
                    style="transition: stroke-dashoffset 1s ease-in-out;"
                />
                <defs>
                    <linearGradient id="gradient{hash(label)}" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#4ECDC4;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#26C6DA;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <text x="60" y="60" text-anchor="middle" dy="0.3em" 
                      style="font-size: 18px; font-weight: 700; fill: #2C3E50; transform: rotate(90deg) translateX(60px) translateY(-60px);">
                    {percentage:.0f}
                </text>
            </svg>
            <div style="margin-top: 8px; font-weight: 600; color: #2C3E50; text-align: center;">
                {label}
            </div>
        </div>
        """
        
        st.markdown(ring_html, unsafe_allow_html=True)