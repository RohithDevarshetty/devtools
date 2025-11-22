"""
Performance Analyzer for Trading Strategies
Calculates comprehensive metrics and generates reports
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import json


class PerformanceAnalyzer:
    """Analyzes backtest results and calculates performance metrics"""

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.metrics = {}

    def calculate_metrics(self) -> Dict:
        """Calculate all performance metrics"""

        if not self.portfolio.equity_curve:
            return {"error": "No equity curve data available"}

        # Extract equity curve
        dates, values = zip(*self.portfolio.equity_curve)
        equity_series = pd.Series(values, index=dates)

        # Calculate returns
        returns = equity_series.pct_change().dropna()

        # Basic metrics
        initial_capital = self.portfolio.initial_capital
        final_value = self.portfolio.get_total_value()
        total_return = ((final_value - initial_capital) / initial_capital) * 100

        # Calculate metrics
        self.metrics = {
            'initial_capital': round(initial_capital, 2),
            'final_value': round(final_value, 2),
            'total_return_pct': round(total_return, 2),
            'total_return_inr': round(final_value - initial_capital, 2),

            # Trade statistics
            'total_trades': len(self.portfolio.trades),
            'total_buy_trades': sum(1 for t in self.portfolio.trades if t.order_type.value == 'BUY'),
            'total_sell_trades': sum(1 for t in self.portfolio.trades if t.order_type.value == 'SELL'),
            'total_commission_paid': round(sum(t.commission for t in self.portfolio.trades), 2),

            # Risk metrics
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'max_drawdown_pct': self._calculate_max_drawdown(equity_series),
            'volatility_annual': round(returns.std() * np.sqrt(252) * 100, 2),

            # Win rate
            'win_rate_pct': self._calculate_win_rate(),
            'avg_win_pct': self._calculate_avg_win(),
            'avg_loss_pct': self._calculate_avg_loss(),
            'profit_factor': self._calculate_profit_factor(),

            # Time metrics
            'start_date': str(dates[0].date()),
            'end_date': str(dates[-1].date()),
            'trading_days': len(equity_series),

            # Current positions
            'open_positions': len(self.portfolio.positions),
            'position_value': round(self.portfolio.get_position_value(), 2),
            'cash_remaining': round(self.portfolio.cash, 2),
        }

        # Calculate CAGR
        years = (dates[-1] - dates[0]).days / 365.25
        if years > 0:
            cagr = (((final_value / initial_capital) ** (1 / years)) - 1) * 100
            self.metrics['cagr_pct'] = round(cagr, 2)
        else:
            self.metrics['cagr_pct'] = 0.0

        # Calmar ratio
        if self.metrics['max_drawdown_pct'] != 0:
            self.metrics['calmar_ratio'] = round(
                self.metrics['cagr_pct'] / abs(self.metrics['max_drawdown_pct']), 2
            )
        else:
            self.metrics['calmar_ratio'] = 0.0

        return self.metrics

    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.06) -> float:
        """Calculate Sharpe Ratio (assuming 6% risk-free rate for India)"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252)
        return round(sharpe, 2)

    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.06) -> float:
        """Calculate Sortino Ratio (downside deviation only)"""
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
        return round(sortino, 2)

    def _calculate_max_drawdown(self, equity_series: pd.Series) -> float:
        """Calculate maximum drawdown percentage"""
        if len(equity_series) == 0:
            return 0.0

        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax * 100
        max_dd = drawdown.min()

        return round(max_dd, 2)

    def _calculate_win_rate(self) -> float:
        """Calculate percentage of winning trades"""
        if len(self.portfolio.trades) == 0:
            return 0.0

        # Match buy and sell trades
        buy_trades = [t for t in self.portfolio.trades if t.order_type.value == 'BUY']
        sell_trades = [t for t in self.portfolio.trades if t.order_type.value == 'SELL']

        if len(sell_trades) == 0:
            return 0.0

        wins = sum(1 for st in sell_trades
                  for bt in buy_trades
                  if st.symbol == bt.symbol and st.price > bt.price)

        return round((wins / len(sell_trades)) * 100, 2)

    def _calculate_avg_win(self) -> float:
        """Calculate average winning trade percentage"""
        winning_trades = self._get_trade_pairs()
        wins = [pct for pct in winning_trades if pct > 0]

        if len(wins) == 0:
            return 0.0

        return round(np.mean(wins), 2)

    def _calculate_avg_loss(self) -> float:
        """Calculate average losing trade percentage"""
        trade_returns = self._get_trade_pairs()
        losses = [pct for pct in trade_returns if pct < 0]

        if len(losses) == 0:
            return 0.0

        return round(np.mean(losses), 2)

    def _calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        trade_returns = self._get_trade_pairs()

        gross_profit = sum(pct for pct in trade_returns if pct > 0)
        gross_loss = abs(sum(pct for pct in trade_returns if pct < 0))

        if gross_loss == 0:
            return 0.0 if gross_profit == 0 else float('inf')

        return round(gross_profit / gross_loss, 2)

    def _get_trade_pairs(self) -> List[float]:
        """Get matched buy-sell trade pairs and calculate returns"""
        buy_trades = {}
        returns = []

        for trade in self.portfolio.trades:
            if trade.order_type.value == 'BUY':
                if trade.symbol not in buy_trades:
                    buy_trades[trade.symbol] = []
                buy_trades[trade.symbol].append(trade)

            elif trade.order_type.value == 'SELL':
                if trade.symbol in buy_trades and buy_trades[trade.symbol]:
                    buy_trade = buy_trades[trade.symbol].pop(0)
                    return_pct = ((trade.price - buy_trade.price) / buy_trade.price) * 100
                    returns.append(return_pct)

        return returns

    def print_report(self):
        """Print detailed performance report"""
        if not self.metrics:
            self.calculate_metrics()

        print("\n" + "=" * 80)
        print("TRADING STRATEGY BACKTEST REPORT")
        print("=" * 80)

        print(f"\n📊 OVERALL PERFORMANCE")
        print("-" * 80)
        print(f"Initial Capital:        ₹{self.metrics['initial_capital']:,.2f}")
        print(f"Final Value:            ₹{self.metrics['final_value']:,.2f}")
        print(f"Total Return:           ₹{self.metrics['total_return_inr']:,.2f} ({self.metrics['total_return_pct']:+.2f}%)")
        print(f"CAGR:                   {self.metrics['cagr_pct']:.2f}%")

        print(f"\n📈 RISK METRICS")
        print("-" * 80)
        print(f"Max Drawdown:           {self.metrics['max_drawdown_pct']:.2f}%")
        print(f"Annual Volatility:      {self.metrics['volatility_annual']:.2f}%")
        print(f"Sharpe Ratio:           {self.metrics['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio:          {self.metrics['sortino_ratio']:.2f}")
        print(f"Calmar Ratio:           {self.metrics['calmar_ratio']:.2f}")

        print(f"\n💼 TRADE STATISTICS")
        print("-" * 80)
        print(f"Total Trades:           {self.metrics['total_trades']}")
        print(f"  - Buy Trades:         {self.metrics['total_buy_trades']}")
        print(f"  - Sell Trades:        {self.metrics['total_sell_trades']}")
        print(f"Win Rate:               {self.metrics['win_rate_pct']:.2f}%")
        print(f"Average Win:            {self.metrics['avg_win_pct']:+.2f}%")
        print(f"Average Loss:           {self.metrics['avg_loss_pct']:+.2f}%")
        print(f"Profit Factor:          {self.metrics['profit_factor']:.2f}")
        print(f"Total Commission:       ₹{self.metrics['total_commission_paid']:,.2f}")

        print(f"\n📅 PERIOD")
        print("-" * 80)
        print(f"Start Date:             {self.metrics['start_date']}")
        print(f"End Date:               {self.metrics['end_date']}")
        print(f"Trading Days:           {self.metrics['trading_days']}")

        print(f"\n💰 CURRENT STATUS")
        print("-" * 80)
        print(f"Open Positions:         {self.metrics['open_positions']}")
        print(f"Position Value:         ₹{self.metrics['position_value']:,.2f}")
        print(f"Cash Remaining:         ₹{self.metrics['cash_remaining']:,.2f}")

        print("\n" + "=" * 80)

    def print_trades(self, limit: int = 20):
        """Print trade history"""
        print(f"\n📋 TRADE HISTORY (Last {limit} trades)")
        print("-" * 100)
        print(f"{'Date':<12} {'Symbol':<15} {'Type':<6} {'Quantity':<10} {'Price':<12} {'Commission':<12}")
        print("-" * 100)

        for trade in self.portfolio.trades[-limit:]:
            print(f"{trade.date.strftime('%Y-%m-%d'):<12} "
                  f"{trade.symbol:<15} "
                  f"{trade.order_type.value:<6} "
                  f"{trade.quantity:<10} "
                  f"₹{trade.price:<11,.2f} "
                  f"₹{trade.commission:<11,.2f}")

        print("-" * 100)

    def print_positions(self):
        """Print current positions"""
        if not self.portfolio.positions:
            print("\n📦 No open positions")
            return

        print(f"\n📦 OPEN POSITIONS")
        print("-" * 100)
        print(f"{'Symbol':<15} {'Quantity':<10} {'Avg Price':<12} {'Current Price':<15} {'P&L':<15} {'P&L %':<10}")
        print("-" * 100)

        for symbol, pos in self.portfolio.positions.items():
            pl_color = "+" if pos.profit_loss >= 0 else ""
            print(f"{symbol:<15} "
                  f"{pos.quantity:<10} "
                  f"₹{pos.avg_price:<11,.2f} "
                  f"₹{pos.current_price:<14,.2f} "
                  f"₹{pos.profit_loss:<14,.2f} "
                  f"{pl_color}{pos.profit_loss_pct:.2f}%")

        print("-" * 100)

    def export_to_json(self, filename: str):
        """Export metrics to JSON file"""
        if not self.metrics:
            self.calculate_metrics()

        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)

        print(f"\n✅ Metrics exported to {filename}")

    def export_trades_to_csv(self, filename: str):
        """Export trades to CSV file"""
        trades_data = []

        for trade in self.portfolio.trades:
            trades_data.append({
                'date': trade.date,
                'symbol': trade.symbol,
                'type': trade.order_type.value,
                'quantity': trade.quantity,
                'price': trade.price,
                'commission': trade.commission
            })

        df = pd.DataFrame(trades_data)
        df.to_csv(filename, index=False)

        print(f"✅ Trades exported to {filename}")


class StrategyComparer:
    """Compare multiple strategy results"""

    def __init__(self):
        self.results = {}

    def add_result(self, strategy_name: str, analyzer: PerformanceAnalyzer):
        """Add strategy result for comparison"""
        if not analyzer.metrics:
            analyzer.calculate_metrics()

        self.results[strategy_name] = analyzer.metrics

    def print_comparison(self):
        """Print comparison table"""
        if not self.results:
            print("No results to compare")
            return

        print("\n" + "=" * 120)
        print("STRATEGY COMPARISON")
        print("=" * 120)

        metrics_to_compare = [
            ('total_return_pct', 'Total Return %'),
            ('cagr_pct', 'CAGR %'),
            ('sharpe_ratio', 'Sharpe Ratio'),
            ('max_drawdown_pct', 'Max Drawdown %'),
            ('win_rate_pct', 'Win Rate %'),
            ('profit_factor', 'Profit Factor'),
            ('total_trades', 'Total Trades'),
        ]

        # Print header
        print(f"{'Metric':<25}", end='')
        for strategy_name in self.results.keys():
            print(f"{strategy_name[:20]:<22}", end='')
        print()
        print("-" * 120)

        # Print metrics
        for metric_key, metric_name in metrics_to_compare:
            print(f"{metric_name:<25}", end='')

            for strategy_name in self.results.keys():
                value = self.results[strategy_name].get(metric_key, 0)
                if isinstance(value, float):
                    print(f"{value:>20.2f}  ", end='')
                else:
                    print(f"{value:>20}  ", end='')
            print()

        print("=" * 120)

        # Find best strategy
        best_return = max(self.results.items(), key=lambda x: x[1].get('total_return_pct', 0))
        best_sharpe = max(self.results.items(), key=lambda x: x[1].get('sharpe_ratio', 0))

        print(f"\n🏆 Best Total Return:    {best_return[0]} ({best_return[1]['total_return_pct']:.2f}%)")
        print(f"🏆 Best Sharpe Ratio:    {best_sharpe[0]} ({best_sharpe[1]['sharpe_ratio']:.2f})")
        print()
