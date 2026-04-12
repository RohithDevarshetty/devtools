#!/usr/bin/env python3
"""
Showcase of all 13 crazy trading strategies
Demonstrates each strategy with a quick backtest
"""

from backtesting_engine import BacktestEngine
from trading_strategies import *
from data_fetcher import DataGenerator
from performance_analyzer import PerformanceAnalyzer, StrategyComparer
from datetime import datetime, timedelta


def showcase_all_strategies():
    """Run a quick showcase of all 13 strategies"""
    print("\n" + "=" * 80)
    print("🎪 SHOWCASE: ALL 13 CRAZY TRADING STRATEGIES")
    print("=" * 80)

    # Generate test data
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    print("\n📊 Generating diverse market data for testing...")
    data = DataGenerator.mixed_market_scenarios(n_stocks=6, start_date=start_date, end_date=end_date)
    print(f"  ✓ Generated data for {len(data)} stocks with varied market conditions")

    # All 13 strategies
    all_strategies = [
        # Original 6
        ("💥 Momentum Explosion", MomentumExplosionStrategy(position_size_pct=0.15)),
        ("🎯 Mean Reversion Madness", MeanReversionMadnessStrategy(position_size_pct=0.12)),
        ("⚡ Volatility Breakout", VolatilityBreakoutStrategy(position_size_pct=0.10)),
        ("🔥 SuperTrend Follower", SuperTrendFollowerStrategy(position_size_pct=0.20)),
        ("🎪 Bollinger Squeeze", BollingerSqueezeStrategy(position_size_pct=0.15)),
        ("🚀 Gap and Go", GapAndGoStrategy(position_size_pct=0.12)),

        # New 7
        ("🚁 Triple Momentum Rocket", TripleMomentumRocketStrategy(position_size_pct=0.18)),
        ("🎣 Reversal Hunter", ReversalHunterStrategy(position_size_pct=0.14)),
        ("📢 Volume Explosion", VolumeExplosionStrategy(position_size_pct=0.16)),
        ("🌈 MA Rainbow", MovingAverageRainbowStrategy(position_size_pct=0.20)),
        ("🏄 Trend Surfing Extreme", TrendSurfingExtremeStrategy(position_size_pct=0.17)),
        ("🎯 Breakout Bandit", BreakoutBanditStrategy(position_size_pct=0.13)),
        ("⚡ Swing Scalper", SwingScalperStrategy(position_size_pct=0.11))
    ]

    print("\n" + "=" * 80)
    print("RUNNING BACKTESTS ON ALL 13 STRATEGIES")
    print("=" * 80)
    print()

    comparer = StrategyComparer()
    initial_capital = 1000000  # 10 lakhs

    for emoji_name, strategy in all_strategies:
        print(f"\n{emoji_name}")
        print("-" * 80)

        # Run backtest
        engine = BacktestEngine(initial_capital=initial_capital)
        for symbol, df in data.items():
            engine.load_data(symbol, df)

        portfolio = engine.run(strategy, start_date, end_date)
        analyzer = PerformanceAnalyzer(portfolio)
        metrics = analyzer.calculate_metrics()

        # Add to comparison
        comparer.add_result(emoji_name, analyzer)

        # Print quick summary
        print(f"  Strategy Type:    {strategy.__class__.__doc__.split(':')[0].strip()}")
        print(f"  Total Return:     {metrics['total_return_pct']:+.2f}%")
        print(f"  CAGR:             {metrics['cagr_pct']:.2f}%")
        print(f"  Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown:     {metrics['max_drawdown_pct']:.2f}%")
        print(f"  Win Rate:         {metrics['win_rate_pct']:.2f}%")
        print(f"  Total Trades:     {metrics['total_trades']}")
        print(f"  Profit Factor:    {metrics['profit_factor']:.2f}")

    # Print final comparison
    print("\n" + "=" * 80)
    print("FINAL COMPARISON: ALL 13 STRATEGIES")
    print("=" * 80)
    comparer.print_comparison()

    print("\n" + "=" * 80)
    print("STRATEGY CATEGORIES")
    print("=" * 80)
    print("""
🔵 TREND FOLLOWING STRATEGIES:
  - 💥 Momentum Explosion: EMA crossover with RSI
  - 🔥 SuperTrend Follower: Multi-indicator confirmation
  - 🚁 Triple Momentum Rocket: RSI + MACD + ROC alignment
  - 🏄 Trend Surfing Extreme: Trailing stop trend rider
  - 🌈 MA Rainbow: 5 MA alignment system

🟢 MEAN REVERSION STRATEGIES:
  - 🎯 Mean Reversion Madness: Bollinger Bands extremes
  - 🎣 Reversal Hunter: Candlestick patterns + oversold RSI

🟡 BREAKOUT STRATEGIES:
  - ⚡ Volatility Breakout: ATR-based breakouts
  - 🎯 Breakout Bandit: 52-week high breakouts
  - 🎪 Bollinger Squeeze: Volatility compression plays

🟠 VOLUME-BASED STRATEGIES:
  - 📢 Volume Explosion: Massive volume spike trading

🔴 GAP & MOMENTUM STRATEGIES:
  - 🚀 Gap and Go: Morning gap momentum
  - ⚡ Swing Scalper: Quick swing trades with tight stops

Each strategy has unique characteristics and performs differently in various
market conditions. Use the comparison above to find the best fit for your
trading style and market expectations.
    """)

    print("=" * 80)
    print("\n✅ Showcase complete! All 13 strategies demonstrated successfully.\n")


if __name__ == "__main__":
    showcase_all_strategies()
