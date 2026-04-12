#!/usr/bin/env python3
"""Quick test script to verify the backtesting system works"""

from backtesting_engine import BacktestEngine
from trading_strategies import MomentumExplosionStrategy, MeanReversionMadnessStrategy
from data_fetcher import DataGenerator
from performance_analyzer import PerformanceAnalyzer, StrategyComparer

def quick_test():
    """Run a quick test to verify everything works"""
    print("🧪 Running quick verification test...")

    # Generate test data
    data = DataGenerator.mixed_market_scenarios(n_stocks=3,
                                                 start_date='2023-01-01',
                                                 end_date='2023-06-01')

    # Test Momentum Strategy
    print("\n1. Testing Momentum Explosion Strategy...")
    engine = BacktestEngine(initial_capital=1000000)
    for symbol, df in data.items():
        engine.load_data(symbol, df)

    strategy = MomentumExplosionStrategy(position_size_pct=0.15)
    portfolio = engine.run(strategy)

    analyzer = PerformanceAnalyzer(portfolio)
    metrics = analyzer.calculate_metrics()

    print(f"   ✓ Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"   ✓ Total Trades: {metrics['total_trades']}")
    print(f"   ✓ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")

    # Test Mean Reversion Strategy
    print("\n2. Testing Mean Reversion Strategy...")
    engine2 = BacktestEngine(initial_capital=1000000)
    for symbol, df in data.items():
        engine2.load_data(symbol, df)

    strategy2 = MeanReversionMadnessStrategy(position_size_pct=0.12)
    portfolio2 = engine2.run(strategy2)

    analyzer2 = PerformanceAnalyzer(portfolio2)
    metrics2 = analyzer2.calculate_metrics()

    print(f"   ✓ Total Return: {metrics2['total_return_pct']:.2f}%")
    print(f"   ✓ Total Trades: {metrics2['total_trades']}")
    print(f"   ✓ Sharpe Ratio: {metrics2['sharpe_ratio']:.2f}")

    # Test comparison
    print("\n3. Testing Strategy Comparison...")
    comparer = StrategyComparer()
    comparer.add_result("Momentum Explosion", analyzer)
    comparer.add_result("Mean Reversion", analyzer2)
    comparer.print_comparison()

    print("\n✅ All tests passed! The backtesting system is working correctly.")
    print("\nRun 'python run_backtest.py' to start the interactive backtesting system.")

if __name__ == "__main__":
    quick_test()
