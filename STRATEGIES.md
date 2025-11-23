# 🚀 Complete Strategy Guide

## All 13 Crazy Trading Strategies

### 🔵 Trend Following Strategies (5)

#### 1. 💥 Momentum Explosion
- **Type**: Aggressive trend following
- **Indicators**: Fast/Slow EMA crossover + RSI
- **Entry**: Fast EMA > Slow EMA + RSI > 60
- **Exit**: Fast EMA < Slow EMA or RSI < 40
- **Best For**: Strong trending markets
- **Position Size**: 15% per trade

#### 2. 🔥 SuperTrend Follower
- **Type**: Multi-indicator confirmation
- **Indicators**: SMA (20,50), MACD, RSI
- **Entry**: All indicators align bullish
- **Exit**: Any indicator turns bearish
- **Best For**: High conviction trend entries
- **Position Size**: 20% per trade

#### 3. 🚁 Triple Momentum Rocket
- **Type**: Ultra-aggressive momentum
- **Indicators**: RSI + MACD + Rate of Change
- **Entry**: All three momentum indicators align
  - RSI: 60-80
  - ROC: > 5%
  - MACD: Bullish with positive histogram
- **Exit**: Any momentum indicator fails
- **Best For**: Explosive trending moves
- **Position Size**: 18% per trade

#### 4. 🏄 Trend Surfing Extreme
- **Type**: Trailing stop trend rider
- **Indicators**: SMA (20,50), RSI
- **Entry**: Strong uptrend + good momentum
- **Exit**: 3% trailing stop from highest price
- **Best For**: Riding long trends with protection
- **Position Size**: 17% per trade

#### 5. 🌈 MA Rainbow
- **Type**: Multi-timeframe moving average
- **Indicators**: 5 SMAs (5, 10, 20, 50, 100)
- **Entry**: All MAs aligned in perfect ascending order
- **Exit**: Any MA crosses another
- **Best For**: Very strong trending markets
- **Position Size**: 20% per trade

---

### 🟢 Mean Reversion Strategies (2)

#### 6. 🎯 Mean Reversion Madness
- **Type**: Extreme oversold/overbought
- **Indicators**: Bollinger Bands (20, 2.5 std), RSI
- **Entry**: Price touches lower band + RSI < 25
- **Exit**: Price touches upper band or RSI > 75
- **Best For**: Ranging/choppy markets
- **Position Size**: 12% per trade

#### 7. 🎣 Reversal Hunter
- **Type**: V-shaped reversal catcher
- **Indicators**: RSI + Candlestick patterns
- **Entry**: RSI < 20 + hammer/bullish engulfing
- **Exit**: 10% profit or RSI > 70
- **Best For**: Catching bottoms after sell-offs
- **Position Size**: 14% per trade

---

### 🟡 Breakout Strategies (3)

#### 8. ⚡ Volatility Breakout
- **Type**: ATR-based breakout
- **Indicators**: ATR, 20-day high/low
- **Entry**: Breaks above 20-day high
- **Exit**: Breaks below 20-day low or 2*ATR stop
- **Best For**: Volatile breakout moves
- **Position Size**: 10% per trade

#### 9. 🎯 Breakout Bandit
- **Type**: 52-week high breakouts
- **Indicators**: 252-day high, volume, consolidation
- **Entry**: Breaks 52-week high after consolidation + high volume
- **Exit**: Falls below 20-day low or 8% stop loss
- **Best For**: Major breakout moves after accumulation
- **Position Size**: 13% per trade

#### 10. 🎪 Bollinger Squeeze
- **Type**: Volatility compression
- **Indicators**: Bollinger Bands, bandwidth
- **Entry**: After squeeze detected, breaks above mid-band
- **Exit**: Price falls to lower band
- **Best For**: Low volatility expanding into trends
- **Position Size**: 15% per trade

---

### 🟠 Volume-Based Strategies (1)

#### 11. 📢 Volume Explosion
- **Type**: Volume spike momentum
- **Indicators**: Volume (20-day average)
- **Entry**: Volume > 2.5x average + bullish candle + 2%+ move
- **Exit**: Volume dries up or price reverses 3%
- **Best For**: News-driven momentum moves
- **Position Size**: 16% per trade

---

### 🔴 Gap & Swing Strategies (2)

#### 12. 🚀 Gap and Go
- **Type**: Morning gap momentum
- **Indicators**: Gap percentage, price action
- **Entry**: Gap up ≥ 2% + price continues higher
- **Exit**: Gap fills or 3% reversal
- **Best For**: Indian market opening gaps
- **Position Size**: 12% per trade

#### 13. ⚡ Swing Scalper
- **Type**: Quick swing trades
- **Indicators**: Fast EMAs (5, 10), RSI (7)
- **Entry**: EMA(5) > EMA(10) + RSI 50-70 + 1% momentum
- **Exit**: 3% profit target OR 1.5% stop loss OR EMA cross down
- **Best For**: Active swing trading, quick profits
- **Position Size**: 11% per trade

---

## Strategy Selection Guide

### 📈 For Trending Markets
Best: Momentum Explosion, SuperTrend Follower, Triple Momentum Rocket, MA Rainbow

### 📉 For Ranging Markets
Best: Mean Reversion Madness, Reversal Hunter, Bollinger Squeeze

### ⚡ For Volatile Markets
Best: Volatility Breakout, Volume Explosion, Swing Scalper

### 🎯 For Breakout Trading
Best: Breakout Bandit, Volatility Breakout, Bollinger Squeeze

### 🌅 For Indian Market Specifics
Best: Gap and Go (morning gaps), Volume Explosion (news-driven)

---

## Risk Levels

**Conservative** (Lower position sizes):
- Volatility Breakout (10%)
- Swing Scalper (11%)
- Mean Reversion Madness (12%)

**Moderate** (Medium position sizes):
- Breakout Bandit (13%)
- Reversal Hunter (14%)
- Momentum Explosion (15%)
- Volume Explosion (16%)

**Aggressive** (Higher position sizes):
- Trend Surfing Extreme (17%)
- Triple Momentum Rocket (18%)
- SuperTrend Follower (20%)
- MA Rainbow (20%)

---

## Quick Start Commands

```bash
# Test a specific strategy
python run_backtest.py
# Select option 1 for single strategy

# Compare all strategies
python run_backtest.py
# Select option 2 for comparison

# Showcase all 13 strategies
python showcase_strategies.py

# Quick test
python test_backtest.py
```

---

## Strategy Customization

All strategies can be customized with parameters:

```python
# Example: Aggressive Momentum Strategy
strategy = MomentumExplosionStrategy(
    fast_period=5,          # Faster entries
    slow_period=30,         # Shorter trend
    rsi_threshold=55,       # Earlier signals
    position_size_pct=0.25  # Larger positions
)

# Example: Conservative Mean Reversion
strategy = MeanReversionMadnessStrategy(
    bb_period=30,           # Smoother bands
    bb_std=3.0,             # Wider bands
    rsi_oversold=20,        # More extreme
    rsi_overbought=80,      # More extreme
    position_size_pct=0.08  # Smaller positions
)
```

---

## Performance Tips

1. **Combine Strategies**: Use multiple strategies for diversification
2. **Market Conditions**: Switch strategies based on market regime
3. **Position Sizing**: Adjust based on your risk tolerance
4. **Stop Losses**: Some strategies have built-in stops, add your own for others
5. **Commission Impact**: Higher frequency strategies pay more commission
6. **Backtesting Period**: Test across different market conditions (bull, bear, sideways)

---

**Remember**: Past performance doesn't guarantee future results. Always test thoroughly before live trading!
