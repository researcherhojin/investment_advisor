"""
Chart Generation Module

Creates interactive charts for stock analysis.
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate interactive charts for stock analysis."""
    
    def __init__(self, theme: str = "plotly_dark"):
        self.theme = theme
        self.default_height = 800
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#4ECDC4',
            'success': '#26C6DA',
            'danger': '#FF5722',
            'warning': '#FFB74D',
            'info': '#667eea',
            'up': '#4ECDC4',
            'down': '#FF5722',
            'text': '#FFFFFF',
            'background': 'rgba(0,0,0,0)',
            'grid': 'rgba(255,255,255,0.1)',
        }
    
    def create_main_chart(
        self,
        df: pd.DataFrame,
        ticker: str,
        market: str,
        technical_data: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create comprehensive main chart with price, volume, and indicators.
        
        Args:
            df: Price history DataFrame
            ticker: Stock ticker
            market: Market identifier
            technical_data: Optional technical analysis data
            
        Returns:
            Plotly figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(
                f'{ticker} 주가 차트',
                'MACD',
                'RSI',
                '거래량'
            ),
            row_heights=[0.5, 0.2, 0.15, 0.15]
        )
        
        # 1. Candlestick chart
        self._add_candlestick(fig, df, row=1, col=1)
        
        # 2. Moving averages
        self._add_moving_averages(fig, df, row=1, col=1)
        
        # 3. Bollinger Bands
        self._add_bollinger_bands(fig, df, row=1, col=1)
        
        # 4. Support/Resistance lines
        if technical_data:
            self._add_support_resistance(fig, technical_data, row=1, col=1)
        
        # 5. MACD
        self._add_macd(fig, df, row=2, col=1)
        
        # 6. RSI
        self._add_rsi(fig, df, row=3, col=1)
        
        # 7. Volume
        self._add_volume(fig, df, row=4, col=1)
        
        # Update layout
        self._update_main_chart_layout(fig, ticker, market)
        
        # Add entrance animation
        self._add_chart_animations(fig)
        
        return fig
    
    def create_technical_indicators_chart(
        self,
        df: pd.DataFrame,
        indicators: List[str]
    ) -> go.Figure:
        """Create chart with selected technical indicators."""
        rows = len(indicators)
        if rows == 0:
            return go.Figure()
        
        # Create subplots
        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=indicators
        )
        
        # Add each indicator
        for i, indicator in enumerate(indicators, 1):
            if indicator == "Price":
                self._add_price_line(fig, df, row=i, col=1)
            elif indicator == "MACD":
                self._add_macd(fig, df, row=i, col=1)
            elif indicator == "RSI":
                self._add_rsi(fig, df, row=i, col=1)
            elif indicator == "Stochastic":
                self._add_stochastic(fig, df, row=i, col=1)
            elif indicator == "ATR":
                self._add_atr(fig, df, row=i, col=1)
            elif indicator == "OBV":
                self._add_obv(fig, df, row=i, col=1)
        
        # Update layout
        fig.update_layout(
            height=200 * rows,
            template=self.theme,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_performance_chart(
        self,
        df: pd.DataFrame,
        benchmark_df: Optional[pd.DataFrame] = None,
        ticker: str = "Stock"
    ) -> go.Figure:
        """Create performance comparison chart."""
        fig = go.Figure()
        
        # Calculate cumulative returns
        stock_returns = (df['Close'].pct_change() + 1).cumprod() - 1
        
        # Add stock performance
        fig.add_trace(go.Scatter(
            x=df.index,
            y=stock_returns * 100,
            mode='lines',
            name=ticker,
            line=dict(color=self.colors['primary'], width=2)
        ))
        
        # Add benchmark if provided
        if benchmark_df is not None and not benchmark_df.empty:
            bench_returns = (benchmark_df['Close'].pct_change() + 1).cumprod() - 1
            fig.add_trace(go.Scatter(
                x=benchmark_df.index,
                y=bench_returns * 100,
                mode='lines',
                name='벤치마크',
                line=dict(color=self.colors['secondary'], width=2, dash='dash')
            ))
        
        # Update layout
        fig.update_layout(
            title='누적 수익률 비교',
            xaxis_title='날짜',
            yaxis_title='수익률 (%)',
            template=self.theme,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_sector_performance_chart(
        self,
        sector_data: pd.DataFrame
    ) -> go.Figure:
        """Create sector performance bar chart."""
        fig = go.Figure()
        
        # Sort by performance
        sorted_data = sector_data.sort_values('Performance', ascending=True)
        
        # Color based on positive/negative
        colors = [
            self.colors['up'] if perf > 0 else self.colors['down']
            for perf in sorted_data['Performance']
        ]
        
        # Create horizontal bar chart
        fig.add_trace(go.Bar(
            x=sorted_data['Performance'],
            y=sorted_data['Sector'],
            orientation='h',
            marker_color=colors,
            text=[f"{p:.1f}%" for p in sorted_data['Performance']],
            textposition='outside'
        ))
        
        # Update layout
        fig.update_layout(
            title='섹터별 성과',
            xaxis_title='성과 (%)',
            template=self.theme,
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_risk_return_scatter(
        self,
        stocks_data: List[Dict[str, Any]]
    ) -> go.Figure:
        """Create risk-return scatter plot."""
        fig = go.Figure()
        
        # Extract data
        returns = [s['return'] for s in stocks_data]
        risks = [s['risk'] for s in stocks_data]
        names = [s['name'] for s in stocks_data]
        
        # Add scatter points
        fig.add_trace(go.Scatter(
            x=risks,
            y=returns,
            mode='markers+text',
            text=names,
            textposition='top center',
            marker=dict(
                size=10,
                color=returns,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="수익률 (%)")
            )
        ))
        
        # Add efficient frontier line (if applicable)
        # This is a simplified version
        
        # Update layout
        fig.update_layout(
            title='리스크-수익률 분석',
            xaxis_title='변동성 (연간 %)',
            yaxis_title='수익률 (연간 %)',
            template=self.theme,
            height=500,
            hovermode='closest'
        )
        
        return fig
    
    # Helper methods for adding chart components
    
    def _add_candlestick(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add professional candlestick chart with enhanced styling."""
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down'],
                increasing_fillcolor=self.colors['up'],
                decreasing_fillcolor=self.colors['down'],
                line=dict(width=1),
                hovertemplate='<b>%{x}</b><br>' +
                            'Open: %{open}<br>' +
                            'High: %{high}<br>' +
                            'Low: %{low}<br>' +
                            'Close: %{close}<br>' +
                            '<extra></extra>'
            ),
            row=row, col=col
        )
    
    def _add_price_line(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add professional price line with smooth styling."""
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(
                    color=self.colors['accent'], 
                    width=2.5,
                    shape='spline',
                    smoothing=0.3
                ),
                hovertemplate='<b>%{x}</b><br>Close: %{y}<extra></extra>'
            ),
            row=row, col=col
        )
    
    def _add_moving_averages(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add moving averages."""
        # Calculate MAs if not in DataFrame
        for period in [20, 50, 200]:
            ma_col = f'MA_{period}'
            if ma_col not in df.columns:
                df[ma_col] = df['Close'].rolling(window=period).mean()
            
            if not df[ma_col].isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[ma_col],
                        mode='lines',
                        name=f'MA{period}',
                        line=dict(width=1),
                        visible='legendonly' if period == 200 else True
                    ),
                    row=row, col=col
                )
    
    def _add_bollinger_bands(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add Bollinger Bands."""
        bollinger = ta.volatility.BollingerBands(df['Close'])
        
        # Upper band
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=bollinger.bollinger_hband(),
                mode='lines',
                name='BB Upper',
                line=dict(width=1, dash='dash', color='gray'),
                visible='legendonly'
            ),
            row=row, col=col
        )
        
        # Lower band
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=bollinger.bollinger_lband(),
                mode='lines',
                name='BB Lower',
                line=dict(width=1, dash='dash', color='gray'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)',
                visible='legendonly'
            ),
            row=row, col=col
        )
    
    def _add_support_resistance(
        self, 
        fig: go.Figure, 
        technical_data: Dict[str, Any], 
        row: int, 
        col: int
    ):
        """Add support and resistance lines."""
        support = technical_data.get('support_level')
        resistance = technical_data.get('resistance_level')
        
        if support:
            fig.add_hline(
                y=support,
                line_dash="dash",
                line_color="green",
                annotation_text="지지선",
                row=row, col=col
            )
        
        if resistance:
            fig.add_hline(
                y=resistance,
                line_dash="dash",
                line_color="red",
                annotation_text="저항선",
                row=row, col=col
            )
    
    def _add_macd(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add MACD indicator."""
        macd = ta.trend.MACD(df['Close'])
        
        # MACD line
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=macd.macd(),
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=1)
            ),
            row=row, col=col
        )
        
        # Signal line
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=macd.macd_signal(),
                mode='lines',
                name='Signal',
                line=dict(color='red', width=1)
            ),
            row=row, col=col
        )
        
        # Histogram
        macd_hist = macd.macd_diff()
        colors = ['green' if val >= 0 else 'red' for val in macd_hist]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=macd_hist,
                name='MACD Hist',
                marker_color=colors
            ),
            row=row, col=col
        )
    
    def _add_rsi(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add RSI indicator."""
        rsi = ta.momentum.rsi(df['Close'], window=14)
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=row, col=col
        )
        
        # Overbought/Oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=col)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=col)
    
    def _add_volume(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add volume bars."""
        colors = [
            self.colors['up'] if close >= open else self.colors['down']
            for close, open in zip(df['Close'], df['Open'])
        ]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='거래량',
                marker_color=colors,
                opacity=0.7
            ),
            row=row, col=col
        )
    
    def _add_stochastic(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add Stochastic oscillator."""
        stoch = ta.momentum.StochasticOscillator(
            df['High'], df['Low'], df['Close']
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=stoch.stoch(),
                mode='lines',
                name='%K',
                line=dict(color='blue', width=1)
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=stoch.stoch_signal(),
                mode='lines',
                name='%D',
                line=dict(color='red', width=1)
            ),
            row=row, col=col
        )
        
        # Overbought/Oversold
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=row, col=col)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=row, col=col)
    
    def _add_atr(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add Average True Range."""
        atr = ta.volatility.average_true_range(
            df['High'], df['Low'], df['Close']
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=atr,
                mode='lines',
                name='ATR',
                line=dict(color='orange', width=2)
            ),
            row=row, col=col
        )
    
    def _add_obv(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """Add On-Balance Volume."""
        obv = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=obv,
                mode='lines',
                name='OBV',
                line=dict(color='brown', width=2)
            ),
            row=row, col=col
        )
    
    def _update_main_chart_layout(self, fig: go.Figure, ticker: str, market: str):
        """Update main chart layout with professional styling."""
        fig.update_layout(
            height=self.default_height,
            template=self.theme,
            title=dict(
                text=f"{ticker} Technical Analysis",
                font=dict(
                    size=24,
                    color=self.colors['text'],
                    family="Inter, sans-serif"
                ),
                x=0.5,
                xanchor='center'
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(255,255,255,0.1)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                font=dict(color=self.colors['text'])
            ),
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font=dict(
                color=self.colors['text'],
                family="Inter, sans-serif"
            ),
            margin=dict(l=60, r=40, t=80, b=60),
            # Add animation configuration
            transition_duration=500,
            transition_easing="cubic-in-out"
        )
        
        # Update y-axis labels with professional styling
        currency = "원" if market == "한국장" else "$"
        
        fig.update_yaxes(
            title_text=f"Price ({currency})",
            title_font=dict(color=self.colors['text'], family="Inter, sans-serif"),
            tickfont=dict(color=self.colors['text']),
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            row=1, col=1
        )
        
        fig.update_yaxes(
            title_text="MACD",
            title_font=dict(color=self.colors['text'], family="Inter, sans-serif"),
            tickfont=dict(color=self.colors['text']),
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            row=2, col=1
        )
        
        fig.update_yaxes(
            title_text="RSI",
            title_font=dict(color=self.colors['text'], family="Inter, sans-serif"),
            tickfont=dict(color=self.colors['text']),
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            row=3, col=1
        )
        
        fig.update_yaxes(
            title_text="Volume",
            title_font=dict(color=self.colors['text'], family="Inter, sans-serif"),
            tickfont=dict(color=self.colors['text']),
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            row=4, col=1
        )
        
        # Update x-axis with professional styling
        fig.update_xaxes(
            title_text="Date",
            title_font=dict(color=self.colors['text'], family="Inter, sans-serif"),
            tickfont=dict(color=self.colors['text']),
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            row=4, col=1
        )
    
    def _add_chart_animations(self, fig: go.Figure):
        """Add professional animations to charts."""
        # Add smooth transitions for all traces
        for trace in fig.data:
            if hasattr(trace, 'line'):
                trace.line.update(dict(
                    # Add subtle glow effect
                    width=trace.line.width if trace.line.width else 2
                ))
        
        # Update layout with animation config
        fig.update_layout(
            # Smooth transitions
            transition={
                'duration': 800,
                'easing': 'cubic-in-out'
            },
            # Enable hover animations
            hoverlabel=dict(
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(255,255,255,0.2)",
                font_size=12,
                font_family="Inter, sans-serif"
            )
        )
    
    def create_animated_metric_chart(self, value: float, max_value: float, title: str) -> go.Figure:
        """Create an animated circular progress chart for metrics."""
        
        # Calculate percentage
        percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'color': self.colors['text'], 'family': 'Inter, sans-serif'}},
            delta={'reference': 50, 'increasing': {'color': self.colors['up']}, 'decreasing': {'color': self.colors['down']}},
            gauge={
                'axis': {
                    'range': [None, 100],
                    'tickcolor': self.colors['text'],
                    'tickfont': {'color': self.colors['text'], 'family': 'Inter, sans-serif'}
                },
                'bar': {'color': self.colors['accent']},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': self.colors['grid'],
                'steps': [
                    {'range': [0, 25], 'color': 'rgba(255, 87, 34, 0.2)'},
                    {'range': [25, 50], 'color': 'rgba(255, 183, 77, 0.2)'},
                    {'range': [50, 75], 'color': 'rgba(78, 205, 196, 0.2)'},
                    {'range': [75, 100], 'color': 'rgba(38, 198, 218, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font={'color': self.colors['text'], 'family': 'Inter, sans-serif'},
            height=300,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig