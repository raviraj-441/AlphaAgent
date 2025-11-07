"""
Multi-source Market Data Fetcher with Intelligent Fallback

Provides market data with fallback chain:
1. Yahoo Finance (primary) - Fast, reliable
2. Alpha Vantage (fallback 1) - More reliable for rate limits
3. NSE India (fallback 2) - For Indian stocks
4. Local Cache (fallback 3) - Always available
5. Synthetic Data (final fallback) - For testing/availability
"""

import os
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """Market data fetcher with multi-source fallback and intelligent caching."""

    def __init__(self, cache_dir: str = "data/market_cache"):
        """Initialize fetcher with cache directory and API keys."""
        self.alpha_key = os.getenv("ALPHA_VANTAGE_KEY", "")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_backoff = 1  # seconds

    # ========== SOURCE 1: Yahoo Finance ==========
    def _from_yahoo(self, symbol: str, period: str = "1y") -> Optional[pd.Series]:
        """Fetch data from Yahoo Finance (primary source)."""
        try:
            import yfinance as yf
            
            logger.info(f"[Yahoo] Attempting fetch for {symbol}")
            df = yf.download(symbol, period=period, progress=False, threads=False)
            
            if df.empty:
                logger.warning(f"[Yahoo] Empty data for {symbol}")
                return None
            
            if "Adj Close" not in df.columns:
                logger.warning(f"[Yahoo] No Adj Close column for {symbol}")
                return None
            
            logger.info(f"[Yahoo] SUCCESS - {len(df)} rows for {symbol}")
            return df["Adj Close"]
            
        except Exception as e:
            logger.warning(f"[Yahoo] Error for {symbol}: {e}")
            return None

    # ========== SOURCE 2: Alpha Vantage ==========
    def _from_alpha_vantage(self, symbol: str) -> Optional[pd.Series]:
        """Fetch data from Alpha Vantage API (fallback 1)."""
        if not self.alpha_key:
            logger.debug("[AlphaVantage] API key not configured, skipping")
            return None
        
        try:
            logger.info(f"[AlphaVantage] Attempting fetch for {symbol}")
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol,
                "outputsize": "compact",
                "apikey": self.alpha_key,
            }
            
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            if "Error Message" in data or "Time Series (Daily)" not in data:
                logger.warning(f"[AlphaVantage] API error or no data for {symbol}")
                return None
            
            ts_data = data["Time Series (Daily)"]
            if not ts_data:
                logger.warning(f"[AlphaVantage] Empty time series for {symbol}")
                return None
            
            df = pd.DataFrame(ts_data).T.astype(float)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            
            logger.info(f"[AlphaVantage] SUCCESS - {len(df)} rows for {symbol}")
            return df["5. adjusted close"]
            
        except Exception as e:
            logger.warning(f"[AlphaVantage] Error for {symbol}: {e}")
            return None

    # ========== SOURCE 3: NSE India ==========
    def _from_nse(self, symbol: str) -> Optional[pd.Series]:
        """Fetch data from NSE India API (fallback 2 - for Indian stocks)."""
        try:
            logger.info(f"[NSE] Attempting fetch for {symbol}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json",
                "Referer": "https://www.nseindia.com/",
            }
            
            url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]"
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            if "data" not in data or not data["data"]:
                logger.warning(f"[NSE] No data for {symbol}")
                return None
            
            df = pd.DataFrame(data["data"])
            if "CH_TIMESTAMP" not in df.columns or "CH_CLOSING_PRICE" not in df.columns:
                logger.warning(f"[NSE] Missing expected columns for {symbol}")
                return None
            
            df["Date"] = pd.to_datetime(df["CH_TIMESTAMP"])
            df.set_index("Date", inplace=True)
            df.sort_index(inplace=True)
            
            # Convert closing price to float
            df["Adj Close"] = pd.to_numeric(df["CH_CLOSING_PRICE"], errors="coerce")
            
            logger.info(f"[NSE] SUCCESS - {len(df)} rows for {symbol}")
            return df["Adj Close"].dropna()
            
        except Exception as e:
            logger.warning(f"[NSE] Error for {symbol}: {e}")
            return None

    # ========== SOURCE 4: Local Cache ==========
    def _from_cache(self, symbol: str) -> Optional[pd.Series]:
        """Load data from local cache."""
        cache_file = self.cache_dir / f"{symbol}.csv"
        
        if not cache_file.exists():
            logger.debug(f"[Cache] No cache file for {symbol}")
            return None
        
        try:
            df = pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
            if "Adj Close" not in df.columns:
                logger.warning(f"[Cache] Missing Adj Close column for {symbol}")
                return None
            
            logger.info(f"[Cache] Loaded {len(df)} rows for {symbol}")
            return df["Adj Close"]
            
        except Exception as e:
            logger.warning(f"[Cache] Error reading cache for {symbol}: {e}")
            return None

    # ========== SOURCE 5: Synthetic Data ==========
    def _from_synthetic(self, symbol: str, days: int = 252) -> pd.Series:
        """Generate deterministic synthetic data (final fallback)."""
        logger.info(f"[Synthetic] Generating {days}-day data for {symbol}")
        
        # Deterministic seed based on symbol
        seed = sum(ord(c) for c in symbol)
        np.random.seed(seed)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic price movement
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        
        series = pd.Series(prices, index=dates, name="Adj Close")
        logger.info(f"[Synthetic] Generated {len(series)} price points for {symbol}")
        return series

    # ========== SAVE TO CACHE ==========
    def _save_cache(self, symbol: str, series: pd.Series) -> bool:
        """Save price series to local cache."""
        cache_file = self.cache_dir / f"{symbol}.csv"
        
        try:
            df = series.to_frame("Adj Close")
            df.to_csv(cache_file)
            logger.info(f"[Cache] Saved {len(series)} rows for {symbol}")
            return True
        except Exception as e:
            logger.warning(f"[Cache] Failed to save for {symbol}: {e}")
            return False

    # ========== PUBLIC API ==========
    def get_prices(
        self, symbol: str, period: str = "1y", use_cache: bool = True
    ) -> Optional[pd.Series]:
        """
        Fetch prices with intelligent fallback chain.
        
        Tries in order:
        1. Yahoo Finance
        2. Alpha Vantage
        3. NSE India
        4. Local Cache
        5. Synthetic Data
        
        Args:
            symbol: Stock symbol
            period: Time period for Yahoo Finance (e.g., '1y', '6mo')
            use_cache: Whether to use/save cache
        
        Returns:
            Pandas Series of adjusted close prices or None
        """
        logger.info(f"========== Fetching prices for {symbol} ==========")
        
        # Try each source in order
        sources = [
            ("Yahoo", lambda: self._from_yahoo(symbol, period)),
            ("AlphaVantage", lambda: self._from_alpha_vantage(symbol)),
            ("NSE", lambda: self._from_nse(symbol)),
            ("Cache", lambda: self._from_cache(symbol)),
            ("Synthetic", lambda: self._from_synthetic(symbol)),
        ]
        
        for source_name, fetch_func in sources:
            try:
                data = fetch_func()
                
                if data is not None and len(data) > 5:
                    logger.info(f"[SUCCESS] {source_name} provided {len(data)} rows for {symbol}")
                    
                    if use_cache and source_name != "Cache":
                        self._save_cache(symbol, data)
                    
                    return data
                
                time.sleep(0.5)  # Avoid rate limiting
                
            except Exception as e:
                logger.error(f"[{source_name}] Unexpected error: {e}")
                continue
        
        # Final fallback - synthetic
        logger.warning(f"All sources failed, using synthetic data for {symbol}")
        return self._from_synthetic(symbol)

    def get_correlation(
        self, symbol_a: str, symbol_b: str, period: str = "1y", min_overlap: int = 30
    ) -> Optional[float]:
        """
        Calculate correlation between two symbols.
        
        Args:
            symbol_a: First stock symbol
            symbol_b: Second stock symbol
            period: Time period
            min_overlap: Minimum overlapping data points required
        
        Returns:
            Correlation coefficient (-1 to 1) or None
        """
        try:
            logger.info(f"Calculating correlation: {symbol_a} vs {symbol_b}")
            
            prices_a = self.get_prices(symbol_a, period)
            prices_b = self.get_prices(symbol_b, period)
            
            if prices_a is None or prices_b is None:
                logger.warning("Could not fetch both price series for correlation")
                return None
            
            # Align dates
            df = pd.concat([prices_a, prices_b], axis=1).dropna()
            
            if len(df) < min_overlap:
                logger.warning(f"Insufficient overlap: {len(df)} < {min_overlap}")
                return None
            
            corr = df.corr().iloc[0, 1]
            logger.info(f"[Correlation] {symbol_a} vs {symbol_b} = {corr:.3f}")
            return float(corr)
            
        except Exception as e:
            logger.error(f"Correlation error: {e}")
            return None

    def get_stats(
        self, symbol: str, period: str = "1y"
    ) -> Optional[dict]:
        """Get price statistics (return, volatility, Sharpe ratio)."""
        try:
            prices = self.get_prices(symbol, period)
            
            if prices is None or len(prices) < 2:
                return None
            
            returns = prices.pct_change().dropna()
            
            stats = {
                "symbol": symbol,
                "days": len(prices),
                "current_price": float(prices.iloc[-1]),
                "start_price": float(prices.iloc[0]),
                "min_price": float(prices.min()),
                "max_price": float(prices.max()),
                "avg_return_daily": float(returns.mean()),
                "volatility": float(returns.std()),
                "total_return": float((prices.iloc[-1] / prices.iloc[0]) - 1),
                "sharpe_ratio": float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
            }
            
            logger.info(f"[Stats] {symbol}: Return={stats['total_return']:.2%}, Vol={stats['volatility']:.2%}")
            return stats
            
        except Exception as e:
            logger.error(f"Stats error for {symbol}: {e}")
            return None
