"""
Fundamental Analysis Module

Provides comprehensive fundamental analysis functionality.
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Comprehensive fundamental analysis toolkit."""
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
    
    def analyze(self, financial_data: Dict[str, Any], market: str = "미국장") -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis.
        
        Args:
            financial_data: Dictionary with financial data
            market: Market identifier
            
        Returns:
            Dictionary with fundamental analysis results
        """
        if not financial_data:
            logger.warning("No financial data provided")
            return {}
        
        results = {}
        
        # Valuation metrics
        results.update(self._analyze_valuation_metrics(financial_data, market))
        
        # Profitability analysis
        results.update(self._analyze_profitability(financial_data, market))
        
        # Financial health
        results.update(self._analyze_financial_health(financial_data, market))
        
        # Growth analysis
        results.update(self._analyze_growth_metrics(financial_data, market))
        
        # Efficiency metrics
        results.update(self._analyze_efficiency_metrics(financial_data, market))
        
        # Dividend analysis
        results.update(self._analyze_dividend_metrics(financial_data, market))
        
        # Overall fundamental score
        results['fundamental_score'] = self._calculate_fundamental_score(results, market)
        
        # Investment recommendation
        results['investment_grade'] = self._determine_investment_grade(results)
        
        return results
    
    def _analyze_valuation_metrics(self, data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """Analyze valuation metrics."""
        results = {}
        
        # P/E Ratio
        per = self._safe_get_numeric(data, 'PER')
        if per and per > 0:
            results['per'] = per
            results['per_interpretation'] = self._interpret_per(per, market)
        
        # P/B Ratio
        pbr = self._safe_get_numeric(data, 'PBR')
        if pbr and pbr > 0:
            results['pbr'] = pbr
            results['pbr_interpretation'] = self._interpret_pbr(pbr, market)
        
        # Market Cap
        market_cap = self._safe_get_numeric(data, '시가총액') or self._safe_get_numeric(data, 'Market Cap')
        if market_cap:
            results['market_cap'] = market_cap
            results['size_category'] = self._categorize_market_cap(market_cap, market)
        
        # Price to Sales (if available)
        revenue = self._safe_get_numeric(data, 'Revenue') or self._safe_get_numeric(data, 'totalRevenue')
        if market_cap and revenue:
            ps_ratio = market_cap / revenue
            results['ps_ratio'] = ps_ratio
            results['ps_interpretation'] = self._interpret_ps(ps_ratio)
        
        # Enterprise Value metrics (if available)
        if market_cap:
            # This is simplified - in practice, you'd need debt and cash data
            results['enterprise_value'] = market_cap  # Approximation
        
        return results
    
    def _analyze_profitability(self, data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """Analyze profitability metrics."""
        results = {}
        
        # ROE (Return on Equity)
        roe = self._safe_get_numeric(data, 'ROE') or self._safe_get_numeric(data, 'returnOnEquity')
        if roe:
            results['roe'] = roe
            results['roe_interpretation'] = self._interpret_roe(roe)
        
        # ROA (Return on Assets)
        roa = self._safe_get_numeric(data, 'returnOnAssets')
        if roa:
            results['roa'] = roa
            results['roa_interpretation'] = self._interpret_roa(roa)
        
        # Profit Margins
        profit_margin = self._safe_get_numeric(data, 'profitMargins')
        if profit_margin:
            results['profit_margin'] = profit_margin * 100  # Convert to percentage
            results['profit_margin_interpretation'] = self._interpret_profit_margin(profit_margin * 100)
        
        # Gross Margins
        gross_margin = self._safe_get_numeric(data, 'grossMargins')
        if gross_margin:
            results['gross_margin'] = gross_margin * 100
            results['gross_margin_interpretation'] = self._interpret_gross_margin(gross_margin * 100)
        
        # Operating Margins
        operating_margin = self._safe_get_numeric(data, 'operatingMargins')
        if operating_margin:
            results['operating_margin'] = operating_margin * 100
            results['operating_margin_interpretation'] = self._interpret_operating_margin(operating_margin * 100)
        
        return results
    
    def _analyze_financial_health(self, data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """Analyze financial health metrics."""
        results = {}
        
        # Debt to Equity
        debt_to_equity = self._safe_get_numeric(data, 'debtToEquity')
        if debt_to_equity:
            results['debt_to_equity'] = debt_to_equity
            results['debt_to_equity_interpretation'] = self._interpret_debt_to_equity(debt_to_equity)
        
        # Current Ratio
        current_ratio = self._safe_get_numeric(data, 'currentRatio')
        if current_ratio:
            results['current_ratio'] = current_ratio
            results['current_ratio_interpretation'] = self._interpret_current_ratio(current_ratio)
        
        # Quick Ratio
        quick_ratio = self._safe_get_numeric(data, 'quickRatio')
        if quick_ratio:
            results['quick_ratio'] = quick_ratio
            results['quick_ratio_interpretation'] = self._interpret_quick_ratio(quick_ratio)
        
        # Cash Flow Analysis
        free_cash_flow = self._safe_get_numeric(data, 'freeCashflow')
        operating_cash_flow = self._safe_get_numeric(data, 'operatingCashflow')
        
        if free_cash_flow:
            results['free_cash_flow'] = free_cash_flow
            results['fcf_interpretation'] = self._interpret_free_cash_flow(free_cash_flow)
        
        if operating_cash_flow:
            results['operating_cash_flow'] = operating_cash_flow
        
        # Cash Flow Quality
        if free_cash_flow and operating_cash_flow and operating_cash_flow != 0:
            fcf_to_ocf_ratio = free_cash_flow / operating_cash_flow
            results['fcf_to_ocf_ratio'] = fcf_to_ocf_ratio
            results['cash_flow_quality'] = self._interpret_cash_flow_quality(fcf_to_ocf_ratio)
        
        return results
    
    def _analyze_growth_metrics(self, data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """Analyze growth metrics."""
        results = {}
        
        # Revenue Growth
        revenue_growth = self._safe_get_numeric(data, 'revenueGrowth')
        if revenue_growth:
            results['revenue_growth'] = revenue_growth * 100
            results['revenue_growth_interpretation'] = self._interpret_revenue_growth(revenue_growth * 100)
        
        # Earnings Growth
        earnings_growth = self._safe_get_numeric(data, 'earningsGrowth')
        if earnings_growth:
            results['earnings_growth'] = earnings_growth * 100
            results['earnings_growth_interpretation'] = self._interpret_earnings_growth(earnings_growth * 100)
        
        # PEG Ratio (P/E to Growth)
        per = self._safe_get_numeric(data, 'PER')
        if per and earnings_growth and earnings_growth > 0:
            peg_ratio = per / (earnings_growth * 100)
            results['peg_ratio'] = peg_ratio
            results['peg_interpretation'] = self._interpret_peg(peg_ratio)
        
        return results
    
    def _analyze_efficiency_metrics(self, data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """Analyze operational efficiency metrics."""
        results = {}
        
        # Asset Turnover (approximation if revenue and assets available)
        revenue = self._safe_get_numeric(data, 'Revenue') or self._safe_get_numeric(data, 'totalRevenue')
        
        # Inventory Turnover, Receivables Turnover would go here if data available
        # This is a placeholder for more detailed efficiency analysis
        
        return results
    
    def _analyze_dividend_metrics(self, data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """Analyze dividend-related metrics."""
        results = {}
        
        # Dividend Yield
        dividend_yield = self._safe_get_numeric(data, '배당수익률') or self._safe_get_numeric(data, 'dividendYield')
        if dividend_yield:
            # Convert to percentage if needed
            if dividend_yield < 1:  # Likely in decimal form
                dividend_yield *= 100
            
            results['dividend_yield'] = dividend_yield
            results['dividend_yield_interpretation'] = self._interpret_dividend_yield(dividend_yield)
        
        # Dividend sustainability (would need more data for proper analysis)
        if dividend_yield:
            results['dividend_sustainability'] = self._assess_dividend_sustainability(data, dividend_yield)
        
        return results
    
    def _calculate_fundamental_score(self, results: Dict[str, Any], market: str) -> float:
        """Calculate overall fundamental score (0-100)."""
        score = 50  # Neutral starting point
        factors_count = 0
        
        # Valuation component (±15 points)
        per = results.get('per')
        if per:
            if market == "한국장":
                if 5 <= per <= 15:
                    score += 10
                elif per < 5 or per > 25:
                    score -= 10
            else:  # US market
                if 10 <= per <= 20:
                    score += 10
                elif per < 8 or per > 30:
                    score -= 10
            factors_count += 1
        
        pbr = results.get('pbr')
        if pbr:
            if 0.5 <= pbr <= 2:
                score += 5
            elif pbr > 3:
                score -= 5
            factors_count += 1
        
        # Profitability component (±20 points)
        roe = results.get('roe')
        if roe:
            if roe > 15:
                score += 15
            elif roe > 10:
                score += 10
            elif roe < 5:
                score -= 10
            factors_count += 1
        
        profit_margin = results.get('profit_margin')
        if profit_margin:
            if profit_margin > 15:
                score += 5
            elif profit_margin < 5:
                score -= 5
            factors_count += 1
        
        # Financial Health component (±15 points)
        debt_to_equity = results.get('debt_to_equity')
        if debt_to_equity:
            if debt_to_equity < 0.3:
                score += 10
            elif debt_to_equity > 1.0:
                score -= 10
            factors_count += 1
        
        current_ratio = results.get('current_ratio')
        if current_ratio:
            if current_ratio > 1.5:
                score += 5
            elif current_ratio < 1.0:
                score -= 10
            factors_count += 1
        
        # Growth component (±10 points)
        revenue_growth = results.get('revenue_growth')
        if revenue_growth:
            if revenue_growth > 10:
                score += 10
            elif revenue_growth < 0:
                score -= 5
            factors_count += 1
        
        # Adjust score if we have limited data
        if factors_count < 3:
            score = 50  # Return neutral if insufficient data
        
        return max(0, min(100, score))
    
    def _determine_investment_grade(self, results: Dict[str, Any]) -> str:
        """Determine investment grade based on fundamental analysis."""
        score = results.get('fundamental_score', 50)
        
        if score >= 80:
            return "A+ (매우 우수)"
        elif score >= 70:
            return "A (우수)"
        elif score >= 60:
            return "B+ (양호)"
        elif score >= 50:
            return "B (보통)"
        elif score >= 40:
            return "C+ (주의)"
        elif score >= 30:
            return "C (위험)"
        else:
            return "D (매우 위험)"
    
    # Helper methods for interpretations
    def _interpret_per(self, per: float, market: str) -> str:
        """Interpret P/E ratio."""
        if market == "한국장":
            if per < 8:
                return "저평가 가능성"
            elif per <= 15:
                return "적정 수준"
            elif per <= 25:
                return "다소 고평가"
            else:
                return "고평가 위험"
        else:  # US market
            if per < 10:
                return "저평가 가능성"
            elif per <= 20:
                return "적정 수준"
            elif per <= 30:
                return "다소 고평가"
            else:
                return "고평가 위험"
    
    def _interpret_pbr(self, pbr: float, market: str) -> str:
        """Interpret P/B ratio."""
        if pbr < 1:
            return "자산 대비 저평가"
        elif pbr <= 2:
            return "적정 수준"
        elif pbr <= 3:
            return "다소 고평가"
        else:
            return "고평가"
    
    def _interpret_roe(self, roe: float) -> str:
        """Interpret ROE."""
        if roe > 20:
            return "매우 우수한 수익성"
        elif roe > 15:
            return "우수한 수익성"
        elif roe > 10:
            return "양호한 수익성"
        elif roe > 5:
            return "보통 수익성"
        else:
            return "낮은 수익성"
    
    def _interpret_debt_to_equity(self, ratio: float) -> str:
        """Interpret debt-to-equity ratio."""
        if ratio < 0.2:
            return "매우 안전한 부채 수준"
        elif ratio < 0.5:
            return "안전한 부채 수준"
        elif ratio < 1.0:
            return "적정한 부채 수준"
        elif ratio < 2.0:
            return "높은 부채 수준"
        else:
            return "위험한 부채 수준"
    
    def _safe_get_numeric(self, data: Dict[str, Any], key: str) -> Optional[float]:
        """Safely get numeric value from data."""
        value = data.get(key)
        if value is None or value == "정보 없음" or value == "N/A":
            return None
        
        try:
            if isinstance(value, str):
                # Remove currency symbols and commas
                cleaned = value.replace("$", "").replace("원", "").replace(",", "").replace("%", "")
                return float(cleaned)
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry benchmark data (placeholder)."""
        # This would be loaded from a database or file in production
        return {
            "기술": {"per": 25, "pbr": 3, "roe": 15, "debt_to_equity": 0.3},
            "금융": {"per": 12, "pbr": 1.2, "roe": 12, "debt_to_equity": 0.8},
            "제조": {"per": 15, "pbr": 1.5, "roe": 10, "debt_to_equity": 0.5},
            "유틸리티": {"per": 18, "pbr": 1.3, "roe": 8, "debt_to_equity": 0.7},
        }
    
    # Additional interpretation methods would go here...
    def _categorize_market_cap(self, market_cap: float, market: str) -> str:
        """Categorize company by market cap."""
        if market == "한국장":
            # Korean market thresholds (in KRW)
            if market_cap > 10_000_000_000_000:  # 10 trillion KRW
                return "대형주"
            elif market_cap > 1_000_000_000_000:  # 1 trillion KRW
                return "중형주"
            else:
                return "소형주"
        else:
            # US market thresholds (in USD)
            if market_cap > 10_000_000_000:  # 10 billion USD
                return "대형주"
            elif market_cap > 2_000_000_000:  # 2 billion USD
                return "중형주"
            else:
                return "소형주"
    
    def _interpret_ps(self, ps_ratio: float) -> str:
        """Interpret Price-to-Sales ratio."""
        if ps_ratio > 10:
            return "매우 높은 P/S 비율 (과대평가 가능성)"
        elif ps_ratio > 5:
            return "높은 P/S 비율"
        elif ps_ratio > 2:
            return "적정한 P/S 비율"
        elif ps_ratio > 1:
            return "낮은 P/S 비율"
        else:
            return "매우 낮은 P/S 비율 (저평가 가능성)"
    
    def _interpret_dividend_yield(self, yield_pct: float) -> str:
        """Interpret dividend yield."""
        if yield_pct > 6:
            return "매우 높은 배당 (지속가능성 검토 필요)"
        elif yield_pct > 4:
            return "높은 배당"
        elif yield_pct > 2:
            return "적정한 배당"
        elif yield_pct > 0:
            return "낮은 배당"
        else:
            return "무배당"
    
    def _assess_dividend_sustainability(self, data: Dict[str, Any], dividend_yield: float) -> str:
        """Assess dividend sustainability (simplified)."""
        # This is a simplified assessment
        # In practice, you'd look at payout ratio, cash flow coverage, etc.
        
        if dividend_yield > 8:
            return "지속가능성 우려"
        elif dividend_yield > 6:
            return "지속가능성 검토 필요"
        else:
            return "지속가능할 것으로 예상"
    
    # Add more interpretation methods as needed...