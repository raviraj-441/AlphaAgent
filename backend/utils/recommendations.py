"""
Enhanced recommendation engine with fallback strategies.
Combines correlation, semantic similarity, and fallback data sources.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from pathlib import Path
import csv
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PriceDataProvider:
    """Manages historical price data with caching and fallback strategies."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize price data provider.
        
        Args:
            cache_dir: Directory to cache price data
        """
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "test_prices"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._price_cache = {}
    
    def get_historical_prices(
        self,
        symbol: str,
        period_days: int = 365,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Get historical prices for a symbol.
        
        Fallback chain:
        1. Try yfinance (real data)
        2. Try cached CSV in test_prices/
        3. Generate synthetic data for testing
        
        Args:
            symbol: Stock symbol
            period_days: Number of days of history
            use_cache: Use cached data if available
        
        Returns:
            DataFrame with columns: Date, Adj Close, Pct_Change
        """
        if use_cache and symbol in self._price_cache:
            return self._price_cache[symbol]
        
        # Try cache file first
        cache_file = self.cache_dir / f"{symbol.upper()}_prices.csv"
        if cache_file.exists():
            try:
                df = pd.read_csv(cache_file, parse_dates=["Date"])
                df.set_index("Date", inplace=True)
                df["Pct_Change"] = df["Adj Close"].pct_change()
                self._price_cache[symbol] = df
                logger.debug(f"Loaded {symbol} prices from cache: {cache_file}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load cache for {symbol}: {e}")
        
        # Try yfinance (requires internet)
        try:
            import yfinance as yf
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            df = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            if df.empty:
                logger.warning(f"No data from yfinance for {symbol}, falling back to synthetic")
                # Don't return None - fall through to synthetic data
            else:
                df["Pct_Change"] = df["Adj Close"].pct_change()
                self._price_cache[symbol] = df
                
                # Cache to file
                self._save_to_cache(symbol, df)
                logger.debug(f"Fetched {symbol} prices from yfinance")
                return df
        
        except ImportError:
            logger.debug("yfinance not available, falling back to synthetic data")
        except Exception as e:
            logger.warning(f"yfinance fetch failed for {symbol}: {e}")
        
        # Generate synthetic data for testing
        df = self._generate_synthetic_prices(symbol, period_days)
        self._price_cache[symbol] = df
        logger.info(f"Generated synthetic prices for {symbol}")
        return df
    
    def _save_to_cache(self, symbol: str, df: pd.DataFrame) -> None:
        """Save prices to cache CSV."""
        try:
            cache_file = self.cache_dir / f"{symbol.upper()}_prices.csv"
            df_to_save = df.reset_index()
            df_to_save.to_csv(cache_file, index=False)
            logger.debug(f"Cached {symbol} prices to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache {symbol}: {e}")
    
    def _generate_synthetic_prices(
        self,
        symbol: str,
        period_days: int = 365
    ) -> pd.DataFrame:
        """
        Generate synthetic price data for testing.
        Uses simple geometric random walk.
        """
        dates = pd.date_range(end=datetime.now(), periods=period_days, freq='D')
        
        # Base price varies by symbol for realism
        base_prices = {
            "RELIANCE": 2500,
            "TCS": 3500,
            "INFY": 2800,
            "HDFC": 1800,
            "AXISBANK": 700,
            "SBIN": 400,
            "LT": 1600,
        }
        
        base = base_prices.get(symbol.upper(), 1000)
        
        # Random walk
        np.random.seed(hash(symbol) % 2**32)  # Deterministic for tests
        returns = np.random.normal(0.0003, 0.02, period_days)  # ~7% annual volatility
        prices = base * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            "Date": dates,
            "Adj Close": prices
        })
        df["Pct_Change"] = df["Adj Close"].pct_change()
        df.set_index("Date", inplace=True)
        
        return df
    
    def get_correlation(self, sym_a: str, sym_b: str, period_days: int = 252) -> Optional[float]:
        """
        Calculate correlation between two symbols.
        
        Args:
            sym_a: First symbol
            sym_b: Second symbol
            period_days: Period for correlation (default 252 = 1 trading year)
        
        Returns:
            Correlation coefficient or None if data unavailable
        """
        try:
            df_a = self.get_historical_prices(sym_a, period_days)
            df_b = self.get_historical_prices(sym_b, period_days)
            
            if df_a is None or df_b is None or df_a.empty or df_b.empty:
                return None
            
            # Align dates
            common_dates = df_a.index.intersection(df_b.index)
            if len(common_dates) < 20:  # Need minimum data points
                return None
            
            returns_a = df_a.loc[common_dates, "Pct_Change"].dropna()
            returns_b = df_b.loc[common_dates, "Pct_Change"].dropna()
            
            if returns_a.empty or returns_b.empty:
                return None
            
            correlation = returns_a.corr(returns_b)
            return float(correlation) if not np.isnan(correlation) else None
        
        except Exception as e:
            logger.warning(f"Correlation calculation failed ({sym_a}, {sym_b}): {e}")
            return None


class RecommendationFallback:
    """Fallback strategies for when correlation/similarity is low."""
    
    # Predefined similar sectors and alternatives
    SECTOR_ALTERNATIVES = {
        "RELIANCE": ["HDFC", "TCS", "INFY"],  # Financial/IT peers
        "TCS": ["INFY", "LT", "WIPRO"],
        "INFY": ["TCS", "HCL", "TECH"],
        "HDFC": ["ICICI", "AXIS", "KOTAK"],
        "AXISBANK": ["ICICI", "HDFC", "KOTAK"],
        "SBIN": ["PNB", "IDBI", "BOI"],
        "LT": ["BHEL", "NTPC", "POWER"],
    }
    
    # ETF/Index alternatives
    ETFS = [
        {"symbol": "NIFTY50", "description": "Nifty 50 Index ETF"},
        {"symbol": "MIDCAP", "description": "Midcap ETF"},
        {"symbol": "SENSEX", "description": "BSE Sensex ETF"},
    ]
    
    @classmethod
    def get_sector_alternatives(cls, symbol: str, count: int = 3) -> List[str]:
        """Get sector-based alternatives."""
        return cls.SECTOR_ALTERNATIVES.get(symbol.upper(), [])[:count]
    
    @classmethod
    def get_etf_alternatives(cls) -> List[dict]:
        """Get ETF alternatives for diversification."""
        return cls.ETFS


def calculate_similarity_score(
    correlation: Optional[float],
    semantic_similarity: Optional[float],
    corr_threshold: float = 0.85,
    semantic_threshold: float = 0.75
) -> Tuple[float, str]:
    """
    Calculate combined similarity score with fallback logic.
    
    Args:
        correlation: Price correlation (-1 to 1)
        semantic_similarity: Semantic similarity (0 to 1)
        corr_threshold: Minimum correlation threshold
        semantic_threshold: Minimum semantic similarity threshold
    
    Returns:
        Tuple of (score, recommendation_status)
    """
    score = 0.0
    status = "rejected"
    
    # Correlation-based (strong preference)
    if correlation is not None and correlation >= corr_threshold:
        score = 0.7 + (0.2 * ((correlation + 1) / 2))  # Normalize to 0-1
        status = "high_correlation"
    
    # Semantic similarity as fallback
    elif semantic_similarity is not None and semantic_similarity >= semantic_threshold:
        score = 0.6 + (0.15 * semantic_similarity)
        status = "semantic_match"
    
    # Mixed: some correlation or similarity
    elif correlation is not None and correlation > 0.6:
        score = 0.4 + (0.15 * ((correlation + 1) / 2))
        status = "moderate_correlation"
    
    elif semantic_similarity is not None and semantic_similarity > 0.5:
        score = 0.4 + (0.1 * semantic_similarity)
        status = "weak_semantic"
    
    else:
        score = 0.0
        status = "no_match"
    
    return score, status
