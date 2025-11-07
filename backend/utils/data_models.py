"""
Data models for tax-loss harvesting system.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TransactionStatus(str, Enum):
    """Status of a transaction."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class ComplianceStatus(str, Enum):
    """Compliance status of a transaction."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"


@dataclass
class PortfolioHolding:
    """Represents a single stock holding in portfolio."""
    stock_name: str
    symbol: str
    quantity: float
    purchase_date: datetime
    purchase_price: float
    current_price: float
    asset_class: str = "equity"
    
    @property
    def cost_basis(self) -> float:
        """Total cost basis."""
        return self.quantity * self.purchase_price
    
    @property
    def current_value(self) -> float:
        """Current market value."""
        return self.quantity * self.current_price
    
    @property
    def unrealized_gain_loss(self) -> float:
        """Unrealized gain/loss."""
        return self.current_value - self.cost_basis


@dataclass
class TaxLossOpportunity:
    """Represents a tax-loss harvesting opportunity."""
    holding: PortfolioHolding
    unrealized_loss: float
    loss_percentage: float
    eligible_for_harvesting: bool
    reason: str = ""
    rank: int = 0


@dataclass
class ComplianceCheckResult:
    """Result of compliance check."""
    is_compliant: bool
    status: ComplianceStatus
    regulation_references: List[str] = field(default_factory=list)
    explanation: str = ""
    risk_level: str = "low"  # low, medium, high
    suggested_fix: Optional[str] = None


@dataclass
class ReplacementSecurity:
    """Represents a replacement security suggestion."""
    original_symbol: str
    recommended_symbol: str
    correlation_score: float
    semantic_similarity: float = 0.0
    reason: str = ""
    risk_profile_match: float = 1.0


@dataclass
class TaxSavingsCalculation:
    """Tax savings calculation result."""
    transaction_count: int
    total_harvested_loss: float
    applicable_tax_rate: float
    immediate_tax_savings: float
    projected_10yr_value: float
    projected_value_increase: float
    monte_carlo_runs: int = 1000
    assumptions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentProposal:
    """Proposal from an agent during negotiation."""
    agent_name: str
    proposal_type: str  # "approve", "reject", "modify"
    content: Dict[str, Any]
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    iteration: int = 0


@dataclass
class NegotiationRound:
    """Single round of negotiation."""
    iteration: int
    proposals: List[AgentProposal] = field(default_factory=list)
    consensus_reached: bool = False
    summary: str = ""


@dataclass
class FinalRecommendation:
    """Final recommendation from orchestrator."""
    session_id: str
    user_id: Optional[str] = None
    portfolio_summary: Dict[str, Any] = field(default_factory=dict)
    tax_loss_opportunities: List[TaxLossOpportunity] = field(default_factory=list)
    compliance_results: List[ComplianceCheckResult] = field(default_factory=list)
    recommended_replacements: List[ReplacementSecurity] = field(default_factory=list)
    tax_savings: Optional[TaxSavingsCalculation] = None
    negotiation_history: List[NegotiationRound] = field(default_factory=list)
    final_consensus: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
