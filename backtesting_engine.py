"""
Advanced Backtesting Engine for Indian Stock Market
Supports multiple trading strategies with realistic execution simulation
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Trade:
    date: datetime
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    commission: float = 0.0


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    current_price: float

    @property
    def value(self) -> float:
        return self.quantity * self.current_price

    @property
    def profit_loss(self) -> float:
        return (self.current_price - self.avg_price) * self.quantity

    @property
    def profit_loss_pct(self) -> float:
        return ((self.current_price - self.avg_price) / self.avg_price) * 100


class Portfolio:
    def __init__(self, initial_capital: float, commission_rate: float = 0.0003):
        """
        Initialize portfolio

        Args:
            initial_capital: Starting capital in INR
            commission_rate: Commission rate (default 0.03% for Indian brokers)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []

    def get_position_value(self) -> float:
        """Get total value of all positions"""
        return sum(pos.value for pos in self.positions.values())

    def get_total_value(self) -> float:
        """Get total portfolio value (cash + positions)"""
        return self.cash + self.get_position_value()

    def can_buy(self, symbol: str, price: float, quantity: int) -> bool:
        """Check if we have enough cash to buy"""
        cost = price * quantity
        commission = cost * self.commission_rate
        return self.cash >= (cost + commission)

    def buy(self, date: datetime, symbol: str, price: float, quantity: int) -> bool:
        """Execute a buy order"""
        if not self.can_buy(symbol, price, quantity):
            return False

        cost = price * quantity
        commission = cost * self.commission_rate
        total_cost = cost + commission

        self.cash -= total_cost

        if symbol in self.positions:
            # Update existing position
            pos = self.positions[symbol]
            total_quantity = pos.quantity + quantity
            pos.avg_price = ((pos.avg_price * pos.quantity) + (price * quantity)) / total_quantity
            pos.quantity = total_quantity
        else:
            # Create new position
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_price=price,
                current_price=price
            )

        self.trades.append(Trade(
            date=date,
            symbol=symbol,
            order_type=OrderType.BUY,
            quantity=quantity,
            price=price,
            commission=commission
        ))

        return True

    def sell(self, date: datetime, symbol: str, price: float, quantity: int) -> bool:
        """Execute a sell order"""
        if symbol not in self.positions:
            return False

        pos = self.positions[symbol]
        if pos.quantity < quantity:
            return False

        revenue = price * quantity
        commission = revenue * self.commission_rate
        net_revenue = revenue - commission

        self.cash += net_revenue
        pos.quantity -= quantity

        if pos.quantity == 0:
            del self.positions[symbol]

        self.trades.append(Trade(
            date=date,
            symbol=symbol,
            order_type=OrderType.SELL,
            quantity=quantity,
            price=price,
            commission=commission
        ))

        return True

    def update_prices(self, date: datetime, prices: Dict[str, float]):
        """Update current prices for all positions"""
        for symbol, pos in self.positions.items():
            if symbol in prices:
                pos.current_price = prices[symbol]

        self.equity_curve.append((date, self.get_total_value()))


class BacktestEngine:
    def __init__(self, initial_capital: float = 1000000, commission_rate: float = 0.0003):
        """
        Initialize backtesting engine

        Args:
            initial_capital: Starting capital in INR (default 10 lakhs)
            commission_rate: Commission rate (default 0.03%)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.portfolio = None
        self.data: Dict[str, pd.DataFrame] = {}

    def load_data(self, symbol: str, df: pd.DataFrame):
        """Load price data for a symbol"""
        self.data[symbol] = df.copy()

    def run(self, strategy, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Portfolio:
        """
        Run backtest with given strategy

        Args:
            strategy: Trading strategy object with generate_signals method
            start_date: Start date for backtest (optional)
            end_date: End date for backtest (optional)

        Returns:
            Portfolio object with results
        """
        self.portfolio = Portfolio(self.initial_capital, self.commission_rate)

        # Get all unique dates across all symbols
        all_dates = set()
        for df in self.data.values():
            all_dates.update(df.index)

        all_dates = sorted(all_dates)

        if start_date:
            all_dates = [d for d in all_dates if d >= pd.to_datetime(start_date)]
        if end_date:
            all_dates = [d for d in all_dates if d <= pd.to_datetime(end_date)]

        # Run strategy for each date
        for date in all_dates:
            # Get current prices
            current_prices = {}
            for symbol, df in self.data.items():
                if date in df.index:
                    current_prices[symbol] = df.loc[date, 'close']

            # Update portfolio prices
            self.portfolio.update_prices(date, current_prices)

            # Generate signals from strategy
            signals = strategy.generate_signals(date, self.data, self.portfolio)

            # Execute signals
            for signal in signals:
                symbol = signal['symbol']
                action = signal['action']

                if symbol not in current_prices:
                    continue

                price = current_prices[symbol]

                if action == 'BUY':
                    quantity = signal.get('quantity', 0)
                    if quantity > 0:
                        self.portfolio.buy(date, symbol, price, quantity)

                elif action == 'SELL':
                    quantity = signal.get('quantity', 0)
                    if quantity > 0:
                        self.portfolio.sell(date, symbol, price, quantity)

        return self.portfolio
