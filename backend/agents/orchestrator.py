"""
Multi-Agent Orchestrator - Coordinates agents and manages negotiation loop.
"""

import logging
import uuid
from typing import List, Dict, Any
from datetime import datetime

from backend.utils.data_models import (
    FinalRecommendation, NegotiationRound, AgentProposal, PortfolioHolding,
    TaxLossOpportunity
)
from backend.utils.groq_client import GroqLLMClient
from backend.agents.portfolio_parser import PortfolioParserAgent
from backend.agents.tax_loss_identifier import TaxLossIdentifierAgent
from backend.agents.compliance_checker import RegulatoryComplianceAgent
from backend.agents.replacement_recommender import ReplacementRecommenderAgent
from backend.agents.tax_savings_calculator import TaxSavingsCalculatorAgent
from backend.agents.explainability_agent import ExplainabilityAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates multi-agent system for tax-loss harvesting optimization.
    Manages agent coordination and negotiation loops.
    """
    
    MAX_ITERATIONS = 3
    
    def __init__(self, llm_client: GroqLLMClient = None):
        """
        Initialize Agent Orchestrator.
        
        Args:
            llm_client: GroqLLMClient instance. If None, creates one from API key.
        """
        if llm_client is None:
            llm_client = GroqLLMClient()
        
        self.llm_client = llm_client
        
        # Initialize agents
        self.portfolio_parser = PortfolioParserAgent(llm_client)
        self.tax_loss_identifier = TaxLossIdentifierAgent()
        self.compliance_checker = RegulatoryComplianceAgent(llm_client)
        self.replacement_recommender = ReplacementRecommenderAgent(llm_client)
        self.tax_savings_calculator = TaxSavingsCalculatorAgent()
        self.explainability_agent = ExplainabilityAgent(llm_client)
        
        self.logger = logging.getLogger(__name__)
    
    def orchestrate(
        self,
        portfolio_file_data: bytes,
        file_type: str,
        session_id: str = None,
        user_id: str = None,
        annual_income: float = 400000,
        tax_rate: float = None
    ) -> FinalRecommendation:
        """
        Orchestrate full multi-agent pipeline for tax-loss optimization.
        
        Args:
            portfolio_file_data: Binary portfolio file data
            file_type: Type of file (csv, pdf, excel)
            session_id: Session ID for tracking
            user_id: User ID
            annual_income: User's annual income
            tax_rate: Override tax rate (if None, estimated from income)
        
        Returns:
            FinalRecommendation with complete analysis
        """
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        self.logger.info(f"Starting orchestration for session {session_id}")
        
        # Step 1: Parse portfolio
        parse_result = self.portfolio_parser.parse_portfolio(portfolio_file_data, file_type)
        
        if parse_result.get("status") != "success":
            self.logger.error(f"Portfolio parsing failed: {parse_result.get('message')}")
            return self._create_error_recommendation(
                session_id, user_id, parse_result.get("message")
            )
        
        holdings = parse_result.get("holdings", [])
        
        if not holdings:
            return self._create_error_recommendation(
                session_id, user_id, "No holdings found in portfolio"
            )
        
        # Step 2: Identify tax-loss opportunities
        identification_result = self.tax_loss_identifier.identify_opportunities(holdings)
        opportunities = identification_result.get("opportunities", [])
        
        # Start negotiation
        negotiation_history = []
        final_opportunities = opportunities[:5]  # Consider top 5 for negotiation
        
        for iteration in range(self.MAX_ITERATIONS):
            self.logger.info(f"Negotiation iteration {iteration + 1}")
            
            round_proposals = []
            consensus_reached = True
            
            # Step 3: Compliance check
            compliance_results = self.compliance_checker.check_batch_compliance(final_opportunities)
            
            compliance_proposal = AgentProposal(
                agent_name="ComplianceAgent",
                proposal_type="review",
                content={
                    "compliant_opportunities": sum(1 for r in compliance_results if r.is_compliant),
                    "non_compliant_opportunities": sum(1 for r in compliance_results if not r.is_compliant),
                    "results": [{"symbol": opp.holding.symbol, "compliant": cr.is_compliant}
                               for opp, cr in zip(final_opportunities, compliance_results)]
                },
                reasoning=f"Compliance check completed. {sum(1 for r in compliance_results if r.is_compliant)}/{len(compliance_results)} compliant.",
                iteration=iteration + 1
            )
            round_proposals.append(compliance_proposal)
            
            # Filter to compliant opportunities for next steps
            compliant_opps = [
                opp for opp, cr in zip(final_opportunities, compliance_results)
                if cr.is_compliant
            ]
            
            if not compliant_opps:
                consensus_reached = False
                break
            
            # Step 4: Get replacements
            recommendations_dict = self.replacement_recommender.batch_recommend(compliant_opps)
            
            replacement_proposal = AgentProposal(
                agent_name="ReplacementAgent",
                proposal_type="approve",
                content={
                    "recommendations_provided": len(recommendations_dict),
                    "symbols_with_replacements": list(recommendations_dict.keys())
                },
                reasoning=f"Identified replacements for {len(recommendations_dict)} opportunities.",
                iteration=iteration + 1
            )
            round_proposals.append(replacement_proposal)
            
            # Step 5: Calculate savings
            savings_calc = self.tax_savings_calculator.calculate_savings(
                compliant_opps,
                applicable_tax_rate=tax_rate,
                annual_income=annual_income
            )
            
            savings_proposal = AgentProposal(
                agent_name="SavingsAgent",
                proposal_type="approve",
                content={
                    "immediate_tax_savings": round(savings_calc.immediate_tax_savings, 2),
                    "projected_10yr_value": round(savings_calc.projected_10yr_value, 2),
                    "transaction_count": savings_calc.transaction_count
                },
                reasoning=f"Calculated immediate savings: ${savings_calc.immediate_tax_savings:,.2f}",
                iteration=iteration + 1
            )
            round_proposals.append(savings_proposal)
            
            # Create negotiation round
            round_obj = NegotiationRound(
                iteration=iteration + 1,
                proposals=round_proposals,
                consensus_reached=consensus_reached
            )
            negotiation_history.append(round_obj)
            
            # If all agents approved, break
            if all(p.proposal_type == "approve" for p in round_proposals):
                break
        
        # Build final recommendation
        final_rec = FinalRecommendation(
            session_id=session_id,
            user_id=user_id,
            portfolio_summary={
                "total_holdings": len(holdings),
                "opportunities_identified": len(opportunities),
                "compliant_opportunities": len(compliant_opps),
                "total_unrealized_losses": sum(h.unrealized_gain_loss for h in holdings if h.unrealized_gain_loss < 0)
            },
            tax_loss_opportunities=compliant_opps,
            compliance_results=compliance_results[:len(compliant_opps)] if 'compliance_results' in locals() else [],
            recommended_replacements=sum(recommendations_dict.values(), []) if 'recommendations_dict' in locals() else [],
            tax_savings=savings_calc if 'savings_calc' in locals() else None,
            negotiation_history=negotiation_history,
            final_consensus=len(compliant_opps) > 0
        )
        
        self.logger.info(f"Orchestration complete for session {session_id}")
        
        return final_rec
    
    def _create_error_recommendation(
        self,
        session_id: str,
        user_id: str,
        error_message: str
    ) -> FinalRecommendation:
        """Create error recommendation."""
        return FinalRecommendation(
            session_id=session_id,
            user_id=user_id,
            portfolio_summary={"error": error_message},
            final_consensus=False
        )
    
    def get_negotiation_flow(
        self,
        recommendation: FinalRecommendation
    ) -> str:
        """
        Get human-readable negotiation flow visualization.
        
        Args:
            recommendation: FinalRecommendation with negotiation history
        
        Returns:
            Readable summary of negotiation
        """
        flow_text = f"Session: {recommendation.session_id}\n"
        flow_text += f"Opportunities Identified: {recommendation.portfolio_summary.get('opportunities_identified', 0)}\n\n"
        
        for round_obj in recommendation.negotiation_history:
            flow_text += f"Iteration {round_obj.iteration}:\n"
            
            for proposal in round_obj.proposals:
                flow_text += (
                    f"  - {proposal.agent_name}: {proposal.proposal_type.upper()} - "
                    f"{proposal.reasoning}\n"
                )
            
            flow_text += f"  Consensus: {'REACHED' if round_obj.consensus_reached else 'PENDING'}\n\n"
        
        flow_text += f"Final Status: {'CONSENSUS REACHED' if recommendation.final_consensus else 'REVIEW REQUIRED'}\n"
        
        return flow_text


def visualize_negotiation_flow(proposals: List[Dict[str, Any]]) -> str:
    """
    Visualize negotiation flow as readable text.
    
    Args:
        proposals: List of proposal dicts
    
    Returns:
        Readable negotiation flow summary
    """
    if not proposals:
        return "No negotiation data available."
    
    summary = "Negotiation Flow Summary:\n"
    summary += "=" * 50 + "\n\n"
    
    # Group by iteration
    iterations = {}
    for proposal in proposals:
        it = proposal.get("iteration", 1)
        if it not in iterations:
            iterations[it] = []
        iterations[it].append(proposal)
    
    for iteration in sorted(iterations.keys()):
        summary += f"Iteration {iteration}:\n"
        
        for proposal in iterations[iteration]:
            agent = proposal.get("agent_name", "Unknown")
            status = proposal.get("proposal_type", "unknown")
            reasoning = proposal.get("reasoning", "No reasoning provided")
            
            summary += f"  {agent}: {status.upper()}\n"
            summary += f"    Reason: {reasoning}\n"
        
        summary += "\n"
    
    return summary
