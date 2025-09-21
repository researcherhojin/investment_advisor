"""
UI Module

Contains Streamlit UI components and layouts with professional design.
"""

# UI modules moved to backups - using minimal_ui for main application
# from .clean_modern_ui import CleanModernUI  # Moved to backups
# from .card_layout import CardLayoutManager  # Moved to backups
# from .dashboard import DashboardManager  # Moved to backups
# from .themes import ThemeManager  # Moved to backups

# Import from minimal_ui which is used by main.py
from .minimal_ui import (
    apply_minimal_theme,
    render_header,
    render_how_to_use,
    render_stock_input_section,
    render_quick_stats,
    render_analysis_results,
    render_price_chart,
    render_technical_chart,
    render_loading,
    render_error,
    render_footer
)

__all__ = [
    'apply_minimal_theme',
    'render_header',
    'render_how_to_use',
    'render_stock_input_section',
    'render_quick_stats',
    'render_analysis_results',
    'render_price_chart',
    'render_technical_chart',
    'render_loading',
    'render_error',
    'render_footer'
]
