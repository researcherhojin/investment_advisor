"""
Metrics Display Module

Handles the display of key metrics and indicators in the UI with professional design.
"""

import logging
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd

from ..utils import PriceFormatter, DataFormatter
from .styles import ProfessionalTheme, ComponentStyles

logger = logging.getLogger(__name__)


class MetricsDisplay:
    """Handle display of financial metrics and indicators."""
    
    def __init__(self, market: str = "미국장"):
        self.market = market
        self.price_formatter = PriceFormatter(market)
        self.data_formatter = DataFormatter()
    
    def display_key_metrics(self, metrics: Dict[str, Any]):
        """Display key financial metrics using professional cards."""
        # Define metric groups with icons
        metric_groups = {
            "가격 정보": {
                "metrics": ["현재가", "52주 최고가", "52주 최저가", "거래량"],
                "icon": "💰"
            },
            "가치 지표": {
                "metrics": ["PER", "PBR", "ROE", "배당수익률"],
                "icon": "📊"
            },
            "기업 정보": {
                "metrics": ["시가총액", "베타", "EPS", "Revenue"],
                "icon": "🏢"
            },
        }
        
        # Display each group
        for group_name, group_info in metric_groups.items():
            st.markdown(f"### {group_name}")
            
            # Filter available metrics
            available_metrics = {
                k: v for k, v in metrics.items() 
                if k in group_info["metrics"] and v not in ["정보 없음", "N/A", None]
            }
            
            if available_metrics:
                cols = st.columns(min(len(available_metrics), 4))
                
                for i, (key, value) in enumerate(available_metrics.items()):
                    with cols[i % 4]:
                        self._display_professional_metric_card(key, value)
            else:
                st.info(f"{group_name}에 대한 정보가 없습니다.")
    
    def display_technical_indicators(self, indicators: Dict[str, Any]):
        """Display technical indicators."""
        st.subheader("📊 기술적 지표")
        
        # Group indicators
        indicator_groups = {
            "추세 지표": ["sma_20", "sma_50", "sma_200", "trend_direction"],
            "모멘텀 지표": ["rsi", "macd_line", "momentum_signal"],
            "변동성 지표": ["atr", "historical_volatility", "bb_width"],
            "거래량 지표": ["volume_ratio_20", "obv", "volume_signal"],
        }
        
        for group_name, indicator_keys in indicator_groups.items():
            with st.expander(group_name, expanded=True):
                available_indicators = {
                    k: v for k, v in indicators.items()
                    if k in indicator_keys and v is not None
                }
                
                if available_indicators:
                    cols = st.columns(2)
                    for i, (key, value) in enumerate(available_indicators.items()):
                        with cols[i % 2]:
                            self._display_indicator(key, value)
                else:
                    st.info("지표 데이터가 없습니다.")
    
    def display_price_targets(self, targets: Dict[str, float]):
        """Display price targets with visual indicators."""
        st.subheader("🎯 가격 목표")
        
        current_price = targets.get('current_price', 0)
        
        # Create columns for targets
        col1, col2, col3 = st.columns(3)
        
        with col1:
            buy_target = targets.get('buy_target', 0)
            buy_diff = ((buy_target - current_price) / current_price * 100) if current_price > 0 else 0
            
            st.metric(
                label="매수 목표가",
                value=self.price_formatter.format_price(buy_target),
                delta=f"{buy_diff:+.1f}%"
            )
        
        with col2:
            profit_target = targets.get('profit_target', 0)
            profit_diff = ((profit_target - current_price) / current_price * 100) if current_price > 0 else 0
            
            st.metric(
                label="익절 목표가",
                value=self.price_formatter.format_price(profit_target),
                delta=f"{profit_diff:+.1f}%"
            )
        
        with col3:
            stop_loss = targets.get('stop_loss', 0)
            loss_diff = ((stop_loss - current_price) / current_price * 100) if current_price > 0 else 0
            
            st.metric(
                label="손절가",
                value=self.price_formatter.format_price(stop_loss),
                delta=f"{loss_diff:+.1f}%"
            )
        
        # Risk/Reward ratio
        if 'risk_reward_ratio' in targets:
            st.info(f"위험/보상 비율: {targets['risk_reward_ratio']:.2f}:1")
    
    def display_fundamental_analysis(self, analysis: Dict[str, Any]):
        """Display fundamental analysis results."""
        st.subheader("📈 기본적 분석")
        
        # Investment grade
        if 'investment_grade' in analysis:
            grade = analysis['investment_grade']
            grade_color = self._get_grade_color(grade)
            st.markdown(
                f"<h3 style='color: {grade_color};'>투자 등급: {grade}</h3>",
                unsafe_allow_html=True
            )
        
        # Fundamental score
        if 'fundamental_score' in analysis:
            score = analysis['fundamental_score']
            st.progress(score / 100)
            st.caption(f"기본적 분석 점수: {score}/100")
        
        # Key insights
        insights = []
        
        # Valuation
        if 'per_interpretation' in analysis:
            insights.append(f"• PER: {analysis['per_interpretation']}")
        
        if 'pbr_interpretation' in analysis:
            insights.append(f"• PBR: {analysis['pbr_interpretation']}")
        
        # Profitability
        if 'roe_interpretation' in analysis:
            insights.append(f"• ROE: {analysis['roe_interpretation']}")
        
        # Financial health
        if 'debt_to_equity_interpretation' in analysis:
            insights.append(f"• 부채비율: {analysis['debt_to_equity_interpretation']}")
        
        # Growth
        if 'revenue_growth_interpretation' in analysis:
            insights.append(f"• 매출성장: {analysis['revenue_growth_interpretation']}")
        
        if insights:
            st.markdown("\n".join(insights))
    
    def display_economic_indicators(self, indicators: Dict[str, Any]):
        """Display economic indicators."""
        st.subheader("🌍 경제 지표")
        
        # Filter and format indicators
        display_indicators = {}
        for key, value in indicators.items():
            if not key.endswith('_raw') and value not in ["정보 없음", "N/A", None]:
                display_indicators[key] = value
        
        if display_indicators:
            # Create a grid layout
            cols = st.columns(2)
            
            for i, (key, value) in enumerate(display_indicators.items()):
                with cols[i % 2]:
                    # Determine if it's a change indicator
                    if "전년대비" in key:
                        try:
                            change_val = float(value.replace('%', ''))
                            delta_color = "normal" if abs(change_val) < 0.1 else "inverse"
                            st.metric(
                                label=key,
                                value=value,
                                delta=value,
                                delta_color=delta_color
                            )
                        except:
                            st.metric(label=key, value=value)
                    else:
                        st.metric(label=key, value=value)
        else:
            st.info("경제 지표 데이터가 없습니다.")
        
        # Overall economic assessment
        if '경제상황_종합평가' in indicators:
            assessment = indicators['경제상황_종합평가']
            assessment_color = self._get_sentiment_color(assessment)
            st.markdown(
                f"<p style='font-size: 18px; color: {assessment_color};'>"
                f"종합 평가: <strong>{assessment}</strong></p>",
                unsafe_allow_html=True
            )
    
    def display_recommendations_table(self, recommendations: pd.DataFrame, title: str):
        """Display recommendations in a formatted table."""
        st.subheader(title)
        
        if recommendations.empty:
            st.info("추천 종목이 없습니다.")
            return
        
        # Format numeric columns
        for col in recommendations.columns:
            if recommendations[col].dtype in ['float64', 'int64']:
                if 'price' in col.lower() or '가격' in col:
                    recommendations[col] = recommendations[col].apply(
                        lambda x: self.price_formatter.format_price(x)
                    )
                elif 'volume' in col.lower() or '거래량' in col:
                    recommendations[col] = recommendations[col].apply(
                        lambda x: self.price_formatter.format_volume(x)
                    )
                elif col in ['PER', 'PBR']:
                    recommendations[col] = recommendations[col].apply(
                        lambda x: self.price_formatter.format_ratio(x)
                    )
        
        # Display table
        st.dataframe(
            recommendations,
            use_container_width=True,
            hide_index=True
        )
    
    def display_analysis_summary(self, summary: Dict[str, Any]):
        """Display analysis summary with key takeaways."""
        st.subheader("📋 분석 요약")
        
        # Technical score
        tech_score = summary.get('technical_score', 50)
        fund_score = summary.get('fundamental_score', 50)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="기술적 분석 점수",
                value=f"{tech_score}/100",
                delta=self._get_score_interpretation(tech_score)
            )
        
        with col2:
            st.metric(
                label="기본적 분석 점수",
                value=f"{fund_score}/100",
                delta=self._get_score_interpretation(fund_score)
            )
        
        # Overall recommendation
        overall_score = (tech_score + fund_score) / 2
        recommendation = self._get_overall_recommendation(overall_score)
        
        st.markdown(f"### 종합 추천: **{recommendation}**")
        
        # Key points
        if 'key_points' in summary:
            st.markdown("### 주요 포인트")
            for point in summary['key_points']:
                st.markdown(f"• {point}")
    
    # Helper methods
    
    def _display_professional_metric_card(self, key: str, value: Any):
        """Display a professional metric card with glassmorphism design."""
        # Format value based on key
        if key in ["현재가", "52주 최고가", "52주 최저가"]:
            formatted_value = self.price_formatter.format_price(value)
            delta = None
        elif key == "시가총액":
            formatted_value = self.price_formatter.format_market_cap(value)
            delta = None
        elif key == "거래량":
            formatted_value = self.price_formatter.format_volume(value)
            delta = None
        elif key in ["PER", "PBR"]:
            formatted_value = self.price_formatter.format_ratio(value)
            # Add delta for valuation metrics
            if key == "PER":
                if isinstance(value, (int, float)) and value > 0:
                    if value < 15:
                        delta = "저평가"
                    elif value > 25:
                        delta = "고평가"
                    else:
                        delta = "적정"
            elif key == "PBR":
                if isinstance(value, (int, float)) and value > 0:
                    if value < 1:
                        delta = "저평가"
                    elif value > 2:
                        delta = "고평가"
                    else:
                        delta = "적정"
        elif key in ["ROE", "배당수익률"]:
            formatted_value = self.data_formatter.format_percentage(value)
            # Add interpretation for performance metrics
            if key == "ROE":
                if isinstance(value, (int, float)):
                    if value > 15:
                        delta = "우수"
                    elif value > 10:
                        delta = "양호"
                    else:
                        delta = "보통"
        else:
            formatted_value = self.data_formatter.safe_format_number(value)
            delta = None
        
        # Create professional metric card using ProfessionalTheme
        ProfessionalTheme.create_metric_card(
            title=key,
            value=formatted_value,
            delta=delta
        )
    
    def _display_single_metric(self, key: str, value: Any):
        """Display a single metric with appropriate formatting."""
        # Format value based on key
        if key in ["현재가", "52주 최고가", "52주 최저가"]:
            formatted_value = self.price_formatter.format_price(value)
        elif key == "시가총액":
            formatted_value = self.price_formatter.format_market_cap(value)
        elif key == "거래량":
            formatted_value = self.price_formatter.format_volume(value)
        elif key in ["PER", "PBR"]:
            formatted_value = self.price_formatter.format_ratio(value)
        elif key in ["ROE", "배당수익률"]:
            formatted_value = self.data_formatter.format_percentage(value)
        else:
            formatted_value = self.data_formatter.safe_format_number(value)
        
        st.metric(label=key, value=formatted_value)
    
    def _display_indicator(self, key: str, value: Any):
        """Display a technical indicator."""
        # Format indicator name
        display_name = {
            'sma_20': '20일 이동평균',
            'sma_50': '50일 이동평균',
            'sma_200': '200일 이동평균',
            'rsi': 'RSI',
            'macd_line': 'MACD',
            'atr': 'ATR',
            'historical_volatility': '역사적 변동성',
            'volume_ratio_20': '20일 거래량 비율',
            'trend_direction': '추세 방향',
            'momentum_signal': '모멘텀 신호',
            'volume_signal': '거래량 신호',
        }.get(key, key)
        
        # Format value
        if isinstance(value, str):
            formatted_value = value
        elif key in ['historical_volatility']:
            formatted_value = self.data_formatter.format_percentage(value)
        elif key.endswith('_ratio'):
            formatted_value = f"{value:.2f}x"
        else:
            formatted_value = self.data_formatter.safe_format_number(value, 2)
        
        st.metric(label=display_name, value=formatted_value)
    
    def _get_grade_color(self, grade: str) -> str:
        """Get color for investment grade."""
        if 'A' in grade:
            return '#2ca02c'  # Green
        elif 'B' in grade:
            return '#ff7f0e'  # Orange
        elif 'C' in grade:
            return '#ff9800'  # Warning
        else:
            return '#d62728'  # Red
    
    def _get_sentiment_color(self, sentiment: str) -> str:
        """Get color for sentiment."""
        if '긍정' in sentiment:
            return '#2ca02c'
        elif '부정' in sentiment:
            return '#d62728'
        else:
            return '#666666'
    
    def _get_score_interpretation(self, score: float) -> str:
        """Get interpretation for score."""
        if score >= 80:
            return "매우 긍정적"
        elif score >= 60:
            return "긍정적"
        elif score >= 40:
            return "중립적"
        elif score >= 20:
            return "부정적"
        else:
            return "매우 부정적"
    
    def _get_overall_recommendation(self, score: float) -> str:
        """Get overall recommendation based on score."""
        if score >= 80:
            return "강력 매수 💚"
        elif score >= 65:
            return "매수 🟢"
        elif score >= 50:
            return "보유 🟡"
        elif score >= 35:
            return "매도 🟠"
        else:
            return "강력 매도 🔴"