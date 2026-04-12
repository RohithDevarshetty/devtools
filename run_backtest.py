#!/usr/bin/env python3
"""
Main runner for Indian Market Backtesting System
Run crazy trading strategies and compare results!
"""

from backtesting_engine import BacktestEngine
from trading_strategies import (
    MomentumExplosionStrategy,
    MeanReversionMadnessStrategy,
    VolatilityBreakoutStrategy,
    SuperTrendFollowerStrategy,
    BollingerSqueezeStrategy,
    GapAndGoStrategy,
    TripleMomentumRocketStrategy,
    ReversalHunterStrategy,
    VolumeExplosionStrategy,
    MovingAverageRainbowStrategy,
    TrendSurfingExtremeStrategy,
    BreakoutBanditStrategy,
    SwingScalperStrategy
)
from data_fetcher import IndianMarketDataFetcher, DataGenerator
from performance_analyzer import PerformanceAnalyzer, StrategyComparer
from datetime import datetime, timedelta


def run_single_strategy_backtest():
    """Run backtest with a single strategy"""
    print("\n🚀 RUNNING SINGLE STRATEGY BACKTEST")
    print("=" * 80)

    # Set parameters
    initial_capital = 1000000  # 10 lakhs
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Fetch data for Indian stocks
    print("\n📊 Fetching market data...")
    stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'WIPRO']

    # Generate sample data (use real data if yfinance is available)
    data = {}
    for stock in stocks:
        print(f"  Loading {stock}...")
        data[stock] = IndianMarketDataFetcher.generate_sample_data(
            stock, start_date, end_date,
            initial_price=1000 + hash(stock) % 1000,
            volatility=0.02
        )

    # Initialize backtesting engine
    engine = BacktestEngine(initial_capital=initial_capital)

    # Load data into engine
    for symbol, df in data.items():
        engine.load_data(symbol, df)

    # Run backtest with Momentum Explosion Strategy
    print("\n🎯 Running Momentum Explosion Strategy...")
    strategy = MomentumExplosionStrategy(
        fast_period=10,
        slow_period=50,
        rsi_threshold=60,
        position_size_pct=0.15
    )

    portfolio = engine.run(strategy, start_date, end_date)

    # Analyze results
    analyzer = PerformanceAnalyzer(portfolio)
    analyzer.calculate_metrics()
    analyzer.print_report()
    analyzer.print_positions()
    analyzer.print_trades(limit=10)

    return analyzer


def run_multiple_strategies_comparison():
    """Run and compare multiple trading strategies"""
    print("\n🚀 RUNNING MULTIPLE STRATEGIES COMPARISON")
    print("=" * 80)

    # Set parameters
    initial_capital = 1000000  # 10 lakhs
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Generate mixed market scenarios for better testing
    print("\n📊 Generating market data with mixed scenarios...")
    data = DataGenerator.mixed_market_scenarios(n_stocks=8, start_date=start_date, end_date=end_date)
    print(f"  ✓ Generated data for {len(data)} stocks")

    # Define strategies to test
    strategies = [
        MomentumExplosionStrategy(fast_period=10, slow_period=50, position_size_pct=0.15),
        MeanReversionMadnessStrategy(bb_period=20, bb_std=2.5, position_size_pct=0.12),
        VolatilityBreakoutStrategy(atr_period=14, breakout_multiplier=2.0, position_size_pct=0.10),
        SuperTrendFollowerStrategy(position_size_pct=0.20),
        BollingerSqueezeStrategy(bb_period=20, squeeze_threshold=0.015, position_size_pct=0.15),
        GapAndGoStrategy(min_gap_pct=2.0, position_size_pct=0.12),
        TripleMomentumRocketStrategy(roc_period=10, position_size_pct=0.18),
        ReversalHunterStrategy(rsi_extreme=20, position_size_pct=0.14),
        VolumeExplosionStrategy(volume_multiplier=2.5, position_size_pct=0.16),
        MovingAverageRainbowStrategy(position_size_pct=0.20),
        TrendSurfingExtremeStrategy(trail_pct=3.0, position_size_pct=0.17),
        BreakoutBanditStrategy(lookback_period=252, position_size_pct=0.13),
        SwingScalperStrategy(target_profit_pct=3.0, stop_loss_pct=1.5, position_size_pct=0.11)
    ]

    # Run backtest for each strategy
    comparer = StrategyComparer()

    for strategy in strategies:
        print(f"\n🎯 Running {strategy.name}...")

        # Initialize engine
        engine = BacktestEngine(initial_capital=initial_capital)

        # Load data
        for symbol, df in data.items():
            engine.load_data(symbol, df)

        # Run backtest
        portfolio = engine.run(strategy, start_date, end_date)

        # Analyze
        analyzer = PerformanceAnalyzer(portfolio)
        analyzer.calculate_metrics()

        # Add to comparer
        comparer.add_result(strategy.name, analyzer)

        print(f"  ✓ Complete - Return: {analyzer.metrics['total_return_pct']:.2f}%, "
              f"Sharpe: {analyzer.metrics['sharpe_ratio']:.2f}, "
              f"Trades: {analyzer.metrics['total_trades']}")

    # Print comparison
    comparer.print_comparison()

    return comparer


def run_real_stocks_backtest():
    """Run backtest with real Indian stocks (requires yfinance)"""
    print("\n🚀 RUNNING BACKTEST WITH REAL INDIAN STOCKS")
    print("=" * 80)

    # Set parameters
    initial_capital = 1000000  # 10 lakhs
    start_date = '2023-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Popular Indian stocks
    stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']

    print("\n📊 Fetching real market data from NSE...")
    data = IndianMarketDataFetcher.fetch_multiple_stocks(stocks, start_date, end_date, exchange='NSE')

    if not data:
        print("\n⚠️  Could not fetch real data. Make sure yfinance is installed:")
        print("    pip install yfinance")
        print("\n    Falling back to sample data...")
        data = {stock: IndianMarketDataFetcher.generate_sample_data(stock, start_date, end_date)
                for stock in stocks}

    # Run comparison with real data
    print("\n🎯 Running strategies on real/sample data...")

    strategies = [
        MomentumExplosionStrategy(position_size_pct=0.15),
        MeanReversionMadnessStrategy(position_size_pct=0.12),
        SuperTrendFollowerStrategy(position_size_pct=0.20)
    ]

    comparer = StrategyComparer()

    for strategy in strategies:
        print(f"\n  Testing {strategy.name}...")

        engine = BacktestEngine(initial_capital=initial_capital)

        for symbol, df in data.items():
            engine.load_data(symbol, df)

        portfolio = engine.run(strategy, start_date, end_date)
        analyzer = PerformanceAnalyzer(portfolio)
        analyzer.calculate_metrics()

        comparer.add_result(strategy.name, analyzer)

        print(f"    Return: {analyzer.metrics['total_return_pct']:.2f}%, "
              f"Sharpe: {analyzer.metrics['sharpe_ratio']:.2f}")

    comparer.print_comparison()

    return comparer


def run_custom_backtest():
    """Example of running a custom backtest with specific parameters"""
    print("\n🚀 RUNNING CUSTOM BACKTEST")
    print("=" * 80)

    # Custom parameters
    initial_capital = 500000  # 5 lakhs
    start_date = '2023-06-01'
    end_date = '2024-06-01'

    print("\n📊 Generating custom market data...")
    data = {
        'AGGRESSIVE': DataGenerator.volatile_market('AGG', start_date, end_date),
        'STABLE': DataGenerator.trending_market('STABLE', start_date, end_date, 'up'),
        'SIDEWAYS': DataGenerator.choppy_market('SIDE', start_date, end_date)
    }

    # Create custom strategy with specific parameters
    strategy = MomentumExplosionStrategy(
        fast_period=5,      # More aggressive
        slow_period=30,     # Shorter lookback
        rsi_threshold=55,   # Earlier entry
        position_size_pct=0.25  # Larger positions
    )

    print(f"\n🎯 Running custom {strategy.name}...")

    engine = BacktestEngine(initial_capital=initial_capital, commission_rate=0.0005)

    for symbol, df in data.items():
        engine.load_data(symbol, df)

    portfolio = engine.run(strategy, start_date, end_date)

    # Detailed analysis
    analyzer = PerformanceAnalyzer(portfolio)
    analyzer.calculate_metrics()
    analyzer.print_report()
    analyzer.print_positions()
    analyzer.print_trades(limit=15)

    # Export results
    analyzer.export_to_json('backtest_results.json')
    analyzer.export_trades_to_csv('backtest_trades.csv')

    return analyzer


def main():
    """Main menu for backtesting system"""
    print("\n" + "=" * 80)
    print("🇮🇳  INDIAN MARKET BACKTESTING SYSTEM  🇮🇳")
    print("     Crazy Trading Strategies Analyzer")
    print("=" * 80)

    print("\nSelect an option:")
    print("1. Run single strategy backtest (Quick)")
    print("2. Compare multiple strategies (Comprehensive)")
    print("3. Backtest with real Indian stocks (Requires yfinance)")
    print("4. Run custom backtest (Advanced)")
    print("5. Run all tests")

    try:
        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            run_single_strategy_backtest()

        elif choice == '2':
            run_multiple_strategies_comparison()

        elif choice == '3':
            run_real_stocks_backtest()

        elif choice == '4':
            run_custom_backtest()

        elif choice == '5':
            print("\n🔥 RUNNING ALL TESTS...")
            print("\n" + "=" * 80)
            print("TEST 1: Single Strategy")
            print("=" * 80)
            run_single_strategy_backtest()

            print("\n" + "=" * 80)
            print("TEST 2: Multiple Strategies Comparison")
            print("=" * 80)
            run_multiple_strategies_comparison()

            print("\n" + "=" * 80)
            print("TEST 3: Real Stocks Backtest")
            print("=" * 80)
            run_real_stocks_backtest()

        else:
            print("Invalid choice. Running default comparison...")
            run_multiple_strategies_comparison()

    except KeyboardInterrupt:
        print("\n\n⚠️  Backtest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n✅ Backtesting complete!")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
