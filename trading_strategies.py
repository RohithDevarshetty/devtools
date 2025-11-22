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
