"""
Technical Analysis Module

Provides comprehensive technical analysis functionality.
"""

import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
import ta

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Comprehensive technical analysis toolkit."""
    
    def __init__(self):
        self.indicators = {}
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis on stock data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with technical analysis results
        """
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        results = {}
        
        # Price analysis
        results.update(self._analyze_price_action(df))
        
        # Trend indicators
        results.update(self._calculate_trend_indicators(df))
        
        # Momentum indicators
        results.update(self._calculate_momentum_indicators(df))
        
        # Volatility indicators
        results.update(self._calculate_volatility_indicators(df))
        
        # Volume analysis (if available)
        if 'Volume' in df.columns:
            results.update(self._analyze_volume(df))
        
        # Support and resistance
        results.update(self._find_support_resistance(df))
        
        # Pattern recognition
        results.update(self._identify_patterns(df))
        
        # Overall technical score
        results['technical_score'] = self._calculate_technical_score(results)
        
        return results
    
    def _analyze_price_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze basic price action."""
        current_price = df['Close'].iloc[-1]
        
        # Price levels
        high_52w = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
        low_52w = df['Low'].tail(252).min() if len(df) >= 252 else df['Low'].min()
        
        # Recent performance
        returns_1d = df['Close'].pct_change().iloc[-1] if len(df) > 1 else 0
        returns_5d = (df['Close'].iloc[-1] / df['Close'].iloc[-6] - 1) if len(df) > 5 else 0
        returns_20d = (df['Close'].iloc[-1] / df['Close'].iloc[-21] - 1) if len(df) > 20 else 0
        
        # Price position
        price_position_52w = (current_price - low_52w) / (high_52w - low_52w) if high_52w != low_52w else 0.5
        
        return {
            'current_price': current_price,
            '52w_high': high_52w,
            '52w_low': low_52w,
            'price_position_52w': price_position_52w,
            'returns_1d': returns_1d,
            'returns_5d': returns_5d,
            'returns_20d': returns_20d,
        }
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend-following indicators."""
        close = df['Close']
        
        # Simple Moving Averages
        sma_20 = ta.trend.sma_indicator(close, window=20)
        sma_50 = ta.trend.sma_indicator(close, window=50)
        sma_200 = ta.trend.sma_indicator(close, window=200)
        
        # Exponential Moving Averages
        ema_12 = ta.trend.ema_indicator(close, window=12)
        ema_26 = ta.trend.ema_indicator(close, window=26)
        
        # MACD
        macd = ta.trend.MACD(close)
        macd_line = macd.macd()
        macd_signal = macd.macd_signal()
        macd_histogram = macd.macd_diff()
        
        # ADX (Average Directional Index)
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], close)
        adx_value = adx.adx()
        adx_pos = adx.adx_pos()
        adx_neg = adx.adx_neg()
        
        # Current values
        current_price = close.iloc[-1]
        
        return {
            'sma_20': sma_20.iloc[-1] if not sma_20.empty else None,
            'sma_50': sma_50.iloc[-1] if not sma_50.empty else None,
            'sma_200': sma_200.iloc[-1] if not sma_200.empty else None,
            'ema_12': ema_12.iloc[-1] if not ema_12.empty else None,
            'ema_26': ema_26.iloc[-1] if not ema_26.empty else None,
            'macd_line': macd_line.iloc[-1] if not macd_line.empty else None,
            'macd_signal': macd_signal.iloc[-1] if not macd_signal.empty else None,
            'macd_histogram': macd_histogram.iloc[-1] if not macd_histogram.empty else None,
            'adx': adx_value.iloc[-1] if not adx_value.empty else None,
            'adx_pos': adx_pos.iloc[-1] if not adx_pos.empty else None,
            'adx_neg': adx_neg.iloc[-1] if not adx_neg.empty else None,
            'trend_direction': self._determine_trend_direction(current_price, sma_20, sma_50, sma_200),
        }
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate momentum indicators."""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # RSI
        rsi = ta.momentum.rsi(close, window=14)
        
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(high, low, close)
        stoch_k = stoch.stoch()
        stoch_d = stoch.stoch_signal()
        
        # Williams %R
        williams_r = ta.momentum.williams_r(high, low, close)
        
        # ROC (Rate of Change)
        roc = ta.momentum.roc(close, window=12)
        
        # Money Flow Index
        mfi = None
        if 'Volume' in df.columns:
            mfi = ta.volume.money_flow_index(high, low, close, df['Volume'])
        
        return {
            'rsi': rsi.iloc[-1] if not rsi.empty else None,
            'stoch_k': stoch_k.iloc[-1] if not stoch_k.empty else None,
            'stoch_d': stoch_d.iloc[-1] if not stoch_d.empty else None,
            'williams_r': williams_r.iloc[-1] if not williams_r.empty else None,
            'roc': roc.iloc[-1] if not roc.empty else None,
            'mfi': mfi.iloc[-1] if mfi is not None and not mfi.empty else None,
            'momentum_signal': self._determine_momentum_signal(rsi),
        }
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volatility indicators."""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(close)
        bb_upper = bollinger.bollinger_hband()
        bb_middle = bollinger.bollinger_mavg()
        bb_lower = bollinger.bollinger_lband()
        bb_width = bollinger.bollinger_wband()
        bb_percent = bollinger.bollinger_pband()
        
        # Average True Range
        atr = ta.volatility.average_true_range(high, low, close)
        
        # Historical Volatility
        returns = close.pct_change().dropna()
        historical_volatility = returns.std() * np.sqrt(252)  # Annualized
        
        # Volatility percentile (position in recent volatility range)
        recent_volatility = returns.tail(20).std() * np.sqrt(252)
        volatility_history = returns.rolling(20).std().dropna() * np.sqrt(252)
        volatility_percentile = (volatility_history <= recent_volatility).mean() if len(volatility_history) > 0 else 0.5
        
        return {
            'bb_upper': bb_upper.iloc[-1] if not bb_upper.empty else None,
            'bb_middle': bb_middle.iloc[-1] if not bb_middle.empty else None,
            'bb_lower': bb_lower.iloc[-1] if not bb_lower.empty else None,
            'bb_width': bb_width.iloc[-1] if not bb_width.empty else None,
            'bb_percent': bb_percent.iloc[-1] if not bb_percent.empty else None,
            'atr': atr.iloc[-1] if not atr.empty else None,
            'historical_volatility': historical_volatility,
            'volatility_percentile': volatility_percentile,
        }
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns."""
        volume = df['Volume']
        close = df['Close']
        
        # Volume averages
        volume_avg_20 = volume.rolling(20).mean()
        volume_avg_50 = volume.rolling(50).mean()
        
        # Volume trend
        current_volume = volume.iloc[-1]
        volume_ratio_20 = current_volume / volume_avg_20.iloc[-1] if not volume_avg_20.empty else 1
        volume_ratio_50 = current_volume / volume_avg_50.iloc[-1] if not volume_avg_50.empty else 1
        
        # On-Balance Volume
        obv = ta.volume.on_balance_volume(close, volume)
        
        # Volume Price Trend
        vpt = ta.volume.volume_price_trend(close, volume)
        
        # Accumulation/Distribution Line
        ad_line = ta.volume.acc_dist_index(df['High'], df['Low'], close, volume)
        
        return {
            'current_volume': current_volume,
            'volume_avg_20': volume_avg_20.iloc[-1] if not volume_avg_20.empty else None,
            'volume_avg_50': volume_avg_50.iloc[-1] if not volume_avg_50.empty else None,
            'volume_ratio_20': volume_ratio_20,
            'volume_ratio_50': volume_ratio_50,
            'obv': obv.iloc[-1] if not obv.empty else None,
            'vpt': vpt.iloc[-1] if not vpt.empty else None,
            'ad_line': ad_line.iloc[-1] if not ad_line.empty else None,
            'volume_signal': self._determine_volume_signal(volume_ratio_20, volume_ratio_50),
        }
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify support and resistance levels."""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # Recent support and resistance (last 30 days)
        recent_data = df.tail(30) if len(df) > 30 else df
        support_level = recent_data['Low'].min()
        resistance_level = recent_data['High'].max()
        
        # Pivot points (simple method)
        pivot_highs = []
        pivot_lows = []
        
        # Find local peaks and troughs (simplified)
        window = 5
        for i in range(window, len(df) - window):
            # Local high
            if high.iloc[i] == high.iloc[i-window:i+window+1].max():
                pivot_highs.append(high.iloc[i])
            
            # Local low
            if low.iloc[i] == low.iloc[i-window:i+window+1].min():
                pivot_lows.append(low.iloc[i])
        
        # Key levels (most frequent price areas)
        key_resistance = max(pivot_highs) if pivot_highs else resistance_level
        key_support = min(pivot_lows) if pivot_lows else support_level
        
        current_price = close.iloc[-1]
        
        return {
            'support_level': support_level,
            'resistance_level': resistance_level,
            'key_support': key_support,
            'key_resistance': key_resistance,
            'distance_to_support': (current_price - support_level) / current_price,
            'distance_to_resistance': (resistance_level - current_price) / current_price,
        }
    
    def _identify_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify basic chart patterns."""
        close = df['Close']
        
        patterns = {}
        
        # Double top/bottom (simplified detection)
        if len(df) >= 20:
            recent_highs = df['High'].tail(20)
            recent_lows = df['Low'].tail(20)
            
            # Simple pattern detection based on price levels
            max_high = recent_highs.max()
            min_low = recent_lows.min()
            current_price = close.iloc[-1]
            
            # Trend pattern
            if current_price > close.iloc[-5] > close.iloc[-10]:
                patterns['trend_pattern'] = 'ascending'
            elif current_price < close.iloc[-5] < close.iloc[-10]:
                patterns['trend_pattern'] = 'descending'
            else:
                patterns['trend_pattern'] = 'sideways'
            
            # Breakout potential
            recent_range = max_high - min_low
            if recent_range > 0:
                breakout_threshold = 0.02  # 2% move
                if (current_price - max_high) / max_high > breakout_threshold:
                    patterns['breakout'] = 'upward'
                elif (min_low - current_price) / current_price > breakout_threshold:
                    patterns['breakout'] = 'downward'
                else:
                    patterns['breakout'] = 'none'
        
        return patterns
    
    def _determine_trend_direction(
        self, 
        current_price: float, 
        sma_20: pd.Series, 
        sma_50: pd.Series, 
        sma_200: pd.Series
    ) -> str:
        """Determine overall trend direction."""
        if sma_20.empty or sma_50.empty or sma_200.empty:
            return 'unknown'
        
        sma_20_val = sma_20.iloc[-1]
        sma_50_val = sma_50.iloc[-1]
        sma_200_val = sma_200.iloc[-1]
        
        # Strong uptrend
        if current_price > sma_20_val > sma_50_val > sma_200_val:
            return 'strong_uptrend'
        # Uptrend
        elif current_price > sma_20_val and sma_20_val > sma_50_val:
            return 'uptrend'
        # Strong downtrend
        elif current_price < sma_20_val < sma_50_val < sma_200_val:
            return 'strong_downtrend'
        # Downtrend
        elif current_price < sma_20_val and sma_20_val < sma_50_val:
            return 'downtrend'
        else:
            return 'sideways'
    
    def _determine_momentum_signal(self, rsi: pd.Series) -> str:
        """Determine momentum signal from RSI."""
        if rsi.empty:
            return 'neutral'
        
        rsi_val = rsi.iloc[-1]
        
        if rsi_val > 70:
            return 'overbought'
        elif rsi_val < 30:
            return 'oversold'
        elif rsi_val > 50:
            return 'bullish'
        else:
            return 'bearish'
    
    def _determine_volume_signal(self, ratio_20: float, ratio_50: float) -> str:
        """Determine volume signal."""
        if ratio_20 > 1.5 and ratio_50 > 1.2:
            return 'high_volume_breakout'
        elif ratio_20 > 1.2:
            return 'above_average'
        elif ratio_20 < 0.8:
            return 'below_average'
        else:
            return 'normal'
    
    def _calculate_technical_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall technical score (0-100)."""
        score = 50  # Neutral starting point
        
        # Trend component (±20 points)
        trend = results.get('trend_direction', 'sideways')
        if trend == 'strong_uptrend':
            score += 20
        elif trend == 'uptrend':
            score += 10
        elif trend == 'strong_downtrend':
            score -= 20
        elif trend == 'downtrend':
            score -= 10
        
        # Momentum component (±15 points)
        momentum = results.get('momentum_signal', 'neutral')
        if momentum == 'bullish':
            score += 10
        elif momentum == 'oversold':
            score += 15  # Potential bounce
        elif momentum == 'bearish':
            score -= 10
        elif momentum == 'overbought':
            score -= 15  # Potential correction
        
        # Volume component (±10 points)
        volume_signal = results.get('volume_signal', 'normal')
        if volume_signal == 'high_volume_breakout':
            score += 10
        elif volume_signal == 'above_average':
            score += 5
        elif volume_signal == 'below_average':
            score -= 5
        
        # Support/Resistance component (±5 points)
        distance_to_support = results.get('distance_to_support', 0)
        distance_to_resistance = results.get('distance_to_resistance', 0)
        
        if distance_to_support < 0.02:  # Very close to support
            score += 5
        elif distance_to_resistance < 0.02:  # Very close to resistance
            score -= 5
        
        return max(0, min(100, score))
    
    def get_price_targets(
        self, 
        df: pd.DataFrame, 
        technical_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate dynamic price targets based on technical analysis.
        
        Args:
            df: Stock price DataFrame
            technical_results: Results from technical analysis
            
        Returns:
            Dictionary with price targets
        """
        current_price = df['Close'].iloc[-1]
        
        # Get volatility for dynamic targets
        volatility = technical_results.get('historical_volatility', 0.2)
        atr = technical_results.get('atr', current_price * 0.02)
        
        # Base multipliers adjusted for volatility
        if volatility < 0.15:  # Low volatility
            buy_discount = 0.02
            profit_target = 0.05
            stop_loss = 0.03
        elif volatility < 0.3:  # Medium volatility
            buy_discount = 0.03
            profit_target = 0.08
            stop_loss = 0.04
        else:  # High volatility
            buy_discount = 0.05
            profit_target = 0.12
            stop_loss = 0.06
        
        # Adjust based on support/resistance
        support_level = technical_results.get('support_level', current_price * 0.95)
        resistance_level = technical_results.get('resistance_level', current_price * 1.05)
        
        # Buy target (near support or discounted from current)
        buy_target = min(current_price * (1 - buy_discount), 
                        support_level * 1.01)  # Slightly above support
        
        # Profit target (near resistance or based on volatility)
        profit_target_price = max(current_price * (1 + profit_target),
                                 resistance_level * 0.99)  # Slightly below resistance
        
        # Stop loss (below support or based on ATR)
        stop_loss_price = min(current_price * (1 - stop_loss),
                             support_level * 0.98,  # Below support
                             current_price - (2 * atr))  # 2 ATR below current
        
        return {
            'buy_target': buy_target,
            'profit_target': profit_target_price,
            'stop_loss': stop_loss_price,
            'risk_reward_ratio': (profit_target_price - current_price) / (current_price - stop_loss_price)
        }