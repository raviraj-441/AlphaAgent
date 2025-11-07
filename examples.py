"""
Example usage of the Tax-Loss Harvesting Multi-Agent System.
"""

import asyncio
import json
from datetime import datetime
from backend.utils.groq_client import GroqLLMClient
from backend.utils.data_models import PortfolioHolding, TaxLossOpportunity
from backend.agents.portfolio_parser import PortfolioParserAgent
from backend.agents.tax_loss_identifier import TaxLossIdentifierAgent
from backend.agents.replacement_recommender import ReplacementRecommenderAgent
from backend.agents.tax_savings_calculator import TaxSavingsCalculatorAgent
from backend.agents.explainability_agent import ExplainabilityAgent
from backend.agents.orchestrator import AgentOrchestrator, visualize_negotiation_flow


def example_1_basic_tax_loss_identification():
    """Example 1: Identify tax-loss harvesting opportunities"""
    print("\n" + "="*60)
    print("Example 1: Tax Loss Identification")
    print("="*60)
    
    # Create sample holdings
    holdings = [
        PortfolioHolding(
            stock_name="Tata Consultancy Services",
            symbol="TCS",
            quantity=100,
            purchase_date=datetime(2023, 1, 15),
            purchase_price=3500,
            current_price=3200
        ),
        PortfolioHolding(
            stock_name="Infosys",
            symbol="INFY",
            quantity=50,
            purchase_date=datetime(2023, 3, 20),
            purchase_price=1800,
            current_price=1600
        ),
        PortfolioHolding(
            stock_name="Reliance Industries",
            symbol="RELIANCE",
            quantity=75,
            purchase_date=datetime(2022, 12, 1),
            purchase_price=2600,
            current_price=2750
        ),
    ]
    
    # Identify opportunities
    agent = TaxLossIdentifierAgent()
    result = agent.identify_opportunities(holdings, top_n=10)
    
    print(f"\nStatus: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"\nOpportunities found: {len(result['opportunities'])}")
    
    for opp in result['opportunities']:
        print(f"\n  Symbol: {opp.holding.symbol}")
        print(f"    Unrealized Loss: ${opp.unrealized_loss:,.2f}")
        print(f"    Loss %: {opp.loss_percentage:.2f}%")
        print(f"    Eligible: {opp.eligible_for_harvesting}")
        print(f"    Reason: {opp.reason}")
        print(f"    Rank: {opp.rank}")
    
    print(f"\nSummary:")
    for key, value in result['summary'].items():
        print(f"  {key}: {value}")


def example_2_tax_savings_calculation():
    """Example 2: Calculate tax savings and projections"""
    print("\n" + "="*60)
    print("Example 2: Tax Savings Calculation")
    print("="*60)
    
    # Create sample opportunities
    holdings = [
        PortfolioHolding(
            stock_name="TCS",
            symbol="TCS",
            quantity=100,
            purchase_date=datetime(2023, 1, 15),
            purchase_price=3500,
            current_price=3200
        ),
        PortfolioHolding(
            stock_name="INFY",
            symbol="INFY",
            quantity=50,
            purchase_date=datetime(2023, 3, 20),
            purchase_price=1800,
            current_price=1600
        ),
    ]
    
    opportunities = [
        TaxLossOpportunity(
            holding=holdings[0],
            unrealized_loss=30000,
            loss_percentage=8.6,
            eligible_for_harvesting=True
        ),
        TaxLossOpportunity(
            holding=holdings[1],
            unrealized_loss=10000,
            loss_percentage=11.1,
            eligible_for_harvesting=True
        ),
    ]
    
    # Calculate savings
    calculator = TaxSavingsCalculatorAgent()
    calculation = calculator.calculate_savings(
        opportunities,
        annual_income=500000
    )
    
    report = calculator.generate_savings_report(calculation)
    print(f"\nTax Savings Report:")
    print(json.dumps(report, indent=2, default=str))


def example_3_replacement_recommendations():
    """Example 3: Get replacement security recommendations"""
    print("\n" + "="*60)
    print("Example 3: Replacement Recommendations")
    print("="*60)
    
    # Note: Requires Groq API key
    try:
        llm_client = GroqLLMClient()
        
        holding = PortfolioHolding(
            stock_name="TCS",
            symbol="TCS",
            quantity=100,
            purchase_date=datetime(2023, 1, 15),
            purchase_price=3500,
            current_price=3200
        )
        
        opportunity = TaxLossOpportunity(
            holding=holding,
            unrealized_loss=30000,
            loss_percentage=8.6,
            eligible_for_harvesting=True
        )
        
        recommender = ReplacementRecommenderAgent(llm_client)
        recommendations = recommender.recommend_replacements(opportunity)
        
        print(f"\nReplacements for {opportunity.holding.symbol}:")
        for rec in recommendations:
            print(f"\n  {rec.recommended_symbol}")
            print(f"    Correlation: {rec.correlation_score:.3f}")
            print(f"    Semantic Similarity: {rec.semantic_similarity:.3f}")
            print(f"    Reason: {rec.reason}")
    
    except Exception as e:
        print(f"⚠️  Skipping - Groq API not available: {e}")


def example_4_explainability():
    """Example 4: Generate SHAP explanations"""
    print("\n" + "="*60)
    print("Example 4: Explainability with SHAP")
    print("="*60)
    
    try:
        llm_client = GroqLLMClient()
        
        holding = PortfolioHolding(
            stock_name="TCS",
            symbol="TCS",
            quantity=100,
            purchase_date=datetime(2023, 1, 15),
            purchase_price=3500,
            current_price=3200
        )
        
        opportunity = TaxLossOpportunity(
            holding=holding,
            unrealized_loss=30000,
            loss_percentage=8.6,
            eligible_for_harvesting=True
        )
        
        explainer = ExplainabilityAgent(llm_client)
        
        # Get SHAP explanation
        shap_exp = explainer.get_shap_explanation(opportunity)
        print(f"\nSHAP Explanation for {opportunity.holding.symbol}:")
        print(f"  Recommendation: {shap_exp['recommendation']}")
        print(f"  Base Value: {shap_exp['base_value']}")
        print(f"  Predicted Value: {shap_exp['predicted_value']}")
        print(f"\n  Feature Importance:")
        for feat_imp in shap_exp['feature_importance'][:3]:
            print(f"    {feat_imp['feature']}: {feat_imp['shap_value']} (Rank: {feat_imp['importance_rank']})")
        
        # Get counterfactual
        print(f"\n  Counterfactual Explanation:")
        counterfactual = explainer.get_counterfactual_explanation(opportunity)
        print(f"    {counterfactual}")
        
        # Get decision tree
        decision_tree = explainer.create_decision_tree_explanation(opportunity)
        print(f"\n  Decision Confidence: {decision_tree['confidence']}")
    
    except Exception as e:
        print(f"⚠️  Skipping - Groq API not available: {e}")


def example_5_orchestration():
    """Example 5: Full orchestration workflow"""
    print("\n" + "="*60)
    print("Example 5: Full Multi-Agent Orchestration")
    print("="*60)
    
    try:
        # This is a demo - actual orchestration requires portfolio file data
        print("\nOrchestration flow:")
        print("  1. Parse portfolio file")
        print("  2. Identify tax-loss opportunities")
        print("  3. Check regulatory compliance")
        print("  4. Get replacement recommendations")
        print("  5. Calculate tax savings")
        print("  6. Run multi-iteration negotiation")
        print("  7. Generate final recommendations")
        
        print("\nTo run full orchestration, call:")
        print("  orchestrator = AgentOrchestrator()")
        print("  result = orchestrator.orchestrate(")
        print("      portfolio_file_data=bytes,")
        print("      file_type='csv'")
        print("  )")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_6_sensitivity_analysis():
    """Example 6: Sensitivity analysis on tax rate"""
    print("\n" + "="*60)
    print("Example 6: Sensitivity Analysis")
    print("="*60)
    
    # Create sample opportunities
    holding = PortfolioHolding(
        stock_name="TCS",
        symbol="TCS",
        quantity=100,
        purchase_date=datetime(2023, 1, 15),
        purchase_price=3500,
        current_price=3200
    )
    
    opportunities = [
        TaxLossOpportunity(
            holding=holding,
            unrealized_loss=30000,
            loss_percentage=8.6,
            eligible_for_harvesting=True
        )
    ]
    
    # Perform sensitivity analysis
    calculator = TaxSavingsCalculatorAgent()
    base_calc = calculator.calculate_savings(opportunities)
    
    # Test different tax rates
    tax_rates = [0.10, 0.20, 0.30]
    results = []
    for rate in tax_rates:
        calc = calculator.calculate_savings(opportunities, applicable_tax_rate=rate)
        results.append({
            "tax_rate": f"{rate*100}%",
            "immediate_savings": f"${calc.immediate_tax_savings:,.2f}",
            "projected_10yr": f"${calc.projected_10yr_value:,.2f}"
        })
    
    print(f"\nSensitivity Analysis - Tax Rate Impact:")
    print(json.dumps(results, indent=2))


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("  Tax-Loss Harvesting System - Examples & Demonstrations")
    print("="*60)
    
    # Run examples that don't require Groq API
    example_1_basic_tax_loss_identification()
    example_2_tax_savings_calculation()
    example_6_sensitivity_analysis()
    
    # Run examples that require Groq API (with error handling)
    example_3_replacement_recommendations()
    example_4_explainability()
    example_5_orchestration()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\n📚 Check BACKEND_README.md for detailed API documentation")
    print("🚀 Start the server with: python quickstart.py")
    print("📖 Interactive docs available at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
