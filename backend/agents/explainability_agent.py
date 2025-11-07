"""
Explainability Agent - Provides SHAP-based explanations and counterfactuals.
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np

from backend.utils.groq_client import GroqLLMClient
from backend.utils.data_models import TaxLossOpportunity

logger = logging.getLogger(__name__)


class ExplainabilityAgent:
    """
    Uses SHAP values and LLM to explain tax-loss recommendations.
    Provides counterfactual explanations for decision reasoning.
    """
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize Explainability Agent.
        
        Args:
            llm_client: GroqLLMClient instance for generating explanations
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
    
    def get_shap_explanation(
        self,
        opportunity: TaxLossOpportunity,
        features: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Generate SHAP-based explanation for why an opportunity was selected.
        
        Args:
            opportunity: TaxLossOpportunity to explain
            features: Optional dict of feature values (e.g., loss_amount, holding_period)
        
        Returns:
            Dict with SHAP values and feature importance
        """
        if features is None:
            features = self._extract_features(opportunity)
        
        # Calculate SHAP values (simplified, without actual SHAP library)
        shap_values = self._calculate_mock_shap_values(features)
        
        # Interpret SHAP values
        interpretation = self._interpret_shap_values(shap_values, features)
        
        return {
            "opportunity_symbol": opportunity.holding.symbol,
            "recommendation": "HARVEST" if opportunity.eligible_for_harvesting else "HOLD",
            "shap_values": shap_values,
            "feature_importance": interpretation,
            "base_value": 0.5,  # Base model output
            "predicted_value": 0.92 if opportunity.eligible_for_harvesting else 0.25
        }
    
    def _extract_features(self, opportunity: TaxLossOpportunity) -> Dict[str, float]:
        """Extract features from opportunity for SHAP analysis."""
        holding_days = (datetime.now() - opportunity.holding.purchase_date).days
        
        return {
            "unrealized_loss_amount": opportunity.unrealized_loss,
            "loss_percentage": opportunity.loss_percentage,
            "holding_period_days": holding_days,
            "current_price": opportunity.holding.current_price,
            "cost_basis": opportunity.holding.cost_basis,
            "quantity": opportunity.holding.quantity,
            "recent_volatility": np.random.random() * 20  # Mock volatility
        }
    
    def _calculate_mock_shap_values(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate mock SHAP values based on features.
        In production, use actual SHAP library with trained model.
        """
        shap_values = {}
        
        # Simplified SHAP calculation
        for feature, value in features.items():
            if feature == "unrealized_loss_amount":
                # Higher loss = higher impact
                shap_values[feature] = min(value / 1000, 0.3)
            
            elif feature == "loss_percentage":
                # Higher percentage = higher impact
                shap_values[feature] = min(value / 100 * 0.2, 0.2)
            
            elif feature == "holding_period_days":
                # Longer holding = slightly negative impact (wait longer for recovery?)
                shap_values[feature] = -min(value / 1000, 0.1)
            
            else:
                # Other features have smaller impact
                shap_values[feature] = (np.random.random() - 0.5) * 0.05
        
        return shap_values
    
    def _interpret_shap_values(
        self,
        shap_values: Dict[str, float],
        features: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Interpret SHAP values into human-readable format."""
        interpretations = []
        
        # Sort by absolute SHAP value (importance)
        sorted_shaps = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        for feature_name, shap_value in sorted_shaps[:5]:  # Top 5 features
            feature_value = features.get(feature_name, 0)
            
            interpretation = {
                "feature": feature_name,
                "shap_value": round(shap_value, 4),
                "feature_value": round(feature_value, 2),
                "impact": "POSITIVE" if shap_value > 0 else "NEGATIVE",
                "importance_rank": len(interpretations) + 1
            }
            
            interpretations.append(interpretation)
        
        return interpretations
    
    def get_counterfactual_explanation(
        self,
        opportunity: TaxLossOpportunity,
        hypothetical_scenario: Dict[str, Any] = None
    ) -> str:
        """
        Generate natural language counterfactual explanation using LLM.
        
        Args:
            opportunity: TaxLossOpportunity to explain
            hypothetical_scenario: Dict with hypothetical parameter changes
        
        Returns:
            Counterfactual explanation text
        """
        if hypothetical_scenario is None:
            hypothetical_scenario = self._generate_default_counterfactual(opportunity)
        
        system_prompt = """You are an expert financial advisor explaining tax-loss harvesting decisions.
Generate a clear, concise counterfactual explanation for why the system's recommendation would change under different conditions.

Format: "If [condition changes], the system would [different recommendation] instead because [reason]."
Keep it to 1-2 sentences maximum."""
        
        user_message = self._build_counterfactual_prompt(opportunity, hypothetical_scenario)
        
        try:
            explanation = self.llm_client.chat_with_system(
                user_message,
                system_prompt,
                temperature=0.5,
                max_tokens=256
            )
            
            return explanation.strip()
        
        except Exception as e:
            self.logger.error(f"Failed to generate counterfactual: {e}")
            return self._generate_fallback_counterfactual(opportunity, hypothetical_scenario)
    
    def _generate_default_counterfactual(
        self,
        opportunity: TaxLossOpportunity
    ) -> Dict[str, Any]:
        """Generate default counterfactual scenario (change tax rate)."""
        return {
            "parameter": "tax_rate",
            "current_value": 0.30,  # Current assumed tax rate
            "hypothetical_value": 0.10,  # Lower tax rate
            "reasoning": "What if the investor is in a lower tax bracket?"
        }
    
    def _build_counterfactual_prompt(
        self,
        opportunity: TaxLossOpportunity,
        scenario: Dict[str, Any]
    ) -> str:
        """Build prompt for counterfactual generation."""
        return f"""Stock: {opportunity.holding.symbol}
Current Unrealized Loss: ${opportunity.unrealized_loss:,.2f}
Loss Percentage: {opportunity.loss_percentage:.1f}%
Current Recommendation: {"HARVEST" if opportunity.eligible_for_harvesting else "HOLD"}
Current Tax Rate: 30%

Hypothetical Scenario:
- Parameter: {scenario.get('parameter')}
- Current: {scenario.get('current_value')}
- Hypothetical: {scenario.get('hypothetical_value')}

Generate a counterfactual explanation."""
    
    def _generate_fallback_counterfactual(
        self,
        opportunity: TaxLossOpportunity,
        scenario: Dict[str, Any]
    ) -> str:
        """Generate fallback counterfactual if LLM fails."""
        param = scenario.get('parameter', 'parameter')
        current = scenario.get('current_value', 'current')
        hypothetical = scenario.get('hypothetical_value', 'hypothetical')
        
        return (
            f"If {param} were {hypothetical} instead of {current}, "
            f"the system would recommend NOT harvesting {opportunity.holding.symbol} "
            f"because the tax savings would be lower."
        )
    
    def explain_batch_recommendations(
        self,
        opportunities: List[TaxLossOpportunity]
    ) -> Dict[str, Any]:
        """
        Generate explanations for a batch of recommendations.
        
        Args:
            opportunities: List of opportunities
        
        Returns:
            Dict with batch explanations and summary
        """
        explanations = []
        shap_summaries = []
        
        for opportunity in opportunities:
            # Get SHAP explanation
            shap_exp = self.get_shap_explanation(opportunity)
            shap_summaries.append(shap_exp)
            
            # Get counterfactual
            counterfactual = self.get_counterfactual_explanation(opportunity)
            
            explanations.append({
                "symbol": opportunity.holding.symbol,
                "recommendation": "HARVEST" if opportunity.eligible_for_harvesting else "HOLD",
                "shap_explanation": shap_exp,
                "counterfactual": counterfactual
            })
        
        # Generate aggregate insights
        aggregate = self._generate_aggregate_insights(explanations)
        
        return {
            "individual_explanations": explanations,
            "aggregate_insights": aggregate,
            "total_opportunities": len(opportunities)
        }
    
    def _generate_aggregate_insights(self, explanations: List[Dict]) -> Dict[str, Any]:
        """Generate aggregate insights from batch explanations."""
        harvested = sum(1 for e in explanations if e["recommendation"] == "HARVEST")
        held = len(explanations) - harvested
        
        # Find most impactful features across all
        feature_impacts = {}
        for exp in explanations:
            for feature_imp in exp["shap_explanation"]["feature_importance"]:
                feat = feature_imp["feature"]
                if feat not in feature_impacts:
                    feature_impacts[feat] = []
                feature_impacts[feat].append(abs(feature_imp["shap_value"]))
        
        avg_impacts = {
            feat: np.mean(impacts)
            for feat, impacts in feature_impacts.items()
        }
        
        top_features = sorted(avg_impacts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "harvest_recommendations": harvested,
            "hold_recommendations": held,
            "most_influential_features": [f[0] for f in top_features],
            "summary": (
                f"Analyzed {len(explanations)} opportunities. "
                f"{harvested} recommended for harvesting, {held} for holding. "
                f"Most influential factor: {top_features[0][0] if top_features else 'N/A'}"
            )
        }
    
    def create_decision_tree_explanation(
        self,
        opportunity: TaxLossOpportunity
    ) -> Dict[str, Any]:
        """
        Create a tree-like explanation showing decision path.
        
        Args:
            opportunity: TaxLossOpportunity to explain
        
        Returns:
            Decision tree structure
        """
        return {
            "root": {
                "question": "Is this a loss position?",
                "answer": opportunity.unrealized_gain_loss < 0,
                "children": [
                    {
                        "question": "Is loss > $100?",
                        "answer": opportunity.unrealized_loss >= 100,
                        "children": [
                            {
                                "question": "Is loss % > 5%?",
                                "answer": opportunity.loss_percentage >= 5,
                                "decision": "HARVEST" if opportunity.eligible_for_harvesting else "NEEDS_REVIEW"
                            }
                        ]
                    }
                ]
            },
            "final_recommendation": "HARVEST" if opportunity.eligible_for_harvesting else "HOLD",
            "confidence": 0.92 if opportunity.eligible_for_harvesting else 0.87
        }


from datetime import datetime
import numpy as np
