"""
Robust path management utilities.
Provides absolute paths for all resources regardless of working directory.
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PathManager:
    """Centralized path management for the project."""
    
    # Cache for paths
    _paths_cache: dict = {}
    
    @classmethod
    def get_project_root(cls) -> Path:
        """
        Get absolute project root path.
        Works from any working directory.
        
        Returns:
            Absolute path to project root
        """
        if "project_root" not in cls._paths_cache:
            # Find marker file (pyproject.toml, .git, or this file's parent.parent)
            current = Path(__file__).resolve()
            for parent in [current.parent.parent.parent, *current.parents]:
                if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                    cls._paths_cache["project_root"] = parent
                    break
            else:
                # Fallback: assume 3 levels up from this file
                cls._paths_cache["project_root"] = current.parent.parent.parent
        
        return cls._paths_cache["project_root"]
    
    @classmethod
    def get_data_dir(cls) -> Path:
        """Get absolute path to data directory."""
        if "data_dir" not in cls._paths_cache:
            path = cls.get_project_root() / "data"
            path.mkdir(parents=True, exist_ok=True)
            cls._paths_cache["data_dir"] = path
        return cls._paths_cache["data_dir"]
    
    @classmethod
    def get_test_portfolios_dir(cls) -> Path:
        """Get absolute path to test portfolios directory."""
        if "test_portfolios_dir" not in cls._paths_cache:
            path = cls.get_data_dir() / "test_portfolios"
            path.mkdir(parents=True, exist_ok=True)
            cls._paths_cache["test_portfolios_dir"] = path
        return cls._paths_cache["test_portfolios_dir"]
    
    @classmethod
    def get_tax_docs_dir(cls) -> Path:
        """Get absolute path to tax documents directory."""
        if "tax_docs_dir" not in cls._paths_cache:
            path = cls.get_data_dir() / "income_tax_law_texts"
            path.mkdir(parents=True, exist_ok=True)
            cls._paths_cache["tax_docs_dir"] = path
        return cls._paths_cache["tax_docs_dir"]
    
    @classmethod
    def get_test_prices_dir(cls) -> Path:
        """Get absolute path to test prices directory (historical data cache)."""
        if "test_prices_dir" not in cls._paths_cache:
            path = cls.get_data_dir() / "test_prices"
            path.mkdir(parents=True, exist_ok=True)
            cls._paths_cache["test_prices_dir"] = path
        return cls._paths_cache["test_prices_dir"]
    
    @classmethod
    def get_file(cls, relative_path: str) -> Path:
        """
        Get absolute path for a file given relative path from project root.
        
        Args:
            relative_path: Path relative to project root (e.g., "data/test_portfolios/sample.csv")
        
        Returns:
            Absolute Path object
        
        Raises:
            FileNotFoundError: If file doesn't exist (optional warning)
        """
        path = cls.get_project_root() / relative_path
        
        if not path.exists():
            logger.warning(f"File not found: {path}")
        
        return path
    
    @classmethod
    def get_sample_portfolio(cls, name: str = "sample_portfolio.csv") -> Path:
        """
        Get absolute path to sample portfolio file.
        
        Args:
            name: Filename (default: sample_portfolio.csv)
        
        Returns:
            Absolute path to portfolio file
        """
        path = cls.get_test_portfolios_dir() / name
        
        if not path.exists():
            raise FileNotFoundError(f"Portfolio file not found: {path}")
        
        return path
    
    @classmethod
    def get_tax_doc(cls, name: str) -> Path:
        """
        Get absolute path to tax document file.
        
        Args:
            name: Filename
        
        Returns:
            Absolute path to tax document
        """
        path = cls.get_tax_docs_dir() / name
        
        if not path.exists():
            raise FileNotFoundError(f"Tax document not found: {path}")
        
        return path
    
    @classmethod
    def get_test_price_cache(cls, symbol: str) -> Path:
        """
        Get absolute path to test price cache for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
        
        Returns:
            Absolute path to price CSV (may not exist yet)
        """
        return cls.get_test_prices_dir() / f"{symbol.upper()}_prices.csv"
    
    @classmethod
    def ensure_dir(cls, path: Path) -> Path:
        """Ensure directory exists, create if needed."""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the paths cache (useful for testing)."""
        cls._paths_cache.clear()


# Module-level convenience functions
def get_project_root() -> Path:
    """Get absolute project root."""
    return PathManager.get_project_root()


def get_data_dir() -> Path:
    """Get absolute data directory."""
    return PathManager.get_data_dir()


def get_test_portfolios_dir() -> Path:
    """Get absolute test portfolios directory."""
    return PathManager.get_test_portfolios_dir()


def get_tax_docs_dir() -> Path:
    """Get absolute tax documents directory."""
    return PathManager.get_tax_docs_dir()


def get_test_prices_dir() -> Path:
    """Get absolute test prices directory."""
    return PathManager.get_test_prices_dir()


def get_sample_portfolio(name: str = "sample_portfolio.csv") -> Path:
    """Get absolute path to sample portfolio."""
    return PathManager.get_sample_portfolio(name)


def get_file(relative_path: str) -> Path:
    """Get absolute path for file from project root."""
    return PathManager.get_file(relative_path)
