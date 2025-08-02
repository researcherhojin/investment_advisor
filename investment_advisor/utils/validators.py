"""
Input Validators

Utility functions for validating user inputs and data.
"""

import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validation utilities."""
    
    # Common ticker patterns
    US_TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}$')
    KOREA_TICKER_PATTERN = re.compile(r'^\d{6}$')
    
    # Valid markets
    VALID_MARKETS = ["미국장", "한국장"]
    
    # Valid industries
    VALID_INDUSTRIES = [
        "기술", "의료", "금융", "소비재", "에너지", "통신", "산업재", "유틸리티",
        "전자/IT", "바이오", "건설"
    ]
    
    @classmethod
    def validate_ticker(cls, ticker: str, market: str) -> Dict[str, Any]:
        """
        Validate stock ticker format.
        
        Args:
            ticker: Stock ticker symbol
            market: Market identifier
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": "", "normalized_ticker": ""}
        
        if not ticker:
            result["message"] = "티커를 입력해주세요."
            return result
        
        # Normalize ticker
        normalized = ticker.strip().upper()
        
        if market == "미국장":
            if cls.US_TICKER_PATTERN.match(normalized):
                result["valid"] = True
                result["normalized_ticker"] = normalized
                result["message"] = "유효한 미국 주식 티커입니다."
            else:
                result["message"] = "미국 주식 티커는 1-5자리 영문자여야 합니다 (예: AAPL, MSFT)."
        
        elif market == "한국장":
            # Remove any non-digit characters
            digits_only = re.sub(r'\D', '', ticker)
            
            if cls.KOREA_TICKER_PATTERN.match(digits_only):
                result["valid"] = True
                result["normalized_ticker"] = digits_only
                result["message"] = "유효한 한국 주식 종목코드입니다."
            else:
                result["message"] = "한국 주식 종목코드는 6자리 숫자여야 합니다 (예: 005930, 000660)."
        
        else:
            result["message"] = f"지원되지 않는 시장입니다: {market}"
        
        return result
    
    @classmethod
    def validate_market(cls, market: str) -> Dict[str, Any]:
        """
        Validate market selection.
        
        Args:
            market: Market identifier
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": ""}
        
        if not market:
            result["message"] = "시장을 선택해주세요."
            return result
        
        if market in cls.VALID_MARKETS:
            result["valid"] = True
            result["message"] = "유효한 시장 선택입니다."
        else:
            result["message"] = f"지원되는 시장: {', '.join(cls.VALID_MARKETS)}"
        
        return result
    
    @classmethod
    def validate_industry(cls, industry: str) -> Dict[str, Any]:
        """
        Validate industry selection.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": ""}
        
        if not industry:
            result["message"] = "산업을 선택해주세요."
            return result
        
        if industry in cls.VALID_INDUSTRIES:
            result["valid"] = True
            result["message"] = "유효한 산업 선택입니다."
        else:
            result["message"] = f"지원되는 산업: {', '.join(cls.VALID_INDUSTRIES)}"
        
        return result
    
    @classmethod
    def validate_analysis_period(cls, period: int) -> Dict[str, Any]:
        """
        Validate analysis period.
        
        Args:
            period: Analysis period in months
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": ""}
        
        if not isinstance(period, (int, float)):
            result["message"] = "분석 기간은 숫자여야 합니다."
            return result
        
        period = int(period)
        
        if period < 1:
            result["message"] = "분석 기간은 최소 1개월이어야 합니다."
        elif period > 60:
            result["message"] = "분석 기간은 최대 60개월(5년)까지 가능합니다."
        else:
            result["valid"] = True
            result["message"] = f"{period}개월 분석 기간이 설정되었습니다."
        
        return result
    
    @classmethod
    def validate_date_range(
        cls, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Validate date range for analysis.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": ""}
        
        # Check if dates are valid
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            result["message"] = "유효한 날짜를 입력해주세요."
            return result
        
        # Check date order
        if start_date >= end_date:
            result["message"] = "시작 날짜는 종료 날짜보다 빨라야 합니다."
            return result
        
        # Check if dates are too far in the future
        now = datetime.now()
        if start_date > now or end_date > now:
            result["message"] = "미래 날짜는 선택할 수 없습니다."
            return result
        
        # Check minimum period (at least 7 days)
        if (end_date - start_date).days < 7:
            result["message"] = "분석을 위해 최소 7일간의 데이터가 필요합니다."
            return result
        
        # Check maximum period (5 years)
        if (end_date - start_date).days > 365 * 5:
            result["message"] = "분석 기간은 최대 5년까지 가능합니다."
            return result
        
        result["valid"] = True
        result["message"] = f"{(end_date - start_date).days}일간의 데이터를 분석합니다."
        
        return result
    
    @classmethod
    def validate_price_input(cls, price: Any) -> Dict[str, Any]:
        """
        Validate price input.
        
        Args:
            price: Price value to validate
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": "", "normalized_price": 0.0}
        
        if price is None:
            result["message"] = "가격을 입력해주세요."
            return result
        
        try:
            # Handle string inputs (remove currency symbols and commas)
            if isinstance(price, str):
                cleaned_price = re.sub(r'[^\d.-]', '', price)
                price_value = float(cleaned_price)
            else:
                price_value = float(price)
            
            if price_value <= 0:
                result["message"] = "가격은 0보다 커야 합니다."
                return result
            
            # Check reasonable price ranges
            if price_value > 1_000_000:  # Very high price
                result["message"] = "입력된 가격이 매우 높습니다. 확인해주세요."
                return result
            
            result["valid"] = True
            result["normalized_price"] = price_value
            result["message"] = f"가격: {price_value:,.2f}"
            
        except (ValueError, TypeError):
            result["message"] = "유효한 숫자를 입력해주세요."
        
        return result
    
    @classmethod
    def sanitize_text_input(cls, text: str, max_length: int = 100) -> str:
        """
        Sanitize text input to prevent injection attacks.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    @classmethod
    def validate_portfolio_allocation(cls, allocations: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate portfolio allocation percentages.
        
        Args:
            allocations: Dictionary of asset -> allocation percentage
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": "", "total_allocation": 0.0}
        
        if not allocations:
            result["message"] = "포트폴리오 구성을 입력해주세요."
            return result
        
        try:
            total = sum(allocations.values())
            result["total_allocation"] = total
            
            # Check individual allocations
            for asset, allocation in allocations.items():
                if allocation < 0:
                    result["message"] = f"{asset}의 비중은 음수일 수 없습니다."
                    return result
                
                if allocation > 100:
                    result["message"] = f"{asset}의 비중이 100%를 초과합니다."
                    return result
            
            # Check total allocation
            if abs(total - 100) > 0.01:  # Allow small rounding errors
                result["message"] = f"총 투자 비중이 {total:.1f}%입니다. 100%가 되어야 합니다."
                return result
            
            result["valid"] = True
            result["message"] = "포트폴리오 구성이 유효합니다."
            
        except (ValueError, TypeError) as e:
            result["message"] = f"포트폴리오 구성 검증 중 오류: {str(e)}"
        
        return result
    
    @classmethod
    def is_market_hours(cls, market: str, check_time: Optional[datetime] = None) -> bool:
        """
        Check if it's currently market hours.
        
        Args:
            market: Market identifier
            check_time: Time to check (defaults to now)
            
        Returns:
            True if market is open
        """
        if check_time is None:
            check_time = datetime.now()
        
        # This is a simplified implementation
        # In production, you'd want to account for holidays, time zones, etc.
        
        weekday = check_time.weekday()  # 0 = Monday, 6 = Sunday
        hour = check_time.hour
        
        # Skip weekends
        if weekday >= 5:  # Saturday or Sunday
            return False
        
        if market == "미국장":
            # US market: 9:30 AM - 4:00 PM EST
            # This is simplified - doesn't account for timezone conversion
            return 9 <= hour <= 16
        
        elif market == "한국장":
            # Korean market: 9:00 AM - 3:30 PM KST
            # This is simplified - doesn't account for timezone conversion
            return 9 <= hour <= 15
        
        return False
    
    @classmethod
    def validate_risk_tolerance(cls, risk_level: str) -> Dict[str, Any]:
        """
        Validate risk tolerance level.
        
        Args:
            risk_level: Risk tolerance level
            
        Returns:
            Dictionary with validation result
        """
        result = {"valid": False, "message": ""}
        
        valid_levels = ["보수적", "중립적", "공격적"]
        
        if risk_level not in valid_levels:
            result["message"] = f"위험 성향은 다음 중 하나여야 합니다: {', '.join(valid_levels)}"
            return result
        
        result["valid"] = True
        result["message"] = f"위험 성향: {risk_level}"
        
        return result