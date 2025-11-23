# 🇮🇳 Indian Market Backtesting System

A comprehensive, production-ready backtesting framework for testing **crazy trading strategies** on the Indian stock market (NSE/BSE).

## 🚀 Features

- **Complete Backtesting Engine**: Realistic portfolio management with commission tracking
- **13 Crazy Trading Strategies**:
  - 💥 Momentum Explosion - Aggressive trend following
  - 🎯 Mean Reversion Madness - Extreme oversold/overbought trading
  - ⚡ Volatility Breakout - Trades explosive price moves
  - 🔥 SuperTrend Follower - Multi-indicator confirmation system
  - 🎪 Bollinger Squeeze - Volatility compression plays
  - 🚀 Gap and Go - Morning gap trading
  - 🚁 Triple Momentum Rocket - Combines RSI, MACD & ROC
  - 🎣 Reversal Hunter - Catches V-shaped reversals with candlestick patterns
  - 📢 Volume Explosion - Trades massive volume spikes
  - 🌈 MA Rainbow - 5 moving average alignment system
  - 🏄 Trend Surfing Extreme - Aggressive trailing stop strategy
  - 🎯 Breakout Bandit - 52-week high breakout trader
  - ⚡ Swing Scalper - Quick 2-5% swing trades
- **Comprehensive Performance Metrics**: Sharpe ratio, Sortino ratio, max drawdown, CAGR, win rate, and more
- **Real Indian Market Data**: Support for NSE/BSE stocks via yfinance
- **Sample Data Generation**: Test strategies without internet connection
- **Strategy Comparison**: Compare multiple strategies side-by-side

## 📦 Installation

```bash
# Clone or download this repository
cd devtools

# Install dependencies
pip install -r requirements.txt
```

## 🎮 Quick Start

### Run the Interactive Menu

```bash
python run_backtest.py
```

This will present you with options:
1. Run single strategy backtest (Quick)
2. Compare multiple strategies (Comprehensive)
3. Backtest with real Indian stocks
4. Run custom backtest (Advanced)
5. Run all tests

### Example: Simple Backtest

```python
from backtesting_engine import BacktestEngine
from trading_strategies import MomentumExplosionStrategy
from data_fetcher import IndianMarketDataFetcher
from performance_analyzer import PerformanceAnalyzer

# Generate sample data
data = {}
stocks = ['RELIANCE', 'TCS', 'INFY']
for stock in stocks:
    data[stock] = IndianMarketDataFetcher.generate_sample_data(
        stock, '2023-01-01', '2024-01-01'
    )

# Initialize engine with 10 lakhs capital
engine = BacktestEngine(initial_capital=1000000)

# Load data
for symbol, df in data.items():
    engine.load_data(symbol, df)

# Run strategy
strategy = MomentumExplosionStrategy(position_size_pct=0.15)
portfolio = engine.run(strategy)

# Analyze results
analyzer = PerformanceAnalyzer(portfolio)
analyzer.calculate_metrics()
analyzer.print_report()
```

## 📊 Trading Strategies

### 1. Momentum Explosion Strategy
Aggressively rides strong trends using EMA crossovers and RSI confirmation.

**Parameters:**
- `fast_period`: Fast EMA period (default: 10)
- `slow_period`: Slow EMA period (default: 50)
- `rsi_threshold`: RSI threshold for momentum (default: 60)
- `position_size_pct`: Position size as % of capital (default: 0.15)

### 2. Mean Reversion Madness Strategy
Buys extreme oversold conditions, sells overbought using Bollinger Bands and RSI.

**Parameters:**
- `bb_period`: Bollinger Band period (default: 20)
- `bb_std`: Standard deviations (default: 2.5)
- `rsi_oversold`: RSI oversold level (default: 25)
- `rsi_overbought`: RSI overbought level (default: 75)

### 3. Volatility Breakout Strategy
Trades price breakouts with ATR-based stops.

**Parameters:**
- `atr_period`: ATR calculation period (default: 14)
- `breakout_multiplier`: Stop loss multiplier (default: 2.0)

### 4. SuperTrend Follower Strategy
Multi-indicator strategy combining Moving Averages, MACD, and RSI.

### 5. Bollinger Squeeze Strategy
Identifies volatility compression and trades the expansion breakout.

**Parameters:**
- `bb_period`: Bollinger Band period (default: 20)
- `squeeze_threshold`: Bandwidth threshold (default: 0.015)

### 6. Gap and Go Strategy
Exploits morning gaps with momentum follow-through.

**Parameters:**
- `min_gap_pct`: Minimum gap percentage (default: 2.0%)

### 7. Triple Momentum Rocket Strategy
Ultra-aggressive momentum strategy combining three indicators: RSI, MACD, and Rate of Change. Only enters when all momentum indicators align explosively.

**Parameters:**
- `roc_period`: Rate of Change lookback period (default: 10)
- `position_size_pct`: Position size as % of capital (default: 0.18)

### 8. Reversal Hunter Strategy
Catches V-shaped reversals after extreme moves using candlestick patterns (hammer, bullish engulfing) combined with oversold RSI.

**Parameters:**
- `rsi_extreme`: RSI level for extreme oversold (default: 20)
- `position_size_pct`: Position size (default: 0.14)

### 9. Volume Explosion Strategy
Trades on massive volume spikes (2.5x+ average volume). When volume explodes with price momentum, rides the wave.

**Parameters:**
- `volume_multiplier`: Volume spike threshold (default: 2.5)
- `volume_period`: Average volume lookback (default: 20)
- `position_size_pct`: Position size (default: 0.16)

### 10. Moving Average Rainbow Strategy
Uses 5 moving averages (5, 10, 20, 50, 100 periods) and only enters when they align in perfect ascending order - creating a "rainbow" effect.

**Parameters:**
- `position_size_pct`: Position size (default: 0.20)

### 11. Trend Surfing Extreme Strategy
Aggressive trend following with tight 3% trailing stops. Uses Parabolic SAR concept to ride trends while protecting profits.

**Parameters:**
- `trail_pct`: Trailing stop percentage (default: 3.0%)
- `position_size_pct`: Position size (default: 0.17)

### 12. Breakout Bandit Strategy
Trades 52-week high breakouts after consolidation periods. Waits for price to consolidate, then catches the explosive breakout.

**Parameters:**
- `lookback_period`: Breakout lookback period (default: 252 days)
- `min_consolidation_days`: Minimum consolidation period (default: 20)
- `position_size_pct`: Position size (default: 0.13)

### 13. Swing Scalper Strategy
Rapid swing trading targeting 2-5% moves. Uses fast EMAs (5, 10) for quick entries and exits with tight profit targets and stop losses.

**Parameters:**
- `target_profit_pct`: Profit target percentage (default: 3.0%)
- `stop_loss_pct`: Stop loss percentage (default: 1.5%)
- `position_size_pct`: Position size (default: 0.11)

## 📈 Performance Metrics

The analyzer calculates:

- **Return Metrics**: Total return, CAGR, absolute profit/loss
- **Risk Metrics**: Sharpe ratio, Sortino ratio, max drawdown, volatility
- **Trade Statistics**: Win rate, profit factor, average win/loss
- **Risk-Adjusted**: Calmar ratio (CAGR/Max Drawdown)

## 🔧 Advanced Usage

### Compare Multiple Strategies

```python
from performance_analyzer import StrategyComparer

comparer = StrategyComparer()

# Run multiple strategies and add results
for strategy in [MomentumExplosionStrategy(), MeanReversionMadnessStrategy()]:
    engine = BacktestEngine(initial_capital=1000000)
    # ... load data and run ...
    analyzer = PerformanceAnalyzer(portfolio)
    comparer.add_result(strategy.name, analyzer)

# Print comparison table
comparer.print_comparison()
```

### Use Real NSE/BSE Data

```python
from data_fetcher import IndianMarketDataFetcher

# Fetch real data (requires yfinance)
data = IndianMarketDataFetcher.fetch_multiple_stocks(
    ['RELIANCE', 'TCS', 'INFY'],
    start_date='2023-01-01',
    end_date='2024-01-01',
    exchange='NSE'  # or 'BSE'
)
```

### Create Custom Strategy

```python
from trading_strategies import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("My Custom Strategy")

    def generate_signals(self, date, data, portfolio):
        signals = []
        # Your strategy logic here
        # Return list of {'symbol': ..., 'action': 'BUY'/'SELL', 'quantity': ...}
        return signals
```

### Export Results

```python
analyzer.export_to_json('results.json')
analyzer.export_trades_to_csv('trades.csv')
```

## 📁 Project Structure

```
devtools/
├── backtesting_engine.py      # Core backtesting engine
├── trading_strategies.py      # 6 trading strategies
├── data_fetcher.py            # Data fetching and generation
├── performance_analyzer.py    # Performance metrics and reporting
├── run_backtest.py           # Main runner script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Example Output

```
================================================================================
TRADING STRATEGY BACKTEST REPORT
================================================================================

📊 OVERALL PERFORMANCE
--------------------------------------------------------------------------------
Initial Capital:        ₹10,00,000.00
Final Value:            ₹13,45,678.00
Total Return:           ₹3,45,678.00 (+34.57%)
CAGR:                   15.23%

📈 RISK METRICS
--------------------------------------------------------------------------------
Max Drawdown:           -12.45%
Annual Volatility:      18.34%
Sharpe Ratio:           1.45
Sortino Ratio:          2.01
Calmar Ratio:           1.22

💼 TRADE STATISTICS
--------------------------------------------------------------------------------
Total Trades:           145
  - Buy Trades:         73
  - Sell Trades:        72
Win Rate:               58.33%
Average Win:            +4.23%
Average Loss:           -2.15%
Profit Factor:          1.89
Total Commission:       ₹4,234.00
```

## ⚠️ Disclaimer

This is a backtesting framework for educational and research purposes only.

- Past performance does not guarantee future results
- Always test strategies thoroughly before live trading
- Consider transaction costs, slippage, and market impact
- Consult a financial advisor before making investment decisions
- The authors are not responsible for any trading losses

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new trading strategies
- Improve performance metrics
- Add visualization capabilities
- Enhance data fetching

## 📝 License

MIT License - Feel free to use and modify for your projects!

## 🔥 Tips for Best Results

1. **Test Multiple Strategies**: No single strategy works in all market conditions
2. **Adjust Position Sizing**: Conservative position sizes (10-15%) reduce risk
3. **Use Real Data**: Test with actual NSE/BSE data before going live
4. **Monitor Drawdowns**: Keep max drawdown below -20%
5. **Optimize Parameters**: Backtest different parameter combinations
6. **Consider Commissions**: Indian brokers typically charge 0.03-0.05%

## 🚀 Next Steps

- Add visualization (equity curves, drawdown charts)
- Implement walk-forward optimization
- Add more Indian market indicators (Nifty correlation, sector rotation)
- Support for options strategies
- Real-time paper trading integration

---

**Happy Backtesting! 📈💰🇮🇳**
