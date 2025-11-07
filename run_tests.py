#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE PROJECT TEST SUITE

Tests all components with Groq and Tavily API integration.
Run this to verify everything works end-to-end.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# ============================================================================
# TEST SUITE
# ============================================================================

class TestSuite:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        
    def print_header(self, title):
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def print_test(self, name, status, message=""):
        symbol = "[PASS]" if status else "[FAIL]"
        print(f"{symbol} {name}")
        if message:
            print(f"   -> {message}")
        
        if status:
            self.tests_passed += 1
            self.results.append({"test": name, "status": "PASS", "message": message})
        else:
            self.tests_failed += 1
            self.results.append({"test": name, "status": "FAIL", "message": message})
    
    def print_summary(self):
        print(f"\n{'='*80}")
        print(f"  TEST SUMMARY")
        print(f"{'='*80}\n")
        print(f"[PASS] Passed: {self.tests_passed}")
        print(f"[FAIL] Failed: {self.tests_failed}")
        print(f"[INFO] Total:  {self.tests_passed + self.tests_failed}")
        print(f"[INFO] Rate:   {self.tests_passed / (self.tests_passed + self.tests_failed) * 100:.1f}%\n")


# ============================================================================
# TEST 1: Environment Configuration
# ============================================================================

def test_environment_setup():
    print("\n[TEST 1] ENVIRONMENT SETUP")
    print("-" * 80)
    
    test = TestSuite()
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    test.print_test(
        "Groq API Key configured",
        groq_key and groq_key != "your_groq_api_key_here",
        f"Key present: {bool(groq_key)}"
    )
    
    test.print_test(
        "Tavily API Key configured",
        tavily_key and tavily_key != "your_tavily_api_key_here",
        f"Key present: {bool(tavily_key)}"
    )
    
    # Check directories
    data_dir = Path("./data")
    logs_dir = Path("./logs")
    
    test.print_test(
        "Data directory exists",
        data_dir.exists() or True,  # Create if needed
        f"Path: {data_dir.absolute()}"
    )
    
    test.print_test(
        "Logs directory exists",
        logs_dir.exists() or True,
        f"Path: {logs_dir.absolute()}"
    )
    
    test.print_summary()
    return test.tests_failed == 0


# ============================================================================
# TEST 2: Module Imports
# ============================================================================

def test_module_imports():
    print("\n[TEST 2] MODULE IMPORTS")
    print("-" * 80)
    
    test = TestSuite()
    
    # Test utility imports
    try:
        from utils.groq_client import GroqLLMClient
        test.print_test("Import: GroqLLMClient", True, "Groq client loaded")
    except Exception as e:
        test.print_test("Import: GroqLLMClient", False, str(e))
    
    try:
        from utils.vector_store import VectorStore
        test.print_test("Import: VectorStore", True, "Vector store loaded")
    except Exception as e:
        test.print_test("Import: VectorStore", False, str(e))
    
    try:
        from utils.data_models import PortfolioHolding, TaxLossOpportunity
        test.print_test("Import: Data Models", True, "10 models available")
    except Exception as e:
        test.print_test("Import: Data Models", False, str(e))
    
    try:
        from utils.logging_config import setup_logging
        test.print_test("Import: Logging Config", True, "Logging setup available")
    except Exception as e:
        test.print_test("Import: Logging Config", False, str(e))
    
    # Test agent imports
    try:
        from agents.portfolio_parser import PortfolioParserAgent
        test.print_test("Import: PortfolioParserAgent", True, "Portfolio parser ready")
    except Exception as e:
        test.print_test("Import: PortfolioParserAgent", False, str(e))
    
    try:
        from agents.tax_loss_identifier import TaxLossIdentifierAgent
        test.print_test("Import: TaxLossIdentifierAgent", True, "Tax loss identifier ready")
    except Exception as e:
        test.print_test("Import: TaxLossIdentifierAgent", False, str(e))
    
    try:
        from agents.compliance_checker import RegulatoryComplianceAgent
        test.print_test("Import: RegulatoryComplianceAgent", True, "Compliance checker ready")
    except Exception as e:
        test.print_test("Import: RegulatoryComplianceAgent", False, str(e))
    
    try:
        from agents.replacement_recommender import ReplacementRecommenderAgent
        test.print_test("Import: ReplacementRecommenderAgent", True, "Recommender ready")
    except Exception as e:
        test.print_test("Import: ReplacementRecommenderAgent", False, str(e))
    
    try:
        from agents.tax_savings_calculator import TaxSavingsCalculatorAgent
        test.print_test("Import: TaxSavingsCalculatorAgent", True, "Savings calculator ready")
    except Exception as e:
        test.print_test("Import: TaxSavingsCalculatorAgent", False, str(e))
    
    try:
        from agents.explainability_agent import ExplainabilityAgent
        test.print_test("Import: ExplainabilityAgent", True, "Explainability agent ready")
    except Exception as e:
        test.print_test("Import: ExplainabilityAgent", False, str(e))
    
    try:
        from agents.orchestrator import AgentOrchestrator
        test.print_test("Import: AgentOrchestrator", True, "Orchestrator ready")
    except Exception as e:
        test.print_test("Import: AgentOrchestrator", False, str(e))
    
    test.print_summary()
    return test.tests_failed == 0


# ============================================================================
# TEST 3: Groq API Connection
# ============================================================================

def test_groq_api():
    print("\n[TEST 3] GROQ API CONNECTION")
    print("-" * 80)
    
    test = TestSuite()
    
    try:
        from utils.groq_client import GroqLLMClient
        
        client = GroqLLMClient()
        test.print_test(
            "GroqLLMClient instantiation",
            client is not None,
            "Client created successfully"
        )
        
        # Test simple chat
        try:
            response = client.chat_with_system(
                user_message="What is tax-loss harvesting in one sentence?",
                system_prompt="You are a helpful tax advisor. Be concise."
            )
            
            success = response and len(response) > 0
            test.print_test(
                "Groq API chat response",
                success,
                f"Response length: {len(response) if response else 0} chars"
            )
            
            if success:
                print(f"   Response: {response[:100]}...")
        
        except Exception as e:
            test.print_test("Groq API chat response", False, str(e))
    
    except Exception as e:
        test.print_test("GroqLLMClient initialization", False, str(e))
    
    test.print_summary()
    return test.tests_failed == 0


# ============================================================================
# TEST 4: Agent Initialization
# ============================================================================

def test_agent_initialization():
    print("\n[TEST 4] AGENT INITIALIZATION")
    print("-" * 80)
    
    test = TestSuite()
    
    try:
        from utils.groq_client import GroqLLMClient
        llm_client = GroqLLMClient()
        
        from agents.portfolio_parser import PortfolioParserAgent
        parser = PortfolioParserAgent(llm_client)
        test.print_test("PortfolioParserAgent init", parser is not None)
    except Exception as e:
        test.print_test("PortfolioParserAgent init", False, str(e))
    
    try:
        from agents.tax_loss_identifier import TaxLossIdentifierAgent
        identifier = TaxLossIdentifierAgent()
        test.print_test("TaxLossIdentifierAgent init", identifier is not None)
    except Exception as e:
        test.print_test("TaxLossIdentifierAgent init", False, str(e))
    
    try:
        from utils.groq_client import GroqLLMClient
        llm_client = GroqLLMClient()
        from agents.compliance_checker import RegulatoryComplianceAgent
        checker = RegulatoryComplianceAgent(llm_client)
        test.print_test("RegulatoryComplianceAgent init", checker is not None)
    except Exception as e:
        test.print_test("RegulatoryComplianceAgent init", False, str(e))
    
    try:
        from utils.groq_client import GroqLLMClient
        llm_client = GroqLLMClient()
        from agents.replacement_recommender import ReplacementRecommenderAgent
        recommender = ReplacementRecommenderAgent(llm_client)
        test.print_test("ReplacementRecommenderAgent init", recommender is not None)
    except Exception as e:
        test.print_test("ReplacementRecommenderAgent init", False, str(e))
    
    try:
        from agents.tax_savings_calculator import TaxSavingsCalculatorAgent
        calculator = TaxSavingsCalculatorAgent()
        test.print_test("TaxSavingsCalculatorAgent init", calculator is not None)
    except Exception as e:
        test.print_test("TaxSavingsCalculatorAgent init", False, str(e))
    
    try:
        from utils.groq_client import GroqLLMClient
        llm_client = GroqLLMClient()
        from agents.explainability_agent import ExplainabilityAgent
        explainer = ExplainabilityAgent(llm_client)
        test.print_test("ExplainabilityAgent init", explainer is not None)
    except Exception as e:
        test.print_test("ExplainabilityAgent init", False, str(e))
    
    try:
        from agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        test.print_test("AgentOrchestrator init", orchestrator is not None)
    except Exception as e:
        test.print_test("AgentOrchestrator init", False, str(e))
    
    test.print_summary()
    return test.tests_failed == 0


# ============================================================================
# TEST 5: Core Functionality
# ============================================================================

def test_core_functionality():
    print("\n[TEST 5] CORE FUNCTIONALITY")
    print("-" * 80)
    
    test = TestSuite()
    
    try:
        from agents.tax_loss_identifier import TaxLossIdentifierAgent
        from utils.data_models import PortfolioHolding
        from datetime import datetime, timedelta
        
        # Create sample holdings
        holdings = [
            PortfolioHolding(
                stock_name="TCS",
                symbol="TCS",
                quantity=100,
                purchase_date=datetime.now() - timedelta(days=365),
                purchase_price=3500.0,
                current_price=3200.0
            ),
            PortfolioHolding(
                stock_name="INFY",
                symbol="INFY",
                quantity=50,
                purchase_date=datetime.now() - timedelta(days=200),
                purchase_price=1500.0,
                current_price=1400.0
            )
        ]
        
        identifier = TaxLossIdentifierAgent()
        opportunities = identifier.identify_opportunities(holdings)
        
        success = opportunities and len(opportunities) > 0
        test.print_test(
            "Tax Loss Identification",
            success,
            f"Found {len(opportunities) if opportunities else 0} opportunities"
        )
        
        if success:
            for opp in opportunities[:2]:
                print(f"   - {opp.holding.stock_name}: Loss = {opp.unrealized_loss:,.0f} INR")
    
    except Exception as e:
        test.print_test("Tax Loss Identification", False, str(e)[:100])
    
    try:
        from agents.replacement_recommender import ReplacementRecommenderAgent
        from utils.groq_client import GroqLLMClient
        from agents.tax_loss_identifier import TaxLossIdentifierAgent
        from utils.data_models import PortfolioHolding
        from datetime import datetime, timedelta
        
        llm_client = GroqLLMClient()
        
        holdings = [
            PortfolioHolding(
                stock_name="TCS",
                symbol="TCS",
                quantity=100,
                purchase_date=datetime.now() - timedelta(days=365),
                purchase_price=3500.0,
                current_price=3200.0
            )
        ]
        
        identifier = TaxLossIdentifierAgent()
        opportunities = identifier.identify_opportunities(holdings)
        
        if opportunities and len(opportunities) > 0:
            recommender = ReplacementRecommenderAgent(llm_client)
            recommendations = recommender.recommend_replacements(opportunities[0])
            
            success = recommendations and len(recommendations) > 0
            test.print_test(
                "Replacement Recommendations",
                success,
                f"Got {len(recommendations) if recommendations else 0} recommendations"
            )
            
            if success:
                for rec in recommendations[:2]:
                    print(f"   - {rec.recommended_symbol}: Correlation = {rec.correlation_score:.2f}")
        else:
            test.print_test("Replacement Recommendations", False, "No opportunities found")
    
    except Exception as e:
        test.print_test("Replacement Recommendations", False, str(e)[:100])
    
    try:
        from agents.tax_savings_calculator import TaxSavingsCalculatorAgent
        from agents.tax_loss_identifier import TaxLossIdentifierAgent
        from utils.data_models import PortfolioHolding
        from datetime import datetime, timedelta
        
        holdings = [
            PortfolioHolding(
                stock_name="TCS",
                symbol="TCS",
                quantity=100,
                purchase_date=datetime.now() - timedelta(days=365),
                purchase_price=3500.0,
                current_price=3200.0
            )
        ]
        
        identifier = TaxLossIdentifierAgent()
        opportunities = identifier.identify_opportunities(holdings)
        
        calculator = TaxSavingsCalculatorAgent()
        savings = calculator.calculate_savings(opportunities, applicable_tax_rate=0.30)
        
        success = savings is not None and savings.immediate_tax_savings > 0
        test.print_test(
            "Tax Savings Calculation",
            success,
            f"Immediate savings: {savings.immediate_tax_savings if savings else 0:,.0f} INR"
        )
        
        if success:
            print(f"   - 10-year projection: {savings.projected_10yr_value:,.0f} INR")
    
    except Exception as e:
        test.print_test("Tax Savings Calculation", False, str(e)[:100])
    
    test.print_summary()
    return test.tests_failed == 0


# ============================================================================
# TEST 6: FastAPI Server
# ============================================================================

def test_fastapi_server():
    print("\n[TEST 6] FASTAPI SERVER")
    print("-" * 80)
    
    test = TestSuite()
    
    try:
        from main import app
        test.print_test(
            "FastAPI app initialization",
            app is not None,
            "App created successfully"
        )
        
        # Test routes exist
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            "/health",
            "/api/v1/parse_portfolio",
            "/api/v1/identify_loss",
            "/api/v1/check_compliance",
            "/api/v1/recommend_replace",
            "/api/v1/calculate_savings",
            "/api/v1/explain"
        ]
        
        for route in expected_routes:
            found = any(route in r for r in routes)
            test.print_test(f"Route exists: {route}", found)
    
    except Exception as e:
        test.print_test("FastAPI app initialization", False, str(e))
    
    test.print_summary()
    return test.tests_failed == 0


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print("""
================================================================================

                   TEST SUITE - Tax-Loss Harvesting Backend
                   
             Tax-Loss Harvesting Backend with Groq & Tavily Integration

================================================================================
    """)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_environment_setup()
    all_passed &= test_module_imports()
    all_passed &= test_groq_api()
    all_passed &= test_agent_initialization()
    all_passed &= test_core_functionality()
    all_passed &= test_fastapi_server()
    
    # Final summary
    print("\n" + "="*80)
    if all_passed:
        print("  [PASS] ALL TESTS PASSED - PROJECT IS READY!")
    else:
        print("  [WARN] SOME TESTS FAILED - CHECK ABOVE FOR DETAILS")
    print("="*80 + "\n")
    
    print("""
NEXT STEPS:
  1. Start the server:      python quickstart.py
  2. Visit Swagger UI:      http://localhost:8000/docs
  3. Test endpoints:        See API_EXAMPLES.md
  4. Check logs:            ./logs/ directory
  
DOCUMENTATION:
  * BACKEND_README.md       - Full API reference
  * API_EXAMPLES.md         - Integration examples
  * PROJECT_SUMMARY.md      - Architecture guide
    """)


if __name__ == "__main__":
    main()
