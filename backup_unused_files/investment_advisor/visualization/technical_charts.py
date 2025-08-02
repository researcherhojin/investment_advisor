"""
Technical Analysis Visualization Module

Provides interactive charts for technical analysis.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import streamlit as st


class TechnicalChartGenerator:
    """Generate technical analysis charts."""
    
    def __init__(self):
        self.chart_height = 600
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8',
            'background': '#f8f9fa',
            'grid': '#e0e0e0'
        }
    
    def create_price_chart_with_indicators(
        self, 
        df: pd.DataFrame,
        indicators: Dict[str, Any],
        ticker: str
    ) -> go.Figure:
        """Create comprehensive price chart with technical indicators."""
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=(
                f'{ticker} 주가 및 이동평균선',
                'RSI (Relative Strength Index)',
                'MACD',
                '거래량'
            )
        )
        
        # 1. Price and Moving Averages
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='가격',
                increasing_line_color=self.colors['success'],
                decreasing_line_color=self.colors['danger']
            ),
            row=1, col=1
        )
        
        # Add moving averages if available
        if 'sma_20' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[indicators['sma_20']] * len(df),
                    mode='lines',
                    name='SMA 20',
                    line=dict(color=self.colors['primary'], width=2)
                ),
                row=1, col=1
            )
        
        if 'sma_50' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[indicators['sma_50']] * len(df),
                    mode='lines',
                    name='SMA 50',
                    line=dict(color=self.colors['secondary'], width=2)
                ),
                row=1, col=1
            )
        
        if 'sma_200' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[indicators['sma_200']] * len(df),
                    mode='lines',
                    name='SMA 200',
                    line=dict(color=self.colors['danger'], width=2)
                ),
                row=1, col=1
            )
        
        # Add Bollinger Bands
        if all(k in indicators for k in ['bb_upper', 'bb_lower', 'bb_middle']):
            # Upper band
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[indicators['bb_upper']] * len(df),
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash')
                ),
                row=1, col=1
            )
            
            # Lower band
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[indicators['bb_lower']] * len(df),
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)'
                ),
                row=1, col=1
            )
        
        # Add support/resistance levels
        if 'support_level' in indicators:
            fig.add_hline(
                y=indicators['support_level'],
                line_dash="dot",
                line_color=self.colors['success'],
                annotation_text=f"지지선: {indicators['support_level']:.2f}",
                row=1, col=1
            )
        
        if 'resistance_level' in indicators:
            fig.add_hline(
                y=indicators['resistance_level'],
                line_dash="dot", 
                line_color=self.colors['danger'],
                annotation_text=f"저항선: {indicators['resistance_level']:.2f}",
                row=1, col=1
            )
        
        # 2. RSI
        if 'rsi' in indicators:
            # Calculate RSI values over time (simplified)
            rsi_values = self._calculate_rsi_series(df['Close'])
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=rsi_values,
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.colors['info'], width=2)
                ),
                row=2, col=1
            )
            
            # RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
        
        # 3. MACD
        if all(k in indicators for k in ['macd', 'macd_signal', 'macd_diff']):
            macd_values = self._calculate_macd_series(df['Close'])
            
            # MACD line
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=macd_values['macd'],
                    mode='lines',
                    name='MACD',
                    line=dict(color=self.colors['primary'], width=2)
                ),
                row=3, col=1
            )
            
            # Signal line
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=macd_values['signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color=self.colors['secondary'], width=2)
                ),
                row=3, col=1
            )
            
            # Histogram
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=macd_values['histogram'],
                    name='Histogram',
                    marker_color=np.where(macd_values['histogram'] > 0, 
                                         self.colors['success'], 
                                         self.colors['danger'])
                ),
                row=3, col=1
            )
        
        # 4. Volume
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                  for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='거래량',
                marker_color=colors
            ),
            row=4, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=self.chart_height,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            title={
                'text': f'{ticker} 기술적 분석 차트',
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="가격", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="거래량", row=4, col=1)
        
        # Update x-axis
        fig.update_xaxes(title_text="날짜", row=4, col=1)
        
        return fig
    
    def create_indicator_summary(self, indicators: Dict[str, Any]) -> go.Figure:
        """Create a visual summary of technical indicators."""
        
        # Create gauge charts for key metrics
        fig = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=('RSI', 'Volatility', 'Trend Strength')
        )
        
        # RSI Gauge
        rsi_value = indicators.get('rsi', 50)
        rsi_color = (self.colors['danger'] if rsi_value > 70 else 
                    self.colors['success'] if rsi_value < 30 else 
                    self.colors['warning'])
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=rsi_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "RSI"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': rsi_color},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 70], 'color': "lightyellow"},
                        {'range': [70, 100], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ),
            row=1, col=1
        )
        
        # Volatility Gauge
        volatility = indicators.get('volatility', 0.2) * 100  # Convert to percentage
        vol_color = (self.colors['danger'] if volatility > 30 else 
                    self.colors['warning'] if volatility > 20 else 
                    self.colors['success'])
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=volatility,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "변동성 (%)"},
                gauge={
                    'axis': {'range': [0, 50]},
                    'bar': {'color': vol_color},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgreen"},
                        {'range': [20, 30], 'color': "lightyellow"},
                        {'range': [30, 50], 'color': "lightcoral"}
                    ]
                }
            ),
            row=1, col=2
        )
        
        # Trend Strength (based on moving averages)
        trend_score = self._calculate_trend_strength(indicators)
        trend_color = (self.colors['success'] if trend_score > 60 else 
                      self.colors['danger'] if trend_score < 40 else 
                      self.colors['warning'])
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=trend_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "추세 강도"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': trend_color},
                    'steps': [
                        {'range': [0, 40], 'color': "lightcoral"},
                        {'range': [40, 60], 'color': "lightyellow"},
                        {'range': [60, 100], 'color': "lightgreen"}
                    ]
                }
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            template='plotly_white',
            title={
                'text': '기술적 지표 요약',
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        
        return fig
    
    def _calculate_rsi_series(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI values over time."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd_series(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calculate MACD values over time."""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }
    
    def _calculate_trend_strength(self, indicators: Dict[str, Any]) -> float:
        """Calculate trend strength based on multiple indicators."""
        score = 50  # Neutral start
        
        # Check moving averages alignment
        sma_20 = indicators.get('sma_20', 0)
        sma_50 = indicators.get('sma_50', 0)
        sma_200 = indicators.get('sma_200', 0)
        
        if sma_20 > sma_50 > sma_200:
            score += 20  # Strong uptrend
        elif sma_20 < sma_50 < sma_200:
            score -= 20  # Strong downtrend
        
        # Check MACD
        macd_diff = indicators.get('macd_diff', 0)
        if macd_diff > 0:
            score += 10
        else:
            score -= 10
        
        # Check RSI
        rsi = indicators.get('rsi', 50)
        if 40 < rsi < 60:
            score += 10  # Healthy range
        elif rsi > 70 or rsi < 30:
            score -= 10  # Overbought/oversold
        
        return max(0, min(100, score))
    
    def display_technical_analysis(
        self, 
        df: pd.DataFrame,
        indicators: Dict[str, Any],
        ticker: str,
        container = None
    ):
        """Display complete technical analysis with charts."""
        
        if container is None:
            container = st
        
        # Display indicator summary first
        container.subheader("📊 기술적 지표 요약")
        summary_fig = self.create_indicator_summary(indicators)
        container.plotly_chart(summary_fig, use_container_width=True)
        
        # Display main technical chart
        container.subheader("📈 기술적 분석 차트")
        main_fig = self.create_price_chart_with_indicators(df, indicators, ticker)
        container.plotly_chart(main_fig, use_container_width=True)
        
        # Display key levels and signals
        col1, col2, col3 = container.columns(3)
        
        with col1:
            st.metric(
                "현재 추세",
                "상승" if indicators.get('macd_diff', 0) > 0 else "하락",
                f"{indicators.get('macd_diff', 0):.2f}"
            )
            
        with col2:
            st.metric(
                "지지/저항선",
                f"S: {indicators.get('support_level', 0):.2f}",
                f"R: {indicators.get('resistance_level', 0):.2f}"
            )
            
        with col3:
            rsi = indicators.get('rsi', 50)
            rsi_signal = "과매수" if rsi > 70 else "과매도" if rsi < 30 else "중립"
            st.metric(
                "RSI 신호",
                rsi_signal,
                f"{rsi:.1f}"
            )