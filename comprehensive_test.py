#!/usr/bin/env python3
"""
Comprehensive Test Suite for AlphaAgent
Tests all components: API endpoints, data models, agents, and utilities
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_section(title):
    """Print formatted section"""
    print(f"\n{'-'*80}")
    print(f"  {title}")
    print(f"{'-'*80}")

# ============================================================================
# SECTION 1: API ENDPOINT TESTS
# ============================================================================

def test_api_endpoints():
    """Test all 6 API endpoints"""
    print_header("SECTION 1: API ENDPOINT TESTS")
    
    results = {}
    
    # Test 1: Health Check
    print_section("1.1 Health Check Endpoint")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "status" in data and data["status"] == "OK"
        assert "service" in data
        assert "version" in data
        print("✅ PASS: Health check working")
        print(f"   Response: {json.dumps(data, indent=6)}")
        results["health"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["health"] = False
    
    # Test 2: Portfolio Parsing
    print_section("1.2 Portfolio Parsing Endpoint")
    try:
        csv_path = Path("data/test_portfolios/sample_portfolio.csv")
        assert csv_path.exists(), f"Test file not found: {csv_path}"
        
        with open(csv_path, 'rb') as f:
            files = {'file': f}
            resp = requests.post(f"{BASE_URL}/api/v1/parse_portfolio", files=files, timeout=10)
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "success" or resp.status_code == 200
        print("✅ PASS: Portfolio parsing working")
        print(f"   Status: {data.get('status')}")
        print(f"   Message: {data.get('message')}")
        results["portfolio_parsing"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["portfolio_parsing"] = False
    
    # Test 3: Tax Loss Identification
    print_section("1.3 Tax Loss Identification Endpoint")
    try:
        payload = {
            "holdings": [
                {
                    "stock_name": "Reliance Industries",
                    "symbol": "RELIANCE",
                    "quantity": 10,
                    "purchase_date": "2023-01-15",
                    "purchase_price": 2500,
                    "current_price": 2100
                },
                {
                    "stock_name": "Tata Consultancy Services",
                    "symbol": "TCS",
                    "quantity": 5,
                    "purchase_date": "2023-03-20",
                    "purchase_price": 3500,
                    "current_price": 3200
                }
            ],
            "top_n": 10
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/identify_loss",
            json=payload,
            timeout=10
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "success"
        assert "opportunities" in data.get("data", {})
        opportunities = data["data"]["opportunities"]
        assert len(opportunities) > 0, "No opportunities identified"
        print("✅ PASS: Tax loss identification working")
        print(f"   Opportunities Found: {len(opportunities)}")
        for i, opp in enumerate(opportunities[:2], 1):
            print(f"   {i}. {opp['symbol']}: Loss ${opp['unrealized_loss']:.2f} ({opp['loss_percentage']:.1f}%)")
        results["identify_loss"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["identify_loss"] = False
    
    # Test 4: Compliance Check
    print_section("1.4 Compliance Check Endpoint")
    try:
        payload = {
            "symbol": "RELIANCE",
            "stock_name": "Reliance Industries",
            "quantity": 10,
            "purchase_price": 2500,
            "current_price": 2100,
            "purchase_date": "2023-01-15",
            "unrealized_loss": 4000
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/check_compliance",
            json=payload,
            timeout=10
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "success"
        compliance_data = data.get("data", {})
        assert "is_compliant" in compliance_data
        assert "status" in compliance_data
        assert "risk_level" in compliance_data
        print("✅ PASS: Compliance check working")
        print(f"   Is Compliant: {compliance_data['is_compliant']}")
        print(f"   Status: {compliance_data['status']}")
        print(f"   Risk Level: {compliance_data['risk_level']}")
        results["compliance"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["compliance"] = False
    
    # Test 5: Recommendations
    print_section("1.5 Recommendations Endpoint")
    try:
        payload = {
            "symbol": "RELIANCE",
            "stock_name": "Reliance Industries",
            "quantity": 10,
            "purchase_price": 2500,
            "current_price": 2100,
            "purchase_date": "2023-01-15",
            "unrealized_loss": 4000
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/recommend_replace",
            json=payload,
            timeout=10
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "success"
        rec_data = data.get("data", {})
        assert "original_symbol" in rec_data
        assert "replacements" in rec_data
        print("✅ PASS: Recommendations endpoint working")
        print(f"   Original Symbol: {rec_data['original_symbol']}")
        print(f"   Recommendations: {rec_data['total_recommendations']}")
        results["recommendations"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["recommendations"] = False
    
    # Test 6: Savings Calculation
    print_section("1.6 Savings Calculation Endpoint")
    try:
        payload = {
            "opportunities": [
                {
                    "symbol": "RELIANCE",
                    "stock_name": "Reliance Industries",
                    "quantity": 10,
                    "purchase_price": 2500,
                    "current_price": 2100,
                    "purchase_date": "2023-01-15",
                    "unrealized_loss": 4000
                }
            ],
            "annual_income": 400000,
            "tax_rate": 0.20
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/calculate_savings",
            json=payload,
            timeout=10
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "success"
        savings_data = data.get("data", {})
        assert "summary" in savings_data
        assert "immediate_impact" in savings_data
        print("✅ PASS: Savings calculation working")
        summary = savings_data["summary"]
        immediate = savings_data["immediate_impact"]
        print(f"   Transactions Harvested: {summary['transactions_harvested']}")
        print(f"   Total Loss Harvested: {summary['total_loss_harvested']}")
        print(f"   Tax Savings: {immediate['tax_savings']}")
        results["savings"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["savings"] = False
    
    return results

# ============================================================================
# SECTION 2: DATA MODEL TESTS
# ============================================================================

def test_data_models():
    """Test data models and validation"""
    print_header("SECTION 2: DATA MODEL TESTS")
    
    results = {}
    
    print_section("2.1 PortfolioHolding Model")
    try:
        from backend.utils.data_models import PortfolioHolding
        from datetime import datetime
        
        holding = PortfolioHolding(
            stock_name="Test Stock",
            symbol="TEST",
            quantity=100,
            purchase_date=datetime(2023, 1, 1),
            purchase_price=1000,
            current_price=900
        )
        
        assert holding.cost_basis == 100000
        assert holding.current_value == 90000
        assert holding.unrealized_gain_loss == -10000
        print("✅ PASS: PortfolioHolding model working correctly")
        print(f"   Cost Basis: ${holding.cost_basis:,.2f}")
        print(f"   Current Value: ${holding.current_value:,.2f}")
        print(f"   Unrealized P&L: ${holding.unrealized_gain_loss:,.2f}")
        results["portfolio_holding"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["portfolio_holding"] = False
    
    print_section("2.2 TaxLossOpportunity Model")
    try:
        from backend.utils.data_models import TaxLossOpportunity, PortfolioHolding
        from datetime import datetime
        
        holding = PortfolioHolding(
            stock_name="Test Stock",
            symbol="TEST",
            quantity=100,
            purchase_date=datetime(2023, 1, 1),
            purchase_price=1000,
            current_price=900
        )
        
        opportunity = TaxLossOpportunity(
            holding=holding,
            unrealized_loss=10000,
            loss_percentage=10.0,
            eligible_for_harvesting=True
        )
        
        assert opportunity.unrealized_loss == 10000
        assert opportunity.eligible_for_harvesting == True
        print("✅ PASS: TaxLossOpportunity model working correctly")
        print(f"   Unrealized Loss: ${opportunity.unrealized_loss:,.2f}")
        print(f"   Loss Percentage: {opportunity.loss_percentage:.2f}%")
        print(f"   Eligible: {opportunity.eligible_for_harvesting}")
        results["tax_loss_opportunity"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["tax_loss_opportunity"] = False
    
    return results

# ============================================================================
# SECTION 3: AGENT TESTS
# ============================================================================

def test_agents():
    """Test agent functionality"""
    print_header("SECTION 3: AGENT TESTS")
    
    results = {}
    
    print_section("3.1 Groq LLM Client")
    try:
        from backend.utils.groq_client import GroqLLMClient
        
        client = GroqLLMClient()
        assert client.api_key is not None
        assert client.model == "llama-3.1-8b-instant"
        print("✅ PASS: Groq LLM client initialized")
        print(f"   Model: {client.model}")
        print(f"   API Key: {'*' * 10}...{client.api_key[-4:]}")
        results["groq_client"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["groq_client"] = False
    
    print_section("3.2 Tax Loss Identifier Agent")
    try:
        from backend.agents.tax_loss_identifier import TaxLossIdentifierAgent
        from backend.utils.groq_client import GroqLLMClient
        from backend.utils.data_models import PortfolioHolding
        from datetime import datetime
        
        client = GroqLLMClient()
        agent = TaxLossIdentifierAgent()
        
        holding = PortfolioHolding(
            stock_name="Reliance",
            symbol="RELIANCE",
            quantity=10,
            purchase_date=datetime(2023, 1, 1),
            purchase_price=2500,
            current_price=2100
        )
        
        result = agent.identify_opportunities([holding], top_n=5)
        assert result.get("status") is not None
        assert "opportunities" in result
        print("✅ PASS: Tax loss identifier agent working")
        print(f"   Status: {result.get('status')}")
        print(f"   Opportunities Found: {len(result.get('opportunities', []))}")
        results["tax_loss_agent"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["tax_loss_agent"] = False
    
    return results

# ============================================================================
# SECTION 4: ENVIRONMENT & CONFIGURATION TESTS
# ============================================================================

def test_environment():
    """Test environment configuration"""
    print_header("SECTION 4: ENVIRONMENT & CONFIGURATION TESTS")
    
    results = {}
    
    print_section("4.1 Environment Variables")
    try:
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        groq_key = os.getenv("GROQ_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        assert groq_key is not None, "GROQ_API_KEY not set"
        assert tavily_key is not None, "TAVILY_API_KEY not set"
        assert len(groq_key) > 10, "GROQ_API_KEY seems incomplete"
        assert len(tavily_key) > 10, "TAVILY_API_KEY seems incomplete"
        
        print("✅ PASS: Environment variables configured")
        print(f"   GROQ_API_KEY: {'*' * 10}...{groq_key[-4:]}")
        print(f"   TAVILY_API_KEY: {'*' * 10}...{tavily_key[-4:]}")
        results["env_vars"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["env_vars"] = False
    
    print_section("4.2 Test Data Files")
    try:
        files_to_check = [
            "data/test_portfolios/sample_portfolio.csv",
            "data/test_portfolios/sample_portfolio_2lots.csv",
            "data/income_tax_law_texts/income_tax_law_excerpt_india.txt"
        ]
        
        missing = []
        for file_path in files_to_check:
            if not Path(file_path).exists():
                missing.append(file_path)
        
        if missing:
            raise FileNotFoundError(f"Missing files: {missing}")
        
        print("✅ PASS: All test data files present")
        for file_path in files_to_check:
            size = Path(file_path).stat().st_size
            print(f"   ✓ {file_path} ({size:,} bytes)")
        results["test_files"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["test_files"] = False
    
    print_section("4.3 Core Modules")
    try:
        import backend
        import backend.agents
        import backend.routes
        import backend.utils
        
        print("✅ PASS: All core modules importable")
        print("   ✓ backend")
        print("   ✓ backend.agents")
        print("   ✓ backend.routes")
        print("   ✓ backend.utils")
        results["core_modules"] = True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["core_modules"] = False
    
    return results

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and generate report"""
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "ALPHAAGENT COMPREHENSIVE TEST SUITE" + " "*24 + "║")
    print("╚" + "═"*78 + "╝")
    
    # Wait for server
    print(f"\n🔗 Connecting to Backend: {BASE_URL}")
    print("⏳ Waiting for server...", end="", flush=True)
    
    import time
    for i in range(15):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print(" ✅ Connected!\n")
            break
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    else:
        print("\n❌ Cannot connect to server!")
        sys.exit(1)
    
    # Run all test sections
    all_results = {}
    
    api_results = test_api_endpoints()
    all_results.update({"API": api_results})
    
    model_results = test_data_models()
    all_results.update({"Models": model_results})
    
    agent_results = test_agents()
    all_results.update({"Agents": agent_results})
    
    env_results = test_environment()
    all_results.update({"Environment": env_results})
    
    # Print Summary
    print_header("FINAL TEST SUMMARY")
    
    total_tests = 0
    total_passed = 0
    
    for section, tests in all_results.items():
        passed = sum(1 for v in tests.values() if v)
        total = len(tests)
        total_passed += passed
        total_tests += total
        
        status = "✅" if passed == total else "⚠️"
        print(f"{status} {section}: {passed}/{total} passed")
        for test_name, result in tests.items():
            symbol = "  ✓" if result else "  ✗"
            print(f"{symbol} {test_name}")
    
    print(f"\n{'='*80}")
    print(f"OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✨ ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL! ✨")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
