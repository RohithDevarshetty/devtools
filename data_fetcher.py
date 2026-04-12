"""
Data Fetcher for Indian Stock Market
Fetches data from NSE/BSE using yfinance and provides sample data generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class IndianMarketDataFetcher:
    """Fetcher for Indian stock market data"""

    NSE_SUFFIX = ".NS"  # National Stock Exchange
    BSE_SUFFIX = ".BO"  # Bombay Stock Exchange

    # Popular Nifty 50 stocks
    NIFTY_50_STOCKS = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR",
        "ICICIBANK", "KOTAKBANK", "SBIN", "BHARTIARTL", "BAJFINANCE",
        "ITC", "ASIANPAINT", "HCLTECH", "LT", "AXISBANK",
        "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "WIPRO",
        "NESTLEIND", "POWERGRID", "NTPC", "TECHM", "TATAMOTORS"
    ]

    @staticmethod
    def get_nse_symbol(ticker: str) -> str:
        """Convert ticker to NSE format"""
        if not ticker.endswith(IndianMarketDataFetcher.NSE_SUFFIX):
            return f"{ticker}{IndianMarketDataFetcher.NSE_SUFFIX}"
        return ticker

    @staticmethod
    def fetch_data(ticker: str, start_date: str, end_date: str, exchange: str = "NSE") -> pd.DataFrame:
        """
        Fetch historical data for Indian stock

        Args:
            ticker: Stock ticker (e.g., "RELIANCE")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            exchange: "NSE" or "BSE"

        Returns:
            DataFrame with OHLCV data
        """
        try:
            import yfinance as yf

            suffix = IndianMarketDataFetcher.NSE_SUFFIX if exchange == "NSE" else IndianMarketDataFetcher.BSE_SUFFIX
            symbol = f"{ticker}{suffix}"

            df = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if df.empty:
                raise ValueError(f"No data found for {symbol}")

            # Standardize column names
            df.columns = [col.lower() for col in df.columns]
            df.index.name = 'date'

            return df

        except ImportError:
            print("Warning: yfinance not installed. Use 'pip install yfinance' to fetch real data.")
            print("Generating sample data instead...")
            return IndianMarketDataFetcher.generate_sample_data(ticker, start_date, end_date)

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            print("Generating sample data instead...")
            return IndianMarketDataFetcher.generate_sample_data(ticker, start_date, end_date)

    @staticmethod
    def generate_sample_data(ticker: str, start_date: str, end_date: str,
                            initial_price: float = 1000.0,
                            volatility: float = 0.02,
                            trend: float = 0.0001) -> pd.DataFrame:
        """
        Generate realistic sample OHLCV data

        Args:
            ticker: Stock ticker
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_price: Starting price
            volatility: Daily volatility (default 2%)
            trend: Daily trend (default 0.01%)

        Returns:
            DataFrame with OHLCV data
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # Generate business days (Indian market is open Mon-Fri)
        dates = pd.bdate_range(start=start, end=end)

        np.random.seed(hash(ticker) % 2**32)  # Consistent data for same ticker

        num_days = len(dates)
        returns = np.random.normal(trend, volatility, num_days)

        # Generate close prices with trend
        close_prices = initial_price * np.exp(np.cumsum(returns))

        # Generate realistic OHLC
        data = []
        for i, (date, close) in enumerate(zip(dates, close_prices)):
            # Add intraday volatility
            intraday_range = close * np.random.uniform(0.005, 0.025)

            open_price = close * (1 + np.random.uniform(-0.01, 0.01))
            high = max(open_price, close) + np.random.uniform(0, intraday_range)
            low = min(open_price, close) - np.random.uniform(0, intraday_range)

            # Generate volume (higher on volatile days)
            base_volume = 1000000
            volume_factor = abs(returns[i]) * 50
            volume = int(base_volume * (1 + volume_factor) * np.random.uniform(0.8, 1.2))

            data.append({
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })

        df = pd.DataFrame(data, index=dates)
        df.index.name = 'date'

        return df

    @staticmethod
    def fetch_multiple_stocks(tickers: List[str], start_date: str, end_date: str,
                              exchange: str = "NSE") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks

        Args:
            tickers: List of stock tickers
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            exchange: "NSE" or "BSE"

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        data = {}

        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            df = IndianMarketDataFetcher.fetch_data(ticker, start_date, end_date, exchange)

            if df is not None and not df.empty:
                data[ticker] = df
                print(f"  ✓ {ticker}: {len(df)} days of data")
            else:
                print(f"  ✗ {ticker}: Failed to fetch data")

        return data

    @staticmethod
    def get_nifty_50_sample(n_stocks: int = 10, start_date: str = None,
                           end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Get sample data for random Nifty 50 stocks

        Args:
            n_stocks: Number of stocks to fetch (default 10)
            start_date: Start date (defaults to 2 years ago)
            end_date: End date (defaults to today)

        Returns:
            Dictionary mapping ticker to DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Select random stocks
        selected = np.random.choice(
            IndianMarketDataFetcher.NIFTY_50_STOCKS,
            size=min(n_stocks, len(IndianMarketDataFetcher.NIFTY_50_STOCKS)),
            replace=False
        )

        return IndianMarketDataFetcher.fetch_multiple_stocks(
            selected.tolist(),
            start_date,
            end_date
        )


class DataGenerator:
    """Generate synthetic market scenarios for testing"""

    @staticmethod
    def trending_market(ticker: str, start_date: str, end_date: str,
                       trend_direction: str = "up") -> pd.DataFrame:
        """Generate trending market data"""
        trend = 0.0005 if trend_direction == "up" else -0.0005
        return IndianMarketDataFetcher.generate_sample_data(
            ticker, start_date, end_date,
            initial_price=1000.0,
            volatility=0.015,
            trend=trend
        )

    @staticmethod
    def choppy_market(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate choppy/sideways market data"""
        return IndianMarketDataFetcher.generate_sample_data(
            ticker, start_date, end_date,
            initial_price=1000.0,
            volatility=0.02,
            trend=0.0
        )

    @staticmethod
    def volatile_market(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate highly volatile market data"""
        return IndianMarketDataFetcher.generate_sample_data(
            ticker, start_date, end_date,
            initial_price=1000.0,
            volatility=0.04,
            trend=0.0001
        )

    @staticmethod
    def mixed_market_scenarios(n_stocks: int = 5, start_date: str = None,
                              end_date: str = None) -> Dict[str, pd.DataFrame]:
        """Generate mixed market scenarios"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        scenarios = {
            'UPTREND_STOCK': DataGenerator.trending_market('UPTREND', start_date, end_date, 'up'),
            'DOWNTREND_STOCK': DataGenerator.trending_market('DOWNTREND', start_date, end_date, 'down'),
            'CHOPPY_STOCK': DataGenerator.choppy_market('CHOPPY', start_date, end_date),
            'VOLATILE_STOCK': DataGenerator.volatile_market('VOLATILE', start_date, end_date),
        }

        # Add some random stocks
        for i in range(n_stocks - 4):
            scenarios[f'RANDOM_{i}'] = IndianMarketDataFetcher.generate_sample_data(
                f'RANDOM_{i}', start_date, end_date,
                initial_price=np.random.uniform(500, 2000),
                volatility=np.random.uniform(0.015, 0.035)
            )

        return scenarios
