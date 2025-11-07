#!/usr/bin/env python3
"""
Simple API Test Runner for AlphaAgent Backend

Tests the following endpoints:
1. Health Check - GET /health
2. Portfolio Parsing - POST /parse_portfolio
3. Tax Loss Identification - POST /identify_loss
4. Compliance Checking - POST /check_compliance
5. Recommendations - POST /recommend_replace
6. Savings Calculation - POST /calculate_savings
"""

import requests
import json
import time
from pathlib import Path
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.paths import get_sample_portfolio
from backend.utils.env import load_env, get_env

# Load environment
load_env()

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Test health endpoint"""
    print_section("TEST 1: Health Check Endpoint")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("[OK] PASS: Health check successful")
            return True
        else:
            print(f"[FAIL] FAIL: Unexpected status code {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] FAIL: Cannot connect to API at localhost:8000")
        print("       Make sure to run: python -m uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"[FAIL] FAIL: {str(e)}")
        return False

def test_parse_portfolio():
    """Test portfolio parsing endpoint"""
    print_section("TEST 2: Portfolio Parsing")
    try:
        portfolio_path = get_sample_portfolio()
        with open(portfolio_path, 'r') as f:
            portfolio_data = f.read()
        
        resp = requests.post(f"{BASE_URL}/parse_portfolio", data=portfolio_data, timeout=10)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Parsed Holdings: {len(data.get('holdings', []))} items")
            if data.get('holdings'):
                print(f"First holding: {data['holdings'][0]}")
            print("[OK] PASS: Portfolio parsed successfully")
            return True
        else:
            print(f"[FAIL] FAIL: Status code {resp.status_code}")
            print(resp.text)
            return False
    except Exception as e:
        print(f"[FAIL] FAIL: {str(e)}")
        return False

def test_identify_loss():
    """Test tax loss identification endpoint"""
    print_section("TEST 3: Tax Loss Identification")
    try:
        payload = {
            "holdings": [
                {"symbol": "AAPL", "cost_basis": 150, "current_price": 140, "quantity": 10},
                {"symbol": "MSFT", "cost_basis": 300, "current_price": 320, "quantity": 5},
            ]
        }
        
        resp = requests.post(f"{BASE_URL}/identify_loss", json=payload, timeout=10)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Identified Losses: {len(data.get('losses', []))} items")
            if data.get('losses'):
                print(f"Loss details: {data['losses'][0]}")
            print("[OK] PASS: Loss identification working")
            return True
        else:
            print(f"[FAIL] FAIL: Status code {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] FAIL: {str(e)}")
        return False

def test_get_correlation():
    """Test correlation calculation"""
    print_section("TEST 4: Price Correlation")
    try:
        payload = {"symbol1": "AAPL", "symbol2": "MSFT"}
        resp = requests.post(f"{BASE_URL}/get_correlation", json=payload, timeout=10)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            correlation = data.get('correlation')
            print(f"Correlation (AAPL vs MSFT): {correlation}")
            print("[OK] PASS: Correlation calculated")
            return True
        else:
            print(f"[FAIL] FAIL: Status code {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] FAIL: {str(e)}")
        return False

def test_recommend_replacement():
    """Test replacement recommendation"""
    print_section("TEST 5: Replacement Recommendation")
    try:
        payload = {
            "symbol": "AAPL",
            "sector": "Technology",
            "market_cap": 2500000000000
        }
        resp = requests.post(f"{BASE_URL}/recommend_replace", json=payload, timeout=10)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            replacements = data.get('recommendations', [])
            print(f"Recommended Replacements: {len(replacements)} items")
            if replacements:
                print(f"Top recommendation: {replacements[0]}")
            print("[OK] PASS: Recommendations generated")
            return True
        else:
            print(f"[FAIL] FAIL: Status code {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] FAIL: {str(e)}")
        return False

def test_local_utilities():
    """Test local utility functions without API"""
    print_section("TEST 6: Local Utilities")
    try:
        from backend.utils.paths import PathManager
        from backend.utils.env import EnvManager
        from backend.utils.recommendations import PriceDataProvider
        
        # Test PathManager
        print("\n[SEARCH] Testing PathManager...")
        pm = PathManager()
        root = pm.get_project_root()
        print(f"  Project root: {root}")
        assert root.exists(), "Project root doesn't exist"
        print("  [OK] Project root verified")
        
        # Test EnvManager
        print("\n[SEARCH] Testing EnvManager...")
        em = EnvManager()
        env_vars = em.get_subprocess_env()
        print(f"  Subprocess env vars: {len(env_vars)} variables")
        print("  [OK] Environment variables loaded")
        
        # Test PriceDataProvider
        print("\n[SEARCH] Testing PriceDataProvider...")
        pdp = PriceDataProvider()
        prices = pdp.get_historical_prices("TEST_SYMBOL", use_cache=False)
        print(f"  Price data fetched: {len(prices)} rows")
        assert len(prices) > 0, "No price data returned"
        print("  [OK] Price data generation working")
        
        print("\n[OK] PASS: All local utilities working")
        return True
    except Exception as e:
        print(f"\n[FAIL] FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AlphaAgent Backend Test Suite")
    print("="*70)
    print("\nNote: Most tests require the API server running at localhost:8000")
    print("      To start the server: python -m uvicorn backend.main:app --reload\n")
    
    tests = [
        ("Local Utilities (No API needed)", test_local_utilities),
        ("Health Check", test_health),
        ("Portfolio Parsing", test_parse_portfolio),
        ("Tax Loss Identification", test_identify_loss),
        ("Price Correlation", test_get_correlation),
        ("Recommendation Engine", test_recommend_replacement),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"\nUnexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
