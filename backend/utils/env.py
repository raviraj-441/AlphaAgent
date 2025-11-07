"""
Environment variable management utilities.
Handles subprocess env passing, .env loading, and consistent env access.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class EnvManager:
    """Unified environment variable management."""
    
    _loaded = False
    _env_cache: Dict[str, str] = {}
    
    @classmethod
    def load_env(cls, env_file: Optional[Path] = None, force: bool = False) -> None:
        """
        Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file (defaults to project root)
            force: Force reload even if already loaded
        """
        if cls._loaded and not force:
            logger.debug("Environment already loaded, skipping")
            return
        
        if env_file is None:
            # Find .env in project root
            project_root = Path(__file__).resolve().parent.parent.parent
            env_file = project_root / ".env"
        
        if not env_file.exists():
            logger.warning(f".env file not found at {env_file}")
            return
        
        load_dotenv(env_file, override=True)
        cls._loaded = True
        logger.info(f"Environment loaded from {env_file}")
    
    @classmethod
    def get(cls, key: str, default: str = "", required: bool = False) -> str:
        """
        Get environment variable with caching.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: If True, raise ValueError if not found
        
        Returns:
            Environment variable value
        
        Raises:
            ValueError: If required=True and key not found
        """
        if key not in cls._env_cache:
            value = os.getenv(key, default)
            if not value and required:
                raise ValueError(f"Required environment variable '{key}' not set")
            cls._env_cache[key] = value
        
        return cls._env_cache[key]
    
    @classmethod
    def get_all(cls) -> Dict[str, str]:
        """Get all environment variables as dict."""
        return os.environ.copy()
    
    @classmethod
    def get_subprocess_env(cls) -> Dict[str, str]:
        """
        Get environment dict for subprocess calls.
        Includes all current environment variables.
        
        Returns:
            Subprocess-safe environment dict
        """
        env = os.environ.copy()
        
        # Ensure critical keys are present
        critical_keys = ["GROQ_API_KEY", "TAVILY_API_KEY", "PYTHONUNBUFFERED"]
        for key in critical_keys:
            value = cls.get(key, "")
            if value:
                env[key] = value
        
        return env
    
    @classmethod
    def run_subprocess(
        cls,
        command: list,
        check: bool = True,
        capture_output: bool = False,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        Run subprocess with proper environment handling.
        
        Args:
            command: Command to run (list)
            check: Raise CalledProcessError on non-zero exit
            capture_output: Capture stdout/stderr
            **kwargs: Additional args for subprocess.run
        
        Returns:
            CompletedProcess result
        
        Raises:
            subprocess.CalledProcessError: If check=True and exit code != 0
        """
        env = cls.get_subprocess_env()
        
        logger.debug(f"Running subprocess: {' '.join(command)}")
        
        return subprocess.run(
            command,
            env=env,
            check=check,
            capture_output=capture_output,
            text=True,
            **kwargs
        )


# Module-level convenience functions
def load_env(env_file: Optional[Path] = None) -> None:
    """Load environment variables."""
    EnvManager.load_env(env_file)


def get_env(key: str, default: str = "", required: bool = False) -> str:
    """Get environment variable."""
    return EnvManager.get(key, default, required)


def get_subprocess_env() -> Dict[str, str]:
    """Get subprocess-safe environment dict."""
    return EnvManager.get_subprocess_env()


def run_subprocess(
    command: list,
    check: bool = True,
    capture_output: bool = False,
    **kwargs
) -> subprocess.CompletedProcess:
    """Run subprocess with proper environment."""
    return EnvManager.run_subprocess(command, check, capture_output, **kwargs)
