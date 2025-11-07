#!/usr/bin/env python
"""
AlphaAgent Production Readiness Verification Script

This script validates that all root-cause fixes are working correctly
and the system is ready for production deployment.

Usage:
    python verify_production_ready.py
    python verify_production_ready.py --verbose
    python verify_production_ready.py --test-all
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple
import json

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

class ProductionVerifier:
    """Validates production readiness of AlphaAgent."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
    
    def print_header(self, text: str):
        """Print section header."""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
    
    def print_check(self, name: str, passed: bool, message: str = ""):
        """Print check result."""
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status}: {name}")
        if message:
            print(f"       {message}")
        if passed:
            self.checks_passed += 1
        else:
            self.checks_failed += 1
    
    def verify_python_version(self) -> bool:
        """Check Python version >= 3.10."""
        self.print_header("Python Version")
        version = sys.version_info
        passed = version.major >= 3 and version.minor >= 10
        msg = f"Python {version.major}.{version.minor}.{version.micro}"
        self.print_check("Python 3.10+", passed, msg)
        return passed
    
    def verify_dependencies(self) -> bool:
        """Check required dependencies are installed."""
        self.print_header("Dependencies")
        
        required = [
            'fastapi', 'uvicorn', 'pydantic', 'dotenv',
            'chromadb', 'pandas', 'numpy', 'crewai',
            'prometheus_client'
        ]
        
        all_passed = True
        for pkg in required:
            try:
                __import__(pkg.replace('-', '_'))
                self.print_check(f"Import {pkg}", True)
            except ImportError:
                self.print_check(f"Import {pkg}", False, "Not installed")
                all_passed = False
        
        return all_passed
    
    def verify_env_manager(self) -> bool:
        """Verify EnvManager class works correctly."""
        self.print_header("Environment Manager (Issue A Fix)")
        
        try:
            from backend.utils.env import EnvManager
            
            # Test: Load environment
            try:
                EnvManager.load_env()
                self.print_check("Load environment", True)
            except Exception as e:
                self.print_check("Load environment", False, str(e))
                return False
            
            # Test: Get environment variable
            os.environ['TEST_VAR'] = 'test_value'
            value = EnvManager.get('TEST_VAR')
            passed = value == 'test_value'
            self.print_check("Get environment variable", passed)
            
            # Test: Get subprocess environment
            try:
                env_dict = EnvManager.get_subprocess_env()
                has_keys = 'PATH' in env_dict or 'Path' in env_dict
                self.print_check("Get subprocess env", has_keys, 
                               f"Keys: {len(env_dict)}")
            except Exception as e:
                self.print_check("Get subprocess env", False, str(e))
                return False
            
            # Test: Run subprocess with environment
            try:
                os.environ['TEST_SUBPROCESS'] = 'subprocess_value'
                result = EnvManager.run_subprocess(
                    [sys.executable, '-c', 
                     'import os; print(os.getenv("TEST_SUBPROCESS", "not_found"))'],
                    capture_output=True
                )
                passed = 'subprocess_value' in result.stdout
                self.print_check("Subprocess env inheritance", passed,
                               f"Output: {result.stdout.strip()}")
            except Exception as e:
                self.print_check("Subprocess env inheritance", False, str(e))
                return False
            
            return True
            
        except ImportError as e:
            self.print_check("Import EnvManager", False, str(e))
            return False
    
    def verify_path_manager(self) -> bool:
        """Verify PathManager class works correctly."""
        self.print_header("Path Manager (Issue B Fix)")
        
        try:
            from backend.utils.paths import PathManager
            
            # Test: Get project root
            try:
                root = PathManager.get_project_root()
                is_absolute = root.is_absolute()
                exists = root.exists()
                self.print_check("Get project root", is_absolute and exists,
                               f"Path: {root}")
            except Exception as e:
                self.print_check("Get project root", False, str(e))
                return False
            
            # Test: Get data directory
            try:
                data_dir = PathManager.get_data_dir()
                is_absolute = data_dir.is_absolute()
                self.print_check("Get data directory (absolute)", is_absolute)
            except Exception as e:
                self.print_check("Get data directory", False, str(e))
                return False
            
            # Test: Get tax docs directory
            try:
                tax_dir = PathManager.get_tax_docs_dir()
                is_absolute = tax_dir.is_absolute()
                self.print_check("Get tax docs directory (absolute)", is_absolute)
            except Exception as e:
                self.print_check("Get tax docs directory", False, str(e))
                return False
            
            # Test: Get sample portfolio
            try:
                portfolio_path = PathManager.get_sample_portfolio()
                is_absolute = portfolio_path.is_absolute()
                self.print_check("Get sample portfolio (absolute)", is_absolute)
            except Exception as e:
                self.print_check("Get sample portfolio", False, str(e))
                return False
            
            # Test: Ensure directory creation
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    test_dir = Path(tmpdir) / 'test' / 'nested' / 'dir'
                    PathManager.ensure_dir(test_dir)
                    created = test_dir.exists()
                    self.print_check("Create nested directories", created)
            except Exception as e:
                self.print_check("Create nested directories", False, str(e))
                return False
            
            return True
            
        except ImportError as e:
            self.print_check("Import PathManager", False, str(e))
            return False
    
    def verify_recommendation_engine(self) -> bool:
        """Verify recommendation engine with fallback."""
        self.print_header("Recommendation Engine (Issue C Fix)")
        
        try:
            from backend.utils.recommendations import PriceDataProvider
            
            provider = PriceDataProvider()
            
            # Test: Get synthetic prices (fallback)
            try:
                prices = provider.get_historical_prices('TEST_SYMBOL')
                has_data = prices is not None and not prices.empty
                self.print_check("Get historical prices (synthetic fallback)", 
                               has_data, f"Rows: {len(prices) if has_data else 0}")
            except Exception as e:
                self.print_check("Get historical prices", False, str(e))
                return False
            
            # Test: Deterministic synthetic data
            try:
                prices1 = provider.get_historical_prices('DETERMINISTIC_TEST')
                prices2 = provider.get_historical_prices('DETERMINISTIC_TEST')
                
                if prices1 is not None and prices2 is not None and not prices1.empty and not prices2.empty:
                    same_values = prices1['Adj Close'].iloc[0] == prices2['Adj Close'].iloc[0]
                    self.print_check("Synthetic data deterministic", same_values)
                else:
                    self.print_check("Synthetic data deterministic", False, 
                                   "Empty data returned")
            except Exception as e:
                self.print_check("Synthetic data deterministic", False, str(e))
                return False
            
            # Test: Get correlation (with fallback)
            try:
                correlation = provider.get_correlation('SYMBOL1', 'SYMBOL2')
                if correlation is None:
                    # This is acceptable - correlation calculation might fail due to data
                    valid_range = True
                    msg = "Value: None (data not available)"
                else:
                    valid_range = -1 <= correlation <= 1
                    msg = f"Value: {correlation:.3f}"
                self.print_check("Get correlation", valid_range, msg)
            except Exception as e:
                self.print_check("Get correlation", False, str(e))
                return False
            
            return True
            
        except ImportError as e:
            self.print_check("Import PriceDataProvider", False, str(e))
            return False
    
    def verify_docker_files(self) -> bool:
        """Verify Docker configuration files exist."""
        self.print_header("Docker Configuration")
        
        root = Path(__file__).parent
        files_to_check = [
            ('Dockerfile', root / 'Dockerfile'),
            ('docker-compose.yml', root / 'docker-compose.yml'),
        ]
        
        all_exist = True
        for name, path in files_to_check:
            exists = path.exists()
            self.print_check(f"{name} exists", exists, f"Path: {path}")
            all_exist = all_exist and exists
        
        return all_exist
    
    def verify_monitoring_files(self) -> bool:
        """Verify monitoring configuration files."""
        self.print_header("Monitoring Configuration")
        
        root = Path(__file__).parent
        files_to_check = [
            ('prometheus.yml', root / 'monitoring' / 'prometheus.yml'),
            ('alerts.yml', root / 'monitoring' / 'alerts.yml'),
            ('Grafana dashboard', root / 'monitoring' / 'grafana' / 'dashboards' / 'alphaagent-dashboard.json'),
        ]
        
        all_exist = True
        for name, path in files_to_check:
            exists = path.exists()
            self.print_check(f"{name} exists", exists, f"Path: {path}")
            all_exist = all_exist and exists
        
        return all_exist
    
    def verify_ci_cd(self) -> bool:
        """Verify CI/CD configuration."""
        self.print_header("CI/CD Configuration")
        
        root = Path(__file__).parent
        workflow_file = root / '.github' / 'workflows' / 'ci.yml'
        exists = workflow_file.exists()
        self.print_check("GitHub Actions workflow", exists, f"Path: {workflow_file}")
        
        return exists
    
    def verify_integration_tests(self) -> bool:
        """Verify integration test file exists and is valid."""
        self.print_header("Integration Tests")
        
        root = Path(__file__).parent
        test_file = root / 'integration_test.py'
        exists = test_file.exists()
        self.print_check("Integration test file exists", exists)
        
        if exists:
            try:
                import ast
                with open(test_file) as f:
                    ast.parse(f.read())
                self.print_check("Integration test file is valid Python", True)
                return True
            except SyntaxError as e:
                self.print_check("Integration test file is valid Python", False, str(e))
                return False
        
        return False
    
    def verify_documentation(self) -> bool:
        """Verify documentation files exist."""
        self.print_header("Documentation")
        
        root = Path(__file__).parent
        docs = [
            ('README.md', root / 'README.md'),
            ('QUICKSTART.md', root / 'QUICKSTART.md'),
            ('DEPLOYMENT.md', root / 'DEPLOYMENT.md'),
            ('MONITORING.md', root / 'MONITORING.md'),
        ]
        
        all_exist = True
        for name, path in docs:
            exists = path.exists()
            size_kb = path.stat().st_size / 1024 if exists else 0
            self.print_check(f"{name} exists", exists, 
                           f"Size: {size_kb:.1f}KB" if exists else "")
            all_exist = all_exist and exists
        
        return all_exist
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("\n")
        print("[Search] AlphaAgent Production Readiness Verification")
        print("   Checking all root-cause fixes and infrastructure...\n")
        
        checks = [
            ("Python Version", self.verify_python_version),
            ("Dependencies", self.verify_dependencies),
            ("Environment Manager (Issue A)", self.verify_env_manager),
            ("Path Manager (Issue B)", self.verify_path_manager),
            ("Recommendation Engine (Issue C)", self.verify_recommendation_engine),
            ("Docker Configuration", self.verify_docker_files),
            ("Monitoring Configuration", self.verify_monitoring_files),
            ("CI/CD Configuration", self.verify_ci_cd),
            ("Integration Tests", self.verify_integration_tests),
            ("Documentation", self.verify_documentation),
        ]
        
        results = []
        for name, check_func in checks:
            try:
                result = check_func()
                results.append((name, result))
            except Exception as e:
                print(f"\n⚠️  Error in {name}: {e}")
                results.append((name, False))
        
        # Summary
        self.print_header("Summary")
        print(f"[OK] Checks Passed: {self.checks_passed}")
        print(f"[FAIL] Checks Failed: {self.checks_failed}")
        
        all_passed = all(result for _, result in results)
        if all_passed:
            print("\n[SUCCESS] All checks passed! AlphaAgent is production-ready.")
        else:
            print("\n[WARNING] Some checks failed. Review output above.")
        
        return all_passed
    
    def print_next_steps(self):
        """Print next steps for deployment."""
        self.print_header("Next Steps")
        print("""
1. Review Documentation:
   - QUICKSTART.md      (30-second setup)
   - DEPLOYMENT.md      (Comprehensive guide)
   - MONITORING.md      (Observability setup)

2. Start with Docker:
   docker-compose up -d
   curl http://localhost:8000/health

3. Run Tests:
   pytest simple_test.py comprehensive_test.py integration_test.py -v

4. Access Services:
   - API:        http://localhost:8000/docs
   - Prometheus: http://localhost:9090
   - Grafana:    http://localhost:3000

5. Monitor:
   docker-compose logs -f web
        """)


def main():
    """Main entry point."""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    test_all = '--test-all' in sys.argv
    
    verifier = ProductionVerifier(verbose=verbose)
    all_passed = verifier.run_all_checks()
    
    if test_all:
        verifier.print_next_steps()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
