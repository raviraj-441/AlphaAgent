"""
Tax Loss Identifier Agent - Identifies tax-loss harvesting opportunities using FIFO.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.utils.data_models import PortfolioHolding, TaxLossOpportunity

logger = logging.getLogger(__name__)


class TaxLossIdentifierAgent:
    """
    Identifies tax-loss harvesting opportunities using FIFO accounting method.
    Calculates unrealized losses for tax optimization.
    """
    
    # Configuration
    MIN_LOSS_THRESHOLD = 100  # Minimum loss amount in USD
    MIN_LOSS_PERCENTAGE = 5   # Minimum loss percentage
    HOLDING_PERIOD_DAYS = 30  # Wash sale period (simplified)
    
    def __init__(self):
        """Initialize Tax Loss Identifier Agent."""
        self.logger = logging.getLogger(__name__)
    
    def identify_opportunities(
        self,
        holdings: List[PortfolioHolding],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Identify top tax-loss harvesting opportunities.
        
        Args:
            holdings: List of portfolio holdings
            top_n: Number of top opportunities to return
        
        Returns:
            Dict with opportunities and summary
        """
        self.logger.info(f"Identifying tax-loss opportunities from {len(holdings)} holdings")
        
        opportunities = []
        
        for holding in holdings:
            opportunity = self._evaluate_holding(holding)
            if opportunity:
                opportunities.append(opportunity)
        
        # Sort by loss amount (descending)
        opportunities.sort(key=lambda x: x.unrealized_loss, reverse=True)
        
        # Get top N
        top_opportunities = opportunities[:top_n]
        
        # Calculate summary
        summary = self._calculate_summary(opportunities, top_opportunities)
        
        return {
            "status": "success",
            "message": f"Identified {len(top_opportunities)} top opportunities",
            "opportunities": top_opportunities,
            "total_opportunities": len(opportunities),
            "summary": summary
        }
    
    def _evaluate_holding(self, holding: PortfolioHolding) -> TaxLossOpportunity:
        """Evaluate a single holding for tax-loss opportunity."""
        unrealized_loss = holding.unrealized_gain_loss  # Will be negative if loss
        loss_percentage = (unrealized_loss / holding.cost_basis * 100) if holding.cost_basis > 0 else 0
        
        # Check if eligible for harvesting
        is_eligible = (
            unrealized_loss < 0 and  # Must be a loss
            abs(unrealized_loss) >= self.MIN_LOSS_THRESHOLD and
            abs(loss_percentage) >= self.MIN_LOSS_PERCENTAGE
        )
        
        reason = ""
        if unrealized_loss >= 0:
            reason = "Not a loss - holding is in profit"
        elif abs(unrealized_loss) < self.MIN_LOSS_THRESHOLD:
            reason = f"Loss below threshold (${self.MIN_LOSS_THRESHOLD})"
        elif abs(loss_percentage) < self.MIN_LOSS_PERCENTAGE:
            reason = f"Loss percentage below threshold ({self.MIN_LOSS_PERCENTAGE}%)"
        else:
            reason = "Eligible for tax-loss harvesting"
        
        # Check wash sale period
        holding_days = (datetime.now() - holding.purchase_date).days
        if holding_days < self.HOLDING_PERIOD_DAYS and is_eligible:
            reason = f"Warning: {holding_days} days held (wash sale period: {self.HOLDING_PERIOD_DAYS} days)"
        
        return TaxLossOpportunity(
            holding=holding,
            unrealized_loss=abs(unrealized_loss),
            loss_percentage=abs(loss_percentage),
            eligible_for_harvesting=is_eligible,
            reason=reason
        )
    
    def _calculate_summary(
        self,
        all_opportunities: List[TaxLossOpportunity],
        top_opportunities: List[TaxLossOpportunity]
    ) -> Dict[str, Any]:
        """Calculate summary statistics."""
        total_loss = sum(opp.unrealized_loss for opp in all_opportunities)
        eligible_loss = sum(
            opp.unrealized_loss for opp in all_opportunities
            if opp.eligible_for_harvesting
        )
        top_loss = sum(opp.unrealized_loss for opp in top_opportunities)
        
        eligible_count = sum(
            1 for opp in all_opportunities
            if opp.eligible_for_harvesting
        )
        
        return {
            "total_unrealized_loss": round(total_loss, 2),
            "eligible_loss": round(eligible_loss, 2),
            "top_opportunities_loss": round(top_loss, 2),
            "total_holdings_analyzed": len(all_opportunities),
            "eligible_holdings": eligible_count,
            "ineligible_count": len(all_opportunities) - eligible_count
        }
    
    def calculate_fifo_cost_basis(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate cost basis using FIFO method.
        
        Args:
            transactions: List of transaction dicts with quantity and price
        
        Returns:
            Dict with cost basis calculations
        """
        # Sort by date (FIFO - oldest first)
        sorted_txns = sorted(transactions, key=lambda x: x.get('date', datetime.now()))
        
        total_cost = 0
        total_quantity = 0
        
        for txn in sorted_txns:
            qty = txn.get('quantity', 0)
            price = txn.get('price', 0)
            total_quantity += qty
            total_cost += qty * price
        
        avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
        
        return {
            "total_quantity": total_quantity,
            "total_cost": total_cost,
            "average_cost_per_share": avg_cost
        }
    
    def estimate_tax_impact(
        self,
        harvested_losses: List[TaxLossOpportunity],
        tax_bracket: float = 0.30
    ) -> Dict[str, float]:
        """
        Estimate tax impact of harvested losses.
        
        Args:
            harvested_losses: Losses to be harvested
            tax_bracket: Applicable tax rate (0.0-1.0)
        
        Returns:
            Dict with tax impact details
        """
        total_loss = sum(opp.unrealized_loss for opp in harvested_losses)
        
        # Tax savings = loss * tax_rate
        tax_savings = total_loss * tax_bracket
        
        return {
            "total_harvested_loss": round(total_loss, 2),
            "tax_bracket": tax_bracket,
            "estimated_tax_savings": round(tax_savings, 2),
            "effective_reduction_percent": round(tax_savings / total_loss * 100, 2) if total_loss > 0 else 0
        }


def rank_opportunities(
    opportunities: List[TaxLossOpportunity]
) -> List[TaxLossOpportunity]:
    """
    Rank opportunities by various criteria.
    
    Args:
        opportunities: List of TaxLossOpportunity objects
    
    Returns:
        Ranked list with rank field set
    """
    # Sort by loss amount (descending)
    ranked = sorted(opportunities, key=lambda x: x.unrealized_loss, reverse=True)
    
    # Assign ranks
    for rank, opp in enumerate(ranked, start=1):
        opp.rank = rank
    
    return ranked
