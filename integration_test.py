"""
Integration tests for new utility modules: EnvManager, PathManager, and RecommendationEngine.
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.env import EnvManager
from backend.utils.paths import PathManager
from backend.utils.recommendations import PriceDataProvider, RecommendationFallback


class TestEnvManager:
    """Test suite for environment variable management."""
    
    def test_load_env(self):
        """Test loading environment variables from .env file."""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=test_value\n')
            f.write('GROQ_API_KEY=test_groq_key\n')
            env_file = f.name
        
        try:
            # Mock the env file path
            with patch.object(EnvManager, '_get_env_file_path', return_value=env_file):
                EnvManager.load_env()
                assert os.getenv('TEST_VAR') == 'test_value'
        finally:
            os.unlink(env_file)
            if 'TEST_VAR' in os.environ:
                del os.environ['TEST_VAR']
    
    def test_get_with_caching(self):
        """Test environment variable retrieval with caching."""
        os.environ['CACHE_TEST'] = 'cache_value'
        
        # First call
        value1 = EnvManager.get('CACHE_TEST')
        # Second call (from cache)
        value2 = EnvManager.get('CACHE_TEST')
        
        assert value1 == value2 == 'cache_value'
        
        # Cleanup
        del os.environ['CACHE_TEST']
    
    def test_get_subprocess_env(self):
        """Test generating environment dict for subprocess."""
        os.environ['TEST_KEY'] = 'test_value'
        
        env_dict = EnvManager.get_subprocess_env()
        
        assert isinstance(env_dict, dict)
        assert 'TEST_KEY' in env_dict
        assert 'PYTHONUNBUFFERED' in env_dict
        assert env_dict['PYTHONUNBUFFERED'] == '1'
        
        # Cleanup
        del os.environ['TEST_KEY']
    
    def test_run_subprocess(self):
        """Test subprocess execution with proper environment."""
        os.environ['TEST_ENV_VAR'] = 'subprocess_test'
        
        # Run simple Python command that echoes an env var
        result = EnvManager.run_subprocess(
            [sys.executable, '-c', 'import os; print(os.getenv("TEST_ENV_VAR"))'],
            capture_output=True
        )
        
        assert 'subprocess_test' in result.stdout
        
        # Cleanup
        del os.environ['TEST_ENV_VAR']


class TestPathManager:
    """Test suite for path management."""
    
    def test_get_project_root(self):
        """Test finding project root directory."""
        root = PathManager.get_project_root()
        
        assert root is not None
        assert root.exists()
        # Check for marker files
        assert (root / 'pyproject.toml').exists() or (root / '.git').exists()
    
    def test_get_data_dir(self):
        """Test getting data directory path."""
        data_dir = PathManager.get_data_dir()
        
        assert data_dir is not None
        assert isinstance(data_dir, Path)
        assert 'data' in str(data_dir)
    
    def test_get_test_portfolios_dir(self):
        """Test getting test portfolios directory."""
        portfolios_dir = PathManager.get_test_portfolios_dir()
        
        assert portfolios_dir is not None
        assert 'test_portfolios' in str(portfolios_dir)
    
    def test_get_tax_docs_dir(self):
        """Test getting tax documents directory."""
        tax_docs_dir = PathManager.get_tax_docs_dir()
        
        assert tax_docs_dir is not None
        assert 'income_tax_law_texts' in str(tax_docs_dir)
    
    def test_get_test_prices_dir(self):
        """Test getting test prices directory."""
        prices_dir = PathManager.get_test_prices_dir()
        
        assert prices_dir is not None
        assert 'test_prices' in str(prices_dir)
    
    def test_get_sample_portfolio(self):
        """Test getting sample portfolio path."""
        portfolio_path = PathManager.get_sample_portfolio()
        
        assert portfolio_path is not None
        assert 'sample_portfolio.csv' in str(portfolio_path)
    
    def test_ensure_dir_creates_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / 'test' / 'nested' / 'dir'
            
            PathManager.ensure_dir(test_dir)
            
            assert test_dir.exists()
            assert test_dir.is_dir()
    
    def test_paths_are_absolute(self):
        """Test that all paths returned are absolute."""
        paths_to_test = [
            PathManager.get_project_root(),
            PathManager.get_data_dir(),
            PathManager.get_test_portfolios_dir(),
            PathManager.get_tax_docs_dir(),
            PathManager.get_test_prices_dir(),
            PathManager.get_sample_portfolio(),
        ]
        
        for path in paths_to_test:
            assert path.is_absolute(), f"Path {path} is not absolute"


class TestPriceDataProvider:
    """Test suite for price data provider with fallback chain."""
    
    def test_get_historical_prices_with_cache(self):
        """Test retrieving cached historical prices."""
        provider = PriceDataProvider()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / 'TEST_prices.csv'
            cache_file.write_text('Date,Close\n2024-01-01,100.0\n2024-01-02,101.0\n')
            
            # Mock the cache directory
            with patch.object(PathManager, 'get_test_prices_dir', return_value=Path(tmpdir)):
                prices = provider.get_historical_prices('TEST')
                
                assert prices is not None
                assert not prices.empty
    
    def test_get_historical_prices_synthetic_fallback(self):
        """Test synthetic data generation as fallback."""
        provider = PriceDataProvider()
        
        # Just call with a valid symbol - will fallback to synthetic if yfinance unavailable
        prices = provider.get_historical_prices('TEST_SYMBOL')
        
        assert prices is not None, "Prices should not be None"
        assert not prices.empty, "Prices should not be empty"
        assert 'Adj Close' in prices.columns, "Should have Adj Close column"
    
    def test_synthetic_prices_are_deterministic(self):
        """Test that synthetic prices are deterministic for same symbol."""
        provider = PriceDataProvider()
        
        # Clear cache to ensure fresh generation
        provider._price_cache.clear()
        
        prices1 = provider.get_historical_prices('TEST_SYMBOL', use_cache=False)
        prices2 = provider.get_historical_prices('TEST_SYMBOL', use_cache=False)
        
        # Both should be non-empty
        assert prices1 is not None, "First call should return prices"
        assert prices2 is not None, "Second call should return prices"
        assert not prices1.empty, "First prices should not be empty"
        assert not prices2.empty, "Second prices should not be empty"
        
        # Values should be identical (deterministic)
        assert prices1['Adj Close'].iloc[0] == prices2['Adj Close'].iloc[0]

    
    def test_get_correlation(self):
        """Test correlation calculation between two symbols."""
        provider = PriceDataProvider()
        
        # Mock price data
        import pandas as pd
        with patch.object(provider, 'get_historical_prices') as mock_prices:
            # Create test price series
            prices1 = pd.Series([100, 101, 102, 101, 100], name='AAPL')
            prices2 = pd.Series([50, 51, 52, 51, 50], name='MSFT')
            
            mock_prices.side_effect = [prices1, prices2]
            
            correlation = provider.get_correlation('AAPL', 'MSFT')
            
            assert correlation is not None
            assert -1 <= correlation <= 1
    
    def test_get_correlation_handles_errors(self):
        """Test correlation calculation handles missing data gracefully."""
        provider = PriceDataProvider()
        
        # Mock to return None for both
        with patch.object(provider, 'get_historical_prices', return_value=None):
            correlation = provider.get_correlation('INVALID1', 'INVALID2')
            
            assert correlation == 0  # Default when data unavailable


class TestRecommendationFallback:
    """Test suite for recommendation fallback strategies."""
    
    def test_get_sector_alternatives(self):
        """Test getting sector alternative stocks."""
        fallback = RecommendationFallback()
        
        alternatives = fallback.get_sector_alternatives('AAPL')
        
        assert alternatives is not None
        assert isinstance(alternatives, list)
        assert len(alternatives) > 0
    
    def test_get_etf_alternatives(self):
        """Test getting ETF alternatives for a stock."""
        fallback = RecommendationFallback()
        
        etfs = fallback.get_etf_alternatives('AAPL', 'Technology')
        
        assert etfs is not None
        assert isinstance(etfs, list)
        assert len(etfs) > 0
    
    def test_fallback_for_unknown_stock(self):
        """Test fallback provides alternatives even for unknown stocks."""
        fallback = RecommendationFallback()
        
        alternatives = fallback.get_sector_alternatives('UNKNOWNSTOCK123')
        
        # Should still return alternatives (generic or sectoral)
        assert alternatives is not None


class TestIntegration:
    """Integration tests combining multiple utilities."""
    
    def test_env_paths_integration(self):
        """Test EnvManager and PathManager work together."""
        # Load environment
        EnvManager.load_env()
        
        # Get paths
        root = PathManager.get_project_root()
        data_dir = PathManager.get_data_dir()
        
        # Verify integration
        assert root.exists()
        assert str(data_dir).startswith(str(root))
    
    def test_recommendation_with_paths(self):
        """Test recommendation engine with path utilities."""
        # Get cache directory
        cache_dir = PathManager.get_test_prices_dir()
        
        # Ensure directory exists
        PathManager.ensure_dir(cache_dir)
        
        # Create provider
        provider = PriceDataProvider()
        
        # Should work without errors
        prices = provider.get_historical_prices('TEST')
        assert prices is not None
    
    def test_subprocess_execution_from_different_cwd(self):
        """Test subprocess inherits environment regardless of cwd."""
        os.environ['TEST_SUBPROCESS_VAR'] = 'test_value'
        
        # Run from different directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                result = EnvManager.run_subprocess(
                    [sys.executable, '-c', 
                     'import os; print(os.getenv("TEST_SUBPROCESS_VAR"))']
                )
                
                assert 'test_value' in result
            finally:
                os.chdir(original_cwd)
                del os.environ['TEST_SUBPROCESS_VAR']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
