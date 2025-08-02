"""
Theme System

Provides consistent theming across the application with light/dark mode support.
"""

from typing import Dict, Any
import streamlit as st


class ThemeManager:
    """Manages application themes and color schemes."""
    
    def __init__(self):
        # Initialize theme from session state or default
        if 'theme_mode' not in st.session_state:
            st.session_state.theme_mode = 'light'
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Get the current active theme."""
        if st.session_state.theme_mode == 'dark':
            return self._get_dark_theme()
        return self._get_light_theme()
    
    def _get_light_theme(self) -> Dict[str, Any]:
        """Light theme configuration."""
        return {
            # Primary colors
            'primary': '#3B82F6',        # Blue 500
            'primary_dark': '#2563EB',   # Blue 600
            'primary_light': '#60A5FA',  # Blue 400
            
            # Status colors
            'success': '#10B981',        # Emerald 500
            'success_dark': '#059669',   # Emerald 600
            'success_light': '#34D399',  # Emerald 400
            
            'danger': '#EF4444',         # Red 500
            'danger_dark': '#DC2626',    # Red 600
            'danger_light': '#F87171',   # Red 400
            
            'warning': '#F59E0B',        # Amber 500
            'warning_dark': '#D97706',   # Amber 600
            'warning_light': '#FBBF24',  # Amber 400
            
            'info': '#06B6D4',           # Cyan 500
            'info_dark': '#0891B2',      # Cyan 600
            'info_light': '#22D3EE',     # Cyan 400
            
            # Neutral colors
            'neutral': '#6B7280',        # Gray 500
            'neutral_dark': '#4B5563',   # Gray 600
            'neutral_light': '#9CA3AF',  # Gray 400
            
            # Background colors
            'background': '#FFFFFF',
            'surface': '#F9FAFB',
            'card_bg': '#FFFFFF',
            
            # Text colors
            'text_primary': '#111827',    # Gray 900
            'text_secondary': '#6B7280',  # Gray 500
            'text_disabled': '#D1D5DB',   # Gray 300
            
            # Border colors
            'border': '#E5E7EB',         # Gray 200
            'border_focus': '#3B82F6',   # Primary
            
            # Chart colors
            'chart_colors': [
                '#3B82F6',  # Blue
                '#10B981',  # Emerald
                '#F59E0B',  # Amber
                '#EF4444',  # Red
                '#8B5CF6',  # Purple
                '#EC4899',  # Pink
                '#06B6D4',  # Cyan
                '#84CC16',  # Lime
            ],
            
            # Shadows
            'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'shadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            
            # Gradients
            'gradient_primary': 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
            'gradient_success': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            'gradient_danger': 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
        }
    
    def _get_dark_theme(self) -> Dict[str, Any]:
        """Dark theme configuration."""
        return {
            # Primary colors
            'primary': '#60A5FA',        # Blue 400
            'primary_dark': '#3B82F6',   # Blue 500
            'primary_light': '#93BBFC',  # Blue 300
            
            # Status colors
            'success': '#34D399',        # Emerald 400
            'success_dark': '#10B981',   # Emerald 500
            'success_light': '#6EE7B7',  # Emerald 300
            
            'danger': '#F87171',         # Red 400
            'danger_dark': '#EF4444',    # Red 500
            'danger_light': '#FCA5A5',   # Red 300
            
            'warning': '#FBBF24',        # Amber 400
            'warning_dark': '#F59E0B',   # Amber 500
            'warning_light': '#FCD34D',  # Amber 300
            
            'info': '#22D3EE',           # Cyan 400
            'info_dark': '#06B6D4',      # Cyan 500
            'info_light': '#67E8F9',     # Cyan 300
            
            # Neutral colors
            'neutral': '#9CA3AF',        # Gray 400
            'neutral_dark': '#6B7280',   # Gray 500
            'neutral_light': '#D1D5DB',  # Gray 300
            
            # Background colors
            'background': '#111827',     # Gray 900
            'surface': '#1F2937',        # Gray 800
            'card_bg': '#1F2937',        # Gray 800
            
            # Text colors
            'text_primary': '#F9FAFB',    # Gray 50
            'text_secondary': '#D1D5DB',  # Gray 300
            'text_disabled': '#6B7280',   # Gray 500
            
            # Border colors
            'border': '#374151',         # Gray 700
            'border_focus': '#60A5FA',   # Primary
            
            # Chart colors (slightly adjusted for dark mode)
            'chart_colors': [
                '#60A5FA',  # Blue 400
                '#34D399',  # Emerald 400
                '#FBBF24',  # Amber 400
                '#F87171',  # Red 400
                '#A78BFA',  # Purple 400
                '#F472B6',  # Pink 400
                '#22D3EE',  # Cyan 400
                '#A3E635',  # Lime 400
            ],
            
            # Shadows (darker for dark mode)
            'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.2)',
            'shadow': '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
            'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
            'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
            
            # Gradients
            'gradient_primary': 'linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%)',
            'gradient_success': 'linear-gradient(135deg, #34D399 0%, #10B981 100%)',
            'gradient_danger': 'linear-gradient(135deg, #F87171 0%, #EF4444 100%)',
        }
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        st.session_state.theme_mode = 'dark' if st.session_state.theme_mode == 'light' else 'light'
        st.rerun()
    
    def apply_theme(self):
        """Apply the current theme to the application."""
        theme = self.get_current_theme()
        
        # Generate CSS based on current theme
        css = f"""
        <style>
        /* CSS Variables for easy access */
        :root {{
            --primary: {theme['primary']};
            --primary-dark: {theme['primary_dark']};
            --primary-light: {theme['primary_light']};
            
            --success: {theme['success']};
            --danger: {theme['danger']};
            --warning: {theme['warning']};
            --info: {theme['info']};
            --neutral: {theme['neutral']};
            
            --bg: {theme['background']};
            --surface: {theme['surface']};
            --card-bg: {theme['card_bg']};
            
            --text-primary: {theme['text_primary']};
            --text-secondary: {theme['text_secondary']};
            --text-disabled: {theme['text_disabled']};
            
            --border: {theme['border']};
            --border-focus: {theme['border_focus']};
        }}
        
        /* Apply theme to body */
        .stApp {{
            background-color: {theme['background']};
            color: {theme['text_primary']};
        }}
        
        /* Sidebar theming */
        .css-1d391kg {{
            background-color: {theme['surface']};
        }}
        
        /* Card theming */
        .stMarkdown {{
            color: {theme['text_primary']};
        }}
        
        /* Button theming */
        .stButton > button {{
            background-color: {theme['primary']};
            color: white;
            border: none;
        }}
        
        .stButton > button:hover {{
            background-color: {theme['primary_dark']};
        }}
        
        /* Input theming */
        .stTextInput > div > div > input {{
            background-color: {theme['card_bg']};
            color: {theme['text_primary']};
            border-color: {theme['border']};
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {theme['border_focus']};
        }}
        
        /* Selectbox theming */
        .stSelectbox > div > div {{
            background-color: {theme['card_bg']};
            color: {theme['text_primary']};
            border-color: {theme['border']};
        }}
        
        /* Tab theming */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {theme['surface']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: {theme['text_secondary']};
            background-color: transparent;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {theme['primary']};
            border-bottom-color: {theme['primary']};
        }}
        
        /* Metric theming */
        [data-testid="metric-container"] {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 1rem;
            box-shadow: {theme['shadow_sm']};
        }}
        
        /* Expander theming */
        .streamlit-expanderHeader {{
            background-color: {theme['surface']};
            color: {theme['text_primary']};
        }}
        
        /* Custom classes */
        .theme-card {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: {theme['shadow']};
        }}
        
        .theme-success {{
            color: {theme['success']};
        }}
        
        .theme-danger {{
            color: {theme['danger']};
        }}
        
        .theme-warning {{
            color: {theme['warning']};
        }}
        
        .theme-info {{
            color: {theme['info']};
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.3s ease-out;
        }}
        
        /* Transitions */
        * {{
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def render_theme_toggle(self):
        """Render a theme toggle button."""
        theme = self.get_current_theme()
        current_mode = st.session_state.theme_mode
        
        icon = "🌙" if current_mode == 'light' else "☀️"
        
        # Position the toggle in the top right
        st.markdown(f"""
        <div style="position: fixed; top: 1rem; right: 1rem; z-index: 1000;">
            <button onclick="window.location.reload();" 
                    style="background: {theme['surface']}; 
                           border: 1px solid {theme['border']};
                           border-radius: 8px;
                           padding: 0.5rem 1rem;
                           cursor: pointer;
                           font-size: 1.5rem;
                           transition: all 0.3s ease;">
                {icon}
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a hidden toggle that can be triggered
        if st.button("toggle_theme", key="theme_toggle_hidden", type="secondary"):
            self.toggle_theme()
    
    def get_chart_config(self) -> Dict[str, Any]:
        """Get chart configuration based on current theme."""
        theme = self.get_current_theme()
        
        return {
            'color_discrete_sequence': theme['chart_colors'],
            'template': 'plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white',
            'font': {
                'family': 'Inter, sans-serif',
                'color': theme['text_primary']
            },
            'paper_bgcolor': theme['card_bg'],
            'plot_bgcolor': theme['background'],
            'gridcolor': theme['border'],
            'linecolor': theme['border']
        }