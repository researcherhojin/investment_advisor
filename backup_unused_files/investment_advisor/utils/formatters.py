"""
Data Formatters

Utility functions for formatting data display.
"""

import logging
from typing import Any, Union, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class DataFormatter:
    """General data formatting utilities."""
    
    @staticmethod
    def safe_format_number(value: Any, decimal_places: int = 2) -> str:
        """
        Safely format a number with proper handling of None/NaN values.
        
        Args:
            value: Value to format
            decimal_places: Number of decimal places
            
        Returns:
            Formatted string
        """
        if value is None or pd.isna(value):
            return "정보 없음"
        
        try:
            num_value = float(value)
            return f"{num_value:.{decimal_places}f}"
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def format_percentage(value: Any, decimal_places: int = 2) -> str:
        """
        Format a value as percentage.
        
        Args:
            value: Value to format (should be in decimal form, e.g., 0.05 for 5%)
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        if value is None or pd.isna(value):
            return "정보 없음"
        
        try:
            num_value = float(value)
            # If value is already in percentage form (>1), don't multiply by 100
            if abs(num_value) > 1:
                return f"{num_value:.{decimal_places}f}%"
            else:
                return f"{num_value * 100:.{decimal_places}f}%"
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def format_large_number(value: Any, decimal_places: int = 1) -> str:
        """
        Format large numbers with appropriate suffixes (K, M, B, T).
        
        Args:
            value: Value to format
            decimal_places: Number of decimal places
            
        Returns:
            Formatted string with suffix
        """
        if value is None or pd.isna(value):
            return "정보 없음"
        
        try:
            num_value = float(value)
            
            if abs(num_value) >= 1_000_000_000_000:  # Trillion
                return f"{num_value / 1_000_000_000_000:.{decimal_places}f}T"
            elif abs(num_value) >= 1_000_000_000:  # Billion
                return f"{num_value / 1_000_000_000:.{decimal_places}f}B"
            elif abs(num_value) >= 1_000_000:  # Million
                return f"{num_value / 1_000_000:.{decimal_places}f}M"
            elif abs(num_value) >= 1_000:  # Thousand
                return f"{num_value / 1_000:.{decimal_places}f}K"
            else:
                return f"{num_value:.{decimal_places}f}"
                
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def clean_string_value(value: Any) -> str:
        """
        Clean string values by removing unwanted characters.
        
        Args:
            value: Value to clean
            
        Returns:
            Cleaned string
        """
        if value is None or pd.isna(value):
            return "정보 없음"
        
        # Convert to string and clean
        str_value = str(value).strip()
        
        # Replace common "no data" indicators
        no_data_indicators = ["N/A", "n/a", "null", "None", "", "-"]
        if str_value in no_data_indicators:
            return "정보 없음"
        
        return str_value


class PriceFormatter:
    """Specialized formatter for price and financial data."""
    
    def __init__(self, market: str = "미국장"):
        self.market = market
        self.currency_symbol = "원" if market == "한국장" else "$"
        self.currency_position = "suffix" if market == "한국장" else "prefix"
    
    def format_price(self, price: Any, decimal_places: Optional[int] = None) -> str:
        """
        Format price with appropriate currency symbol and decimal places.
        
        Args:
            price: Price value to format
            decimal_places: Number of decimal places (auto-determined if None)
            
        Returns:
            Formatted price string
        """
        if price is None or pd.isna(price):
            return "정보 없음"
        
        try:
            price_value = float(price)
            
            # Auto-determine decimal places if not specified
            if decimal_places is None:
                if self.market == "한국장":
                    decimal_places = 0  # Korean stocks usually don't use decimals
                else:
                    decimal_places = 2  # US stocks use 2 decimal places
            
            # Format the number with commas
            if decimal_places == 0:
                formatted_number = f"{price_value:,.0f}"
            else:
                formatted_number = f"{price_value:,.{decimal_places}f}"
            
            # Add currency symbol
            if self.currency_position == "prefix":
                return f"{self.currency_symbol}{formatted_number}"
            else:
                return f"{formatted_number}{self.currency_symbol}"
                
        except (ValueError, TypeError):
            return str(price)
    
    def format_market_cap(self, market_cap: Any) -> str:
        """
        Format market capitalization with appropriate units.
        
        Args:
            market_cap: Market cap value
            
        Returns:
            Formatted market cap string
        """
        if market_cap is None or pd.isna(market_cap):
            return "정보 없음"
        
        try:
            mc_value = float(market_cap)
            
            if self.market == "한국장":
                # Korean market cap in KRW
                if mc_value >= 1_000_000_000_000:  # 1 trillion KRW
                    return f"{mc_value / 1_000_000_000_000:.1f}조원"
                elif mc_value >= 100_000_000_000:  # 100 billion KRW
                    return f"{mc_value / 100_000_000_000:.1f}천억원"
                elif mc_value >= 10_000_000_000:  # 10 billion KRW
                    return f"{mc_value / 10_000_000_000:.1f}백억원"
                else:
                    return f"{mc_value / 100_000_000:.1f}억원"
            else:
                # US market cap in USD
                if mc_value >= 1_000_000_000_000:  # 1 trillion USD
                    return f"${mc_value / 1_000_000_000_000:.1f}T"
                elif mc_value >= 1_000_000_000:  # 1 billion USD
                    return f"${mc_value / 1_000_000_000:.1f}B"
                elif mc_value >= 1_000_000:  # 1 million USD
                    return f"${mc_value / 1_000_000:.1f}M"
                else:
                    return f"${mc_value:,.0f}"
                    
        except (ValueError, TypeError):
            return str(market_cap)
    
    def format_volume(self, volume: Any) -> str:
        """
        Format trading volume.
        
        Args:
            volume: Volume value
            
        Returns:
            Formatted volume string
        """
        if volume is None or pd.isna(volume):
            return "정보 없음"
        
        try:
            vol_value = float(volume)
            
            if vol_value >= 1_000_000:
                return f"{vol_value / 1_000_000:.1f}M"
            elif vol_value >= 1_000:
                return f"{vol_value / 1_000:.1f}K"
            else:
                return f"{vol_value:,.0f}"
                
        except (ValueError, TypeError):
            return str(volume)
    
    def format_ratio(self, ratio: Any, decimal_places: int = 2) -> str:
        """
        Format financial ratios (P/E, P/B, etc.).
        
        Args:
            ratio: Ratio value
            decimal_places: Number of decimal places
            
        Returns:
            Formatted ratio string
        """
        if ratio is None or pd.isna(ratio):
            return "정보 없음"
        
        try:
            ratio_value = float(ratio)
            
            # Handle negative ratios
            if ratio_value < 0:
                return "음수"
            
            # Handle very large ratios
            if ratio_value > 1000:
                return f"{ratio_value:.0f}배"
            
            return f"{ratio_value:.{decimal_places}f}배"
            
        except (ValueError, TypeError):
            return str(ratio)
    
    def format_change(self, change: Any, change_percent: Any = None) -> str:
        """
        Format price change with color coding information.
        
        Args:
            change: Absolute change value
            change_percent: Percentage change value
            
        Returns:
            Formatted change string
        """
        if change is None or pd.isna(change):
            return "정보 없음"
        
        try:
            change_value = float(change)
            
            # Format absolute change
            change_str = self.format_price(abs(change_value))
            
            # Add percentage if available
            if change_percent is not None and not pd.isna(change_percent):
                try:
                    pct_value = float(change_percent)
                    pct_str = f"({abs(pct_value):.2f}%)"
                except (ValueError, TypeError):
                    pct_str = ""
            else:
                pct_str = ""
            
            # Add sign and combine
            if change_value > 0:
                return f"▲ {change_str} {pct_str}"
            elif change_value < 0:
                return f"▼ {change_str} {pct_str}"
            else:
                return f"- {change_str} {pct_str}"
                
        except (ValueError, TypeError):
            return str(change)
    
    def get_trend_emoji(self, value: Any) -> str:
        """
        Get trend emoji based on value.
        
        Args:
            value: Value to evaluate
            
        Returns:
            Trend emoji
        """
        if value is None or pd.isna(value):
            return "➡️"
        
        try:
            num_value = float(value)
            if num_value > 0:
                return "📈"
            elif num_value < 0:
                return "📉"
            else:
                return "➡️"
        except (ValueError, TypeError):
            return "➡️"