"""
Dashboard Component

Provides a modern dashboard-style main screen with real-time updates and interactive elements.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DashboardManager:
    """Manages the main dashboard interface."""
    
    def __init__(self):
        self.theme = self._get_theme()
        
    def _get_theme(self) -> Dict[str, Any]:
        """Get current theme settings."""
        return {
            'primary': '#3B82F6',
            'success': '#10B981',
            'danger': '#EF4444',
            'warning': '#F59E0B',
            'info': '#06B6D4',
            'background': '#F9FAFB',
            'card_bg': '#FFFFFF',
            'text_primary': '#111827',
            'text_secondary': '#6B7280'
        }
    
    def render_welcome_dashboard(self):
        """Render the welcome dashboard when no analysis is active."""
        # Hero Section
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 1rem; 
                       background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;">
                AI 투자 분석 플랫폼
            </h1>
            <p style="font-size: 1.25rem; color: #6B7280; max-width: 600px; margin: 0 auto;">
                인공지능이 제공하는 심층적인 주식 분석으로<br>
                더 나은 투자 결정을 내리세요
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards
        col1, col2, col3, col4 = st.columns(4)
        
        features = [
            {
                "icon": "🤖",
                "title": "AI 멀티 에이전트",
                "description": "5개의 전문 AI가 협업",
                "color": self.theme['primary']
            },
            {
                "icon": "📊",
                "title": "기술적 분석",
                "description": "20+ 기술 지표 분석",
                "color": self.theme['success']
            },
            {
                "icon": "💰",
                "title": "펀더멘털 분석",
                "description": "재무제표 심층 분석",
                "color": self.theme['warning']
            },
            {
                "icon": "🌍",
                "title": "거시경제 분석",
                "description": "글로벌 경제 영향 평가",
                "color": self.theme['info']
            }
        ]
        
        for col, feature in zip([col1, col2, col3, col4], features):
            with col:
                self._render_feature_card(feature)
        
        # Market Overview Section
        st.markdown("---")
        st.markdown("### 📈 오늘의 시장 동향")
        self._render_market_overview()
        
        # Popular Stocks Section
        st.markdown("### 🔥 인기 종목")
        self._render_popular_stocks()
    
    def _render_feature_card(self, feature: Dict[str, str]):
        """Render a feature card."""
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.5rem; 
                    border: 1px solid #E5E7EB; text-align: center; height: 180px;
                    transition: all 0.3s ease; cursor: pointer;"
             onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 10px 25px -5px rgba(0,0,0,0.1)';"
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{feature['icon']}</div>
            <h4 style="margin: 0.5rem 0; color: {feature['color']}; font-weight: 600;">
                {feature['title']}
            </h4>
            <p style="margin: 0; color: #6B7280; font-size: 0.875rem;">
                {feature['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_market_overview(self):
        """Render market overview cards."""
        # Mock market data (in real app, fetch from API)
        markets = [
            {"name": "S&P 500", "value": 4783.45, "change": 0.73, "icon": "🇺🇸"},
            {"name": "NASDAQ", "value": 15123.68, "change": 1.25, "icon": "📱"},
            {"name": "KOSPI", "value": 2501.34, "change": -0.42, "icon": "🇰🇷"},
            {"name": "원/달러", "value": 1301.50, "change": -0.15, "icon": "💱"}
        ]
        
        cols = st.columns(len(markets))
        for col, market in zip(cols, markets):
            with col:
                change_color = self.theme['success'] if market['change'] >= 0 else self.theme['danger']
                arrow = "↑" if market['change'] >= 0 else "↓"
                
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 1rem;
                           border: 1px solid #E5E7EB;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 1.5rem;">{market['icon']}</span>
                        <span style="color: {change_color}; font-weight: 600;">
                            {arrow} {abs(market['change']):.2f}%
                        </span>
                    </div>
                    <h5 style="margin: 0.5rem 0 0.25rem 0; color: #374151;">
                        {market['name']}
                    </h5>
                    <p style="margin: 0; font-size: 1.125rem; font-weight: 600;">
                        {market['value']:,.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_popular_stocks(self):
        """Render popular stocks section."""
        # Mock popular stocks data
        popular_stocks = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA'],
            'Name': ['Apple', 'Microsoft', 'NVIDIA', 'Google', 'Tesla'],
            'Price': [195.89, 429.68, 878.35, 153.75, 238.45],
            'Change': [2.34, -0.87, 5.21, 1.45, -3.12],
            'Volume': ['52.3M', '23.1M', '45.7M', '18.9M', '112.4M']
        })
        
        # Create interactive table
        for _, stock in popular_stocks.iterrows():
            change_color = self.theme['success'] if stock['Change'] >= 0 else self.theme['danger']
            arrow = "↑" if stock['Change'] >= 0 else "↓"
            
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
                       border: 1px solid #E5E7EB; cursor: pointer; transition: all 0.2s ease;"
                 onmouseover="this.style.background='#F9FAFB';"
                 onmouseout="this.style.background='white';">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: 600; font-size: 1rem;">{stock['Symbol']}</span>
                        <span style="color: #6B7280; margin-left: 0.5rem;">{stock['Name']}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600;">${stock['Price']:.2f}</div>
                        <div style="color: {change_color}; font-size: 0.875rem;">
                            {arrow} {abs(stock['Change']):.2f}%
                        </div>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; color: #6B7280; font-size: 0.75rem;">
                    거래량: {stock['Volume']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_analysis_dashboard(
        self,
        ticker: str,
        analysis_data: Dict[str, Any],
        price_history: pd.DataFrame,
        agent_results: Dict[str, str]
    ):
        """Render the main analysis dashboard."""
        # Summary metrics row
        self._render_summary_metrics(analysis_data)
        
        # Main content area with tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 차트 분석",
            "💼 펀더멘털",
            "🤖 AI 인사이트",
            "📰 뉴스 & 이벤트"
        ])
        
        with tab1:
            self._render_chart_analysis(price_history, ticker, analysis_data)
        
        with tab2:
            self._render_fundamental_analysis(analysis_data)
        
        with tab3:
            self._render_ai_insights(agent_results)
        
        with tab4:
            self._render_news_events(ticker)
    
    def _render_summary_metrics(self, analysis_data: Dict[str, Any]):
        """Render summary metrics at the top of dashboard."""
        stock_info = analysis_data.get('stock_info', {})
        technical = analysis_data.get('technical_analysis', {})
        
        # Calculate overall score
        technical_score = technical.get('technical_score', 50)
        fundamental_score = analysis_data.get('fundamental_analysis', {}).get('fundamental_score', 50)
        overall_score = (technical_score + fundamental_score) / 2
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Overall Score
        with col1:
            score_color = (
                self.theme['success'] if overall_score >= 70 else
                self.theme['warning'] if overall_score >= 40 else
                self.theme['danger']
            )
            self._render_metric_card(
                "종합 점수",
                f"{overall_score:.0f}/100",
                score_color,
                "🎯"
            )
        
        # Technical Score
        with col2:
            self._render_metric_card(
                "기술적 점수",
                f"{technical_score:.0f}/100",
                self.theme['primary'],
                "📊"
            )
        
        # Fundamental Score
        with col3:
            self._render_metric_card(
                "펀더멘털 점수",
                f"{fundamental_score:.0f}/100",
                self.theme['info'],
                "💰"
            )
        
        # Volatility
        with col4:
            volatility = technical.get('historical_volatility', 0) * 100
            vol_color = (
                self.theme['success'] if volatility < 20 else
                self.theme['warning'] if volatility < 40 else
                self.theme['danger']
            )
            self._render_metric_card(
                "변동성",
                f"{volatility:.1f}%",
                vol_color,
                "📈"
            )
        
        # Trend
        with col5:
            trend = technical.get('trend_direction', 'sideways')
            trend_map = {
                'strong_uptrend': ('강한 상승', self.theme['success'], '🚀'),
                'uptrend': ('상승', self.theme['success'], '↗️'),
                'sideways': ('횡보', self.theme['warning'], '→'),
                'downtrend': ('하락', self.theme['danger'], '↘️'),
                'strong_downtrend': ('강한 하락', self.theme['danger'], '📉')
            }
            trend_text, trend_color, trend_icon = trend_map.get(
                trend, ('분석중', self.theme['info'], '🔄')
            )
            self._render_metric_card(
                "추세",
                trend_text,
                trend_color,
                trend_icon
            )
    
    def _render_metric_card(self, label: str, value: str, color: str, icon: str):
        """Render a single metric card."""
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 1rem;
                   border: 1px solid #E5E7EB; text-align: center;">
            <div style="color: #6B7280; font-size: 0.75rem; text-transform: uppercase;">
                {label}
            </div>
            <div style="display: flex; align-items: center; justify-content: center; margin-top: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <span style="font-size: 1.25rem; font-weight: 600; color: {color};">
                    {value}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_chart_analysis(self, price_history: pd.DataFrame, ticker: str, analysis_data: Dict[str, Any]):
        """Render chart analysis tab."""
        # Price chart with technical indicators
        fig = self._create_advanced_chart(price_history, ticker, analysis_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical indicators summary
        st.markdown("### 기술적 지표 요약")
        technical = analysis_data.get('technical_analysis', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_indicator_summary("모멘텀 지표", {
                "RSI": technical.get('rsi', 50),
                "MACD": technical.get('macd_histogram', 0),
                "Stochastic": technical.get('stoch_k', 50)
            })
        
        with col2:
            self._render_indicator_summary("이동평균선", {
                "SMA 20": technical.get('sma_20', 0),
                "SMA 50": technical.get('sma_50', 0),
                "SMA 200": technical.get('sma_200', 0)
            })
    
    def _create_advanced_chart(self, df: pd.DataFrame, ticker: str, analysis_data: Dict[str, Any]) -> go.Figure:
        """Create an advanced interactive chart."""
        from plotly.subplots import make_subplots
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f"{ticker} 가격 차트", "RSI", "거래량")
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='가격',
                increasing_line_color=self.theme['success'],
                decreasing_line_color=self.theme['danger']
            ),
            row=1, col=1
        )
        
        # Add Bollinger Bands if available
        technical = analysis_data.get('technical_analysis', {})
        if all(key in technical for key in ['bb_upper', 'bb_middle', 'bb_lower']):
            # Note: We need the full series, not just last values
            # This is a simplified version
            window = 20
            rolling_mean = df['Close'].rolling(window).mean()
            rolling_std = df['Close'].rolling(window).std()
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=rolling_mean + (rolling_std * 2),
                    name='BB Upper',
                    line=dict(color='rgba(250, 128, 114, 0.5)', width=1),
                    fill=None
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=rolling_mean - (rolling_std * 2),
                    name='BB Lower',
                    line=dict(color='rgba(250, 128, 114, 0.5)', width=1),
                    fill='tonexty',
                    fillcolor='rgba(250, 128, 114, 0.1)'
                ),
                row=1, col=1
            )
        
        # RSI
        def calculate_rsi(prices, period=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        rsi = calculate_rsi(df['Close'])
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                name='RSI',
                line=dict(color=self.theme['primary'], width=2)
            ),
            row=2, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Volume
        volume_colors = [
            self.theme['success'] if df['Close'].iloc[i] >= df['Open'].iloc[i] 
            else self.theme['danger'] 
            for i in range(len(df))
        ]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='거래량',
                marker_color=volume_colors,
                showlegend=False
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_xaxes(rangeslider_visible=False)
        fig.update_yaxes(title_text="가격", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="거래량", row=3, col=1)
        
        return fig
    
    def _render_indicator_summary(self, title: str, indicators: Dict[str, float]):
        """Render indicator summary card."""
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 1rem;
                   border: 1px solid #E5E7EB;">
            <h4 style="margin: 0 0 1rem 0; color: #374151;">{title}</h4>
        """, unsafe_allow_html=True)
        
        for name, value in indicators.items():
            if isinstance(value, (int, float)):
                # Determine signal based on indicator
                if "RSI" in name:
                    signal = "과매수" if value > 70 else "과매도" if value < 30 else "중립"
                    color = self.theme['danger'] if value > 70 else self.theme['success'] if value < 30 else self.theme['info']
                elif "MACD" in name:
                    signal = "상승" if value > 0 else "하락"
                    color = self.theme['success'] if value > 0 else self.theme['danger']
                else:
                    signal = ""
                    color = self.theme['text_primary']
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #6B7280;">{name}</span>
                    <span style="font-weight: 600; color: {color};">
                        {value:.2f} {signal}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def _render_fundamental_analysis(self, analysis_data: Dict[str, Any]):
        """Render fundamental analysis tab."""
        fundamental = analysis_data.get('fundamental_analysis', {})
        stock_info = analysis_data.get('stock_info', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 재무 지표")
            metrics = {
                "PER": stock_info.get('PER', 'N/A'),
                "PBR": stock_info.get('PBR', 'N/A'),
                "ROE": fundamental.get('roe', 'N/A'),
                "부채비율": fundamental.get('debt_ratio', 'N/A')
            }
            
            for metric, value in metrics.items():
                if value != 'N/A' and isinstance(value, (int, float)):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)
                
                st.markdown(f"""
                <div style="background: #F9FAFB; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #6B7280;">{metric}</span>
                        <span style="font-weight: 600;">{value_str}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 💰 수익성 분석")
            
            # Create a simple gauge chart for profitability
            profitability_score = fundamental.get('profitability_score', 50)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=profitability_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "수익성 점수"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.theme['primary']},
                    'steps': [
                        {'range': [0, 40], 'color': "#FEE2E2"},
                        {'range': [40, 70], 'color': "#FEF3C7"},
                        {'range': [70, 100], 'color': "#D1FAE5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_ai_insights(self, agent_results: Dict[str, str]):
        """Render AI insights tab."""
        # Create a sentiment analysis from agent results
        sentiments = self._analyze_agent_sentiments(agent_results)
        
        # Sentiment overview
        st.markdown("### 🎯 AI 종합 의견")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            positive_pct = sentiments['positive'] / sentiments['total'] * 100
            st.markdown(f"""
            <div style="background: #D1FAE5; border-radius: 8px; padding: 1.5rem; text-align: center;">
                <h3 style="color: {self.theme['success']}; margin: 0;">긍정적</h3>
                <p style="font-size: 2rem; font-weight: 600; margin: 0.5rem 0;">
                    {positive_pct:.0f}%
                </p>
                <p style="color: #6B7280; margin: 0;">
                    {sentiments['positive']}명의 에이전트
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            neutral_pct = sentiments['neutral'] / sentiments['total'] * 100
            st.markdown(f"""
            <div style="background: #FEF3C7; border-radius: 8px; padding: 1.5rem; text-align: center;">
                <h3 style="color: {self.theme['warning']}; margin: 0;">중립적</h3>
                <p style="font-size: 2rem; font-weight: 600; margin: 0.5rem 0;">
                    {neutral_pct:.0f}%
                </p>
                <p style="color: #6B7280; margin: 0;">
                    {sentiments['neutral']}명의 에이전트
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            negative_pct = sentiments['negative'] / sentiments['total'] * 100
            st.markdown(f"""
            <div style="background: #FEE2E2; border-radius: 8px; padding: 1.5rem; text-align: center;">
                <h3 style="color: {self.theme['danger']}; margin: 0;">부정적</h3>
                <p style="font-size: 2rem; font-weight: 600; margin: 0.5rem 0;">
                    {negative_pct:.0f}%
                </p>
                <p style="color: #6B7280; margin: 0;">
                    {sentiments['negative']}명의 에이전트
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key insights
        st.markdown("### 💡 주요 인사이트")
        insights = self._extract_key_insights(agent_results)
        
        for insight in insights:
            st.markdown(f"""
            <div style="background: white; border-left: 4px solid {self.theme['primary']}; 
                       padding: 1rem; margin-bottom: 0.5rem; border-radius: 4px;">
                <p style="margin: 0; color: #374151;">• {insight}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _analyze_agent_sentiments(self, agent_results: Dict[str, str]) -> Dict[str, int]:
        """Analyze sentiments from agent results."""
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0, 'total': 0}
        
        positive_keywords = ['매수', '긍정', '상승', '성장', '유망', '추천']
        negative_keywords = ['매도', '부정', '하락', '위험', '우려', '회피']
        
        for agent, analysis in agent_results.items():
            if agent == "중재자":
                continue
                
            sentiments['total'] += 1
            
            # Simple keyword-based sentiment analysis
            text = analysis.lower()
            positive_score = sum(1 for keyword in positive_keywords if keyword in text)
            negative_score = sum(1 for keyword in negative_keywords if keyword in text)
            
            if positive_score > negative_score:
                sentiments['positive'] += 1
            elif negative_score > positive_score:
                sentiments['negative'] += 1
            else:
                sentiments['neutral'] += 1
        
        return sentiments
    
    def _extract_key_insights(self, agent_results: Dict[str, str]) -> List[str]:
        """Extract key insights from agent analyses."""
        insights = []
        
        # Extract first key point from each agent
        for agent, analysis in agent_results.items():
            if agent == "중재자":
                continue
            
            # Find first bullet point or key statement
            lines = analysis.split('\n')
            for line in lines:
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    insight = line.strip().lstrip('•-').strip()
                    if insight and len(insight) > 20:
                        insights.append(f"{agent}: {insight}")
                        break
        
        return insights[:5]  # Return top 5 insights
    
    def _render_news_events(self, ticker: str):
        """Render news and events tab."""
        st.markdown("### 📰 최신 뉴스")
        
        # Mock news data (in real app, fetch from news API)
        news_items = [
            {
                "title": f"{ticker} Q4 실적 발표 예정",
                "date": "2024-01-15",
                "sentiment": "neutral",
                "source": "Reuters"
            },
            {
                "title": f"{ticker} 신제품 출시로 주가 상승 기대",
                "date": "2024-01-14",
                "sentiment": "positive",
                "source": "Bloomberg"
            },
            {
                "title": f"애널리스트, {ticker} 목표가 상향 조정",
                "date": "2024-01-13",
                "sentiment": "positive",
                "source": "CNBC"
            }
        ]
        
        for news in news_items:
            sentiment_color = {
                'positive': self.theme['success'],
                'negative': self.theme['danger'],
                'neutral': self.theme['info']
            }.get(news['sentiment'], self.theme['info'])
            
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 1rem; 
                       margin-bottom: 0.5rem; border: 1px solid #E5E7EB;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #111827;">
                            {news['title']}
                        </h4>
                        <p style="margin: 0; color: #6B7280; font-size: 0.875rem;">
                            {news['source']} • {news['date']}
                        </p>
                    </div>
                    <div style="width: 8px; height: 8px; border-radius: 50%; 
                               background: {sentiment_color}; margin-top: 0.5rem;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)