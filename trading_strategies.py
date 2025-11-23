"""
Crazy Trading Strategies for Indian Market Backtesting
Collection of aggressive and creative trading strategies
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        """Generate trading signals for given date"""
        pass

    def calculate_sma(self, df: pd.DataFrame, period: int, date) -> float:
        """Calculate Simple Moving Average"""
        idx = df.index.get_loc(date)
        if idx < period - 1:
            return None
        return df['close'].iloc[max(0, idx - period + 1):idx + 1].mean()

    def calculate_ema(self, df: pd.DataFrame, period: int, date) -> float:
        """Calculate Exponential Moving Average"""
        idx = df.index.get_loc(date)
        if idx < period - 1:
            return None
        return df['close'].iloc[:idx + 1].ewm(span=period, adjust=False).mean().iloc[-1]

    def calculate_rsi(self, df: pd.DataFrame, period: int, date) -> float:
        """Calculate Relative Strength Index"""
        idx = df.index.get_loc(date)
        if idx < period:
            return None

        prices = df['close'].iloc[max(0, idx - period):idx + 1]
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int, std_dev: float, date) -> tuple:
        """Calculate Bollinger Bands"""
        idx = df.index.get_loc(date)
        if idx < period - 1:
            return None, None, None

        prices = df['close'].iloc[max(0, idx - period + 1):idx + 1]
        sma = prices.mean()
        std = prices.std()

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        return upper, sma, lower


class MomentumExplosionStrategy(BaseStrategy):
    """
    CRAZY Momentum Strategy: Rides strong trends aggressively
    Buys on explosive momentum, sells on weakness
    """

    def __init__(self, fast_period: int = 10, slow_period: int = 50,
                 rsi_threshold: int = 60, position_size_pct: float = 0.15):
        super().__init__("Momentum Explosion")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.rsi_threshold = rsi_threshold
        self.position_size_pct = position_size_pct

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < self.slow_period:
                continue

            fast_ema = self.calculate_ema(df, self.fast_period, date)
            slow_ema = self.calculate_ema(df, self.slow_period, date)
            rsi = self.calculate_rsi(df, 14, date)

            if fast_ema is None or slow_ema is None or rsi is None:
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: Fast EMA crosses above Slow EMA + RSI shows momentum
            if symbol not in portfolio.positions:
                if fast_ema > slow_ema and rsi > self.rsi_threshold:
                    # Calculate position size
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Fast EMA crosses below Slow EMA or RSI drops
            elif symbol in portfolio.positions:
                if fast_ema < slow_ema or rsi < 40:
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class MeanReversionMadnessStrategy(BaseStrategy):
    """
    CRAZY Mean Reversion: Buys oversold, sells overbought
    Uses Bollinger Bands and RSI for extreme entries
    """

    def __init__(self, bb_period: int = 20, bb_std: float = 2.5,
                 rsi_oversold: int = 25, rsi_overbought: int = 75,
                 position_size_pct: float = 0.12):
        super().__init__("Mean Reversion Madness")
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.position_size_pct = position_size_pct

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < self.bb_period:
                continue

            upper, middle, lower = self.calculate_bollinger_bands(df, self.bb_period, self.bb_std, date)
            rsi = self.calculate_rsi(df, 14, date)

            if upper is None or rsi is None:
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: Price touches lower band + RSI oversold
            if symbol not in portfolio.positions:
                if current_price <= lower and rsi < self.rsi_oversold:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Price touches upper band + RSI overbought
            elif symbol in portfolio.positions:
                if current_price >= upper or rsi > self.rsi_overbought:
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class VolatilityBreakoutStrategy(BaseStrategy):
    """
    CRAZY Volatility Breakout: Trades on explosive price moves
    Uses ATR and price breakouts
    """

    def __init__(self, atr_period: int = 14, breakout_multiplier: float = 2.0,
                 position_size_pct: float = 0.10):
        super().__init__("Volatility Breakout")
        self.atr_period = atr_period
        self.breakout_multiplier = breakout_multiplier
        self.position_size_pct = position_size_pct

    def calculate_atr(self, df: pd.DataFrame, period: int, date) -> float:
        """Calculate Average True Range"""
        idx = df.index.get_loc(date)
        if idx < period:
            return None

        high = df['high'].iloc[max(0, idx - period):idx + 1]
        low = df['low'].iloc[max(0, idx - period):idx + 1]
        close = df['close'].iloc[max(0, idx - period):idx + 1]

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]

        return atr

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < max(self.atr_period, 20):
                continue

            atr = self.calculate_atr(df, self.atr_period, date)
            if atr is None:
                continue

            current_price = df.loc[date, 'close']
            high_20 = df['high'].iloc[max(0, idx - 20):idx].max()
            low_20 = df['low'].iloc[max(0, idx - 20):idx].min()

            # BUY Signal: Price breaks above 20-day high with strong ATR
            if symbol not in portfolio.positions:
                if current_price > high_20:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Price breaks below 20-day low or drops by 2*ATR
            elif symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                stop_loss = position.avg_price - (self.breakout_multiplier * atr)

                if current_price < low_20 or current_price < stop_loss:
                    quantity = position.quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class SuperTrendFollowerStrategy(BaseStrategy):
    """
    CRAZY SuperTrend Follower: Uses multiple indicators for confirmation
    Combines Moving Averages, MACD, and RSI for power entries
    """

    def __init__(self, position_size_pct: float = 0.20):
        super().__init__("SuperTrend Follower")
        self.position_size_pct = position_size_pct

    def calculate_macd(self, df: pd.DataFrame, date) -> tuple:
        """Calculate MACD"""
        idx = df.index.get_loc(date)
        if idx < 26:
            return None, None, None

        prices = df['close'].iloc[:idx + 1]
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < 50:
                continue

            # Calculate indicators
            sma20 = self.calculate_sma(df, 20, date)
            sma50 = self.calculate_sma(df, 50, date)
            rsi = self.calculate_rsi(df, 14, date)
            macd, signal, histogram = self.calculate_macd(df, date)

            if None in [sma20, sma50, rsi, macd]:
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: All indicators align bullish
            if symbol not in portfolio.positions:
                conditions = [
                    sma20 > sma50,  # Uptrend
                    current_price > sma20,  # Price above MA
                    rsi > 50 and rsi < 70,  # Momentum but not overbought
                    macd > signal,  # MACD bullish
                    histogram > 0  # MACD histogram positive
                ]

                if all(conditions):
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Any bearish signal
            elif symbol in portfolio.positions:
                exit_conditions = [
                    sma20 < sma50,  # Downtrend
                    current_price < sma20,  # Price below MA
                    rsi < 40,  # Weak momentum
                    macd < signal  # MACD bearish
                ]

                if any(exit_conditions):
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class BollingerSqueezeStrategy(BaseStrategy):
    """
    CRAZY Bollinger Squeeze: Trades volatility compression followed by expansion
    Waits for squeeze then trades the breakout
    """

    def __init__(self, bb_period: int = 20, squeeze_threshold: float = 0.015,
                 position_size_pct: float = 0.15):
        super().__init__("Bollinger Squeeze")
        self.bb_period = bb_period
        self.squeeze_threshold = squeeze_threshold
        self.position_size_pct = position_size_pct

    def detect_squeeze(self, df: pd.DataFrame, date) -> bool:
        """Detect Bollinger Band squeeze"""
        idx = df.index.get_loc(date)
        if idx < self.bb_period:
            return False

        upper, middle, lower = self.calculate_bollinger_bands(df, self.bb_period, 2.0, date)
        if upper is None:
            return False

        bandwidth = (upper - lower) / middle
        return bandwidth < self.squeeze_threshold

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < self.bb_period + 5:
                continue

            current_price = df.loc[date, 'close']

            # Check if we had a squeeze in recent days
            squeeze_detected = False
            for i in range(1, 6):
                past_date = df.index[idx - i]
                if self.detect_squeeze(df, past_date):
                    squeeze_detected = True
                    break

            if not squeeze_detected:
                continue

            # BUY Signal: Breakout above Bollinger mid-line after squeeze
            upper, middle, lower = self.calculate_bollinger_bands(df, self.bb_period, 2.0, date)
            if upper is None:
                continue

            if symbol not in portfolio.positions:
                if current_price > middle:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Price touches lower band or reverses
            elif symbol in portfolio.positions:
                if current_price < middle or current_price < lower:
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class GapAndGoStrategy(BaseStrategy):
    """
    CRAZY Gap and Go: Trades morning gaps in Indian market
    Exploits opening gap ups/downs with momentum follow-through
    """

    def __init__(self, min_gap_pct: float = 2.0, position_size_pct: float = 0.12):
        super().__init__("Gap and Go")
        self.min_gap_pct = min_gap_pct
        self.position_size_pct = position_size_pct

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < 1:
                continue

            current_open = df.loc[date, 'open']
            current_close = df.loc[date, 'close']
            prev_close = df.iloc[idx - 1]['close']

            # Calculate gap percentage
            gap_pct = ((current_open - prev_close) / prev_close) * 100

            # BUY Signal: Gap up and price continues higher
            if symbol not in portfolio.positions:
                if gap_pct >= self.min_gap_pct and current_close > current_open:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_close)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Gap fills or momentum fades
            elif symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                if current_close < prev_close or current_close < position.avg_price * 0.97:
                    quantity = position.quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class TripleMomentumRocketStrategy(BaseStrategy):
    """
    CRAZY Triple Momentum Rocket: Combines RSI, MACD, and Rate of Change
    Only enters when all three momentum indicators align explosively
    """

    def __init__(self, roc_period: int = 10, position_size_pct: float = 0.18):
        super().__init__("Triple Momentum Rocket")
        self.roc_period = roc_period
        self.position_size_pct = position_size_pct

    def calculate_roc(self, df: pd.DataFrame, period: int, date) -> float:
        """Calculate Rate of Change"""
        idx = df.index.get_loc(date)
        if idx < period:
            return None

        current_price = df.loc[date, 'close']
        past_price = df.iloc[idx - period]['close']
        roc = ((current_price - past_price) / past_price) * 100
        return roc

    def calculate_macd(self, df: pd.DataFrame, date) -> tuple:
        """Calculate MACD"""
        idx = df.index.get_loc(date)
        if idx < 26:
            return None, None, None

        prices = df['close'].iloc[:idx + 1]
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < 26:
                continue

            rsi = self.calculate_rsi(df, 14, date)
            roc = self.calculate_roc(df, self.roc_period, date)
            macd, macd_signal, histogram = self.calculate_macd(df, date)

            if None in [rsi, roc, macd]:
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: Triple momentum alignment
            if symbol not in portfolio.positions:
                rocket_conditions = [
                    rsi > 60 and rsi < 80,  # Strong but not overbought
                    roc > 5,  # Strong rate of change
                    macd > macd_signal,  # MACD bullish
                    histogram > 0  # MACD accelerating
                ]

                if all(rocket_conditions):
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Any momentum failure
            elif symbol in portfolio.positions:
                exit_conditions = [
                    rsi < 45,  # Momentum dying
                    roc < -3,  # Negative momentum
                    macd < macd_signal  # MACD bearish
                ]

                if any(exit_conditions):
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class ReversalHunterStrategy(BaseStrategy):
    """
    CRAZY Reversal Hunter: Catches V-shaped reversals after extreme moves
    Uses oversold RSI + hammer/bullish engulfing patterns
    """

    def __init__(self, rsi_extreme: int = 20, position_size_pct: float = 0.14):
        super().__init__("Reversal Hunter")
        self.rsi_extreme = rsi_extreme
        self.position_size_pct = position_size_pct

    def is_hammer(self, df: pd.DataFrame, date) -> bool:
        """Detect hammer candle pattern"""
        idx = df.index.get_loc(date)
        if idx < 1:
            return False

        row = df.loc[date]
        open_price = row['open']
        close = row['close']
        high = row['high']
        low = row['low']

        body = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low

        # Hammer: small body, long lower wick
        return (lower_wick > body * 2) and (upper_wick < body)

    def is_bullish_engulfing(self, df: pd.DataFrame, date) -> bool:
        """Detect bullish engulfing pattern"""
        idx = df.index.get_loc(date)
        if idx < 1:
            return False

        prev = df.iloc[idx - 1]
        curr = df.loc[date]

        prev_bearish = prev['close'] < prev['open']
        curr_bullish = curr['close'] > curr['open']
        engulfing = curr['close'] > prev['open'] and curr['open'] < prev['close']

        return prev_bearish and curr_bullish and engulfing

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < 20:
                continue

            rsi = self.calculate_rsi(df, 14, date)
            if rsi is None:
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: Extreme oversold + reversal pattern
            if symbol not in portfolio.positions:
                is_oversold = rsi < self.rsi_extreme
                has_pattern = self.is_hammer(df, date) or self.is_bullish_engulfing(df, date)

                if is_oversold and has_pattern:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: RSI reaches normal or overbought
            elif symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                # Take profit at 10% or if RSI gets overbought
                if profit_pct > 10 or rsi > 70:
                    quantity = position.quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class VolumeExplosionStrategy(BaseStrategy):
    """
    CRAZY Volume Explosion: Trades on massive volume spikes
    When volume explodes 2x+ average, momentum follows
    """

    def __init__(self, volume_multiplier: float = 2.5,
                 volume_period: int = 20,
                 position_size_pct: float = 0.16):
        super().__init__("Volume Explosion")
        self.volume_multiplier = volume_multiplier
        self.volume_period = volume_period
        self.position_size_pct = position_size_pct

    def calculate_avg_volume(self, df: pd.DataFrame, period: int, date) -> float:
        """Calculate average volume"""
        idx = df.index.get_loc(date)
        if idx < period:
            return None

        return df['volume'].iloc[max(0, idx - period):idx].mean()

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < self.volume_period + 1:
                continue

            avg_volume = self.calculate_avg_volume(df, self.volume_period, date)
            if avg_volume is None or avg_volume == 0:
                continue

            current_volume = df.loc[date, 'volume']
            current_price = df.loc[date, 'close']
            current_open = df.loc[date, 'open']

            volume_ratio = current_volume / avg_volume

            # BUY Signal: Massive volume spike + bullish candle
            if symbol not in portfolio.positions:
                is_volume_spike = volume_ratio > self.volume_multiplier
                is_bullish = current_price > current_open
                strong_move = ((current_price - current_open) / current_open) > 0.02

                if is_volume_spike and is_bullish and strong_move:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Volume dries up or price reverses
            elif symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                volume_dried_up = volume_ratio < 0.7
                price_reverses = current_price < position.avg_price * 0.97

                if volume_dried_up or price_reverses:
                    quantity = position.quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class MovingAverageRainbowStrategy(BaseStrategy):
    """
    CRAZY MA Rainbow: Uses 5 moving averages (5,10,20,50,100)
    Buys when they align perfectly in ascending order
    """

    def __init__(self, position_size_pct: float = 0.20):
        super().__init__("MA Rainbow")
        self.ma_periods = [5, 10, 20, 50, 100]
        self.position_size_pct = position_size_pct

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < max(self.ma_periods):
                continue

            # Calculate all MAs
            mas = []
            for period in self.ma_periods:
                ma = self.calculate_sma(df, period, date)
                if ma is None:
                    break
                mas.append(ma)

            if len(mas) != len(self.ma_periods):
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: Perfect rainbow alignment (ascending order)
            if symbol not in portfolio.positions:
                # Check if MAs are in perfect ascending order
                rainbow_aligned = all(mas[i] > mas[i+1] for i in range(len(mas)-1))
                price_above_all = current_price > mas[0]

                if rainbow_aligned and price_above_all:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Rainbow breaks (any MA crosses another)
            elif symbol in portfolio.positions:
                # Check if any MA crosses below the next one
                rainbow_broken = any(mas[i] <= mas[i+1] for i in range(len(mas)-1))
                price_below_fast = current_price < mas[0]

                if rainbow_broken or price_below_fast:
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class TrendSurfingExtremeStrategy(BaseStrategy):
    """
    CRAZY Trend Surfing Extreme: Aggressive trend following with trailing stops
    Uses Parabolic SAR concept with tight trailing
    """

    def __init__(self, trail_pct: float = 3.0, position_size_pct: float = 0.17):
        super().__init__("Trend Surfing Extreme")
        self.trail_pct = trail_pct
        self.position_size_pct = position_size_pct
        self.entry_prices = {}
        self.highest_prices = {}

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < 50:
                continue

            sma20 = self.calculate_sma(df, 20, date)
            sma50 = self.calculate_sma(df, 50, date)
            rsi = self.calculate_rsi(df, 14, date)

            if None in [sma20, sma50, rsi]:
                continue

            current_price = df.loc[date, 'close']
            current_high = df.loc[date, 'high']

            # BUY Signal: Strong uptrend with momentum
            if symbol not in portfolio.positions:
                strong_uptrend = sma20 > sma50 and current_price > sma20
                good_momentum = rsi > 55 and rsi < 75

                if strong_uptrend and good_momentum:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })
                        self.entry_prices[symbol] = current_price
                        self.highest_prices[symbol] = current_high

            # SELL Signal: Trailing stop hit
            elif symbol in portfolio.positions:
                # Update highest price
                if symbol in self.highest_prices:
                    self.highest_prices[symbol] = max(self.highest_prices[symbol], current_high)
                else:
                    self.highest_prices[symbol] = current_high

                # Calculate trailing stop
                trailing_stop = self.highest_prices[symbol] * (1 - self.trail_pct / 100)

                if current_price < trailing_stop:
                    quantity = portfolio.positions[symbol].quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })
                    # Clean up tracking
                    if symbol in self.entry_prices:
                        del self.entry_prices[symbol]
                    if symbol in self.highest_prices:
                        del self.highest_prices[symbol]

        return signals


class BreakoutBanditStrategy(BaseStrategy):
    """
    CRAZY Breakout Bandit: Trades 52-week highs aggressively
    When a stock breaks multi-month highs, rides the momentum
    """

    def __init__(self, lookback_period: int = 252,
                 min_consolidation_days: int = 20,
                 position_size_pct: float = 0.13):
        super().__init__("Breakout Bandit")
        self.lookback_period = lookback_period
        self.min_consolidation_days = min_consolidation_days
        self.position_size_pct = position_size_pct

    def is_consolidating(self, df: pd.DataFrame, date, days: int) -> bool:
        """Check if price was consolidating"""
        idx = df.index.get_loc(date)
        if idx < days:
            return False

        recent_prices = df['close'].iloc[max(0, idx - days):idx]
        price_range = (recent_prices.max() - recent_prices.min()) / recent_prices.mean()

        # Consolidation if range is less than 10%
        return price_range < 0.10

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < self.lookback_period:
                continue

            current_price = df.loc[date, 'close']
            current_volume = df.loc[date, 'volume']

            # Get highest price in lookback period (excluding today)
            lookback_high = df['high'].iloc[max(0, idx - self.lookback_period):idx].max()
            avg_volume = df['volume'].iloc[max(0, idx - 20):idx].mean()

            # BUY Signal: Breaks 52-week high with volume
            if symbol not in portfolio.positions:
                breaks_high = current_price > lookback_high
                strong_volume = current_volume > avg_volume * 1.5
                was_consolidating = self.is_consolidating(df, date, self.min_consolidation_days)

                if breaks_high and strong_volume and was_consolidating:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Falls below 20-day low or 8% stop loss
            elif symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                low_20 = df['low'].iloc[max(0, idx - 20):idx].min()
                stop_loss = position.avg_price * 0.92

                if current_price < low_20 or current_price < stop_loss:
                    quantity = position.quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals


class SwingScalperStrategy(BaseStrategy):
    """
    CRAZY Swing Scalper: Rapid swing trading on intraday momentum
    Catches 2-5% swings with quick entries and exits
    """

    def __init__(self, target_profit_pct: float = 3.0,
                 stop_loss_pct: float = 1.5,
                 position_size_pct: float = 0.11):
        super().__init__("Swing Scalper")
        self.target_profit_pct = target_profit_pct
        self.stop_loss_pct = stop_loss_pct
        self.position_size_pct = position_size_pct

    def generate_signals(self, date, data: Dict[str, pd.DataFrame], portfolio) -> List[Dict[str, Any]]:
        signals = []

        for symbol, df in data.items():
            if date not in df.index:
                continue

            idx = df.index.get_loc(date)
            if idx < 10:
                continue

            ema5 = self.calculate_ema(df, 5, date)
            ema10 = self.calculate_ema(df, 10, date)
            rsi = self.calculate_rsi(df, 7, date)  # Fast RSI

            if None in [ema5, ema10, rsi]:
                continue

            current_price = df.loc[date, 'close']

            # BUY Signal: Fast EMA crosses above with RSI confirmation
            if symbol not in portfolio.positions:
                fast_cross = ema5 > ema10
                rsi_strong = rsi > 50 and rsi < 70

                # Check for recent upward momentum
                prev_close = df.iloc[idx - 1]['close']
                momentum = ((current_price - prev_close) / prev_close) > 0.01

                if fast_cross and rsi_strong and momentum:
                    available_cash = portfolio.cash * self.position_size_pct
                    quantity = int(available_cash / current_price)

                    if quantity > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'BUY',
                            'quantity': quantity
                        })

            # SELL Signal: Hit profit target or stop loss
            elif symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                hit_target = profit_pct >= self.target_profit_pct
                hit_stop = profit_pct <= -self.stop_loss_pct
                ema_cross_down = ema5 < ema10

                if hit_target or hit_stop or ema_cross_down:
                    quantity = position.quantity
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity
                    })

        return signals
