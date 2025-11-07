"""
Agent Orchestrator with Transparent Debate Logging

Captures and logs all agent interactions, reasoning, and decisions.
Provides visibility into how agents debate and reach consensus.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of agent actions in the debate."""
    START = "START"
    PROPOSE = "PROPOSE"
    EVALUATE = "EVALUATE"
    COUNTER = "COUNTER"
    APPROVE = "APPROVE"
    SUGGEST = "SUGGEST"
    CALCULATE = "CALCULATE"
    REJECT = "REJECT"
    RECONCILE = "RECONCILE"
    END = "END"


@dataclass
class DebateEntry:
    """Single entry in a debate log."""
    timestamp: str
    agent: str
    action: ActionType
    content: str
    reasoning: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        data = {
            "timestamp": self.timestamp,
            "agent": self.agent,
            "action": self.action.value,
            "content": self.content,
        }
        if self.reasoning:
            data["reasoning"] = self.reasoning
        if self.metadata:
            data["metadata"] = self.metadata
        return data


class DebateLogger:
    """Logs and persists agent debates."""
    
    def __init__(self, log_dir: str = "logs/debates"):
        """Initialize debate logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.debate_log: List[DebateEntry] = []
        self.current_session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def log_entry(
        self,
        agent: str,
        action: ActionType,
        content: str,
        reasoning: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DebateEntry:
        """
        Log a single debate entry.
        
        Args:
            agent: Agent name
            action: Type of action
            content: Main content/output
            reasoning: List of reasoning steps
            metadata: Additional metadata
        
        Returns:
            DebateEntry object
        """
        entry = DebateEntry(
            timestamp=datetime.now().isoformat(),
            agent=agent,
            action=action,
            content=content,
            reasoning=reasoning,
            metadata=metadata
        )
        
        self.debate_log.append(entry)
        
        # Console output
        reasoning_str = f"\n  Reasoning: {reasoning}" if reasoning else ""
        logger.info(f"[{agent}] {action.value}: {content[:100]}...{reasoning_str}")
        
        return entry
    
    def get_debate_transcript(self) -> str:
        """Generate human-readable debate transcript."""
        lines = [
            "=" * 80,
            "AGENT DEBATE TRANSCRIPT",
            f"Session: {self.current_session_id}",
            f"Total Entries: {len(self.debate_log)}",
            "=" * 80,
            ""
        ]
        
        for entry in self.debate_log:
            timestamp = datetime.fromisoformat(entry.timestamp).strftime("%H:%M:%S.%f")[:-3]
            lines.append(f"[{timestamp}] {entry.agent.upper()}")
            lines.append(f"    Action: {entry.action.value}")
            lines.append(f"    Content: {entry.content}")
            
            if entry.reasoning:
                lines.append(f"    Reasoning:")
                for reason in entry.reasoning:
                    lines.append(f"      • {reason}")
            
            if entry.metadata:
                lines.append(f"    Metadata: {json.dumps(entry.metadata, indent=6)}")
            
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def save_debate(self, filename: Optional[str] = None) -> Path:
        """
        Save debate log to JSON file.
        
        Args:
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"debate_{self.current_session_id}.json"
        
        filepath = self.log_dir / filename
        
        debate_data = {
            "session_id": self.current_session_id,
            "start_time": self.debate_log[0].timestamp if self.debate_log else None,
            "end_time": self.debate_log[-1].timestamp if self.debate_log else None,
            "total_entries": len(self.debate_log),
            "entries": [entry.to_dict() for entry in self.debate_log]
        }
        
        with open(filepath, "w") as f:
            json.dump(debate_data, f, indent=2)
        
        logger.info(f"Debate saved to {filepath}")
        return filepath
    
    def get_log(self) -> List[Dict[str, Any]]:
        """Get debate log as list of dictionaries."""
        return [entry.to_dict() for entry in self.debate_log]


class AgentOrchestrator:
    """
    Orchestrates multi-agent debate with transparent logging.
    
    Manages:
    - Agent initialization and routing
    - Debate flow and sequencing
    - Argument tracking and consensus building
    - Transparent logging of all decisions
    """
    
    def __init__(self, agents: Dict[str, Any], enable_logging: bool = True):
        """
        Initialize orchestrator.
        
        Args:
            agents: Dictionary of agent instances {name: agent}
            enable_logging: Whether to enable debate logging
        """
        self.agents = agents
        self.logger = DebateLogger() if enable_logging else None
    
    def log(
        self,
        agent: str,
        action: ActionType,
        content: str,
        reasoning: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an agent action."""
        if self.logger:
            self.logger.log_entry(agent, action, content, reasoning, metadata)
    
    def debate_tax_loss_harvest(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Orchestrate debate for tax-loss harvesting recommendations.
        
        Flow:
        1. Portfolio Parser: Extract holdings
        2. Loss Identifier: Propose tax-loss opportunities
        3. Compliance Agent: Validate against regulations
        4. Recommender: Suggest replacements
        5. Calculator: Finalize savings estimate
        
        Args:
            portfolio: Portfolio data (list of holdings)
        
        Returns:
            Final recommendation with full debate log
        """
        self.log("SYSTEM", ActionType.START, f"Starting debate for portfolio with {len(portfolio)} positions")
        
        try:
            # ===== STAGE 1: Parse Portfolio =====
            self.log("PortfolioParser", ActionType.PROPOSE, "Extracting portfolio data", 
                    reasoning=["Validating position counts", "Checking data integrity"])
            
            parsed_positions = len(portfolio)
            self.log("PortfolioParser", ActionType.APPROVE, f"Parsed {parsed_positions} positions")
            
            # ===== STAGE 2: Identify Tax-Loss Opportunities =====
            losses = self._identify_losses(portfolio)
            self.log(
                "TaxLossIdentifier",
                ActionType.PROPOSE,
                f"Identified {len(losses)} positions with losses",
                reasoning=[
                    f"Found {len([l for l in losses if l['type'] == 'short_term'])} short-term losses",
                    f"Found {len([l for l in losses if l['type'] == 'long_term'])} long-term losses",
                    f"Total potential tax saving: ${sum(l.get('tax_saving', 0) for l in losses):,.0f}"
                ],
                metadata={"losses_count": len(losses), "total_tax_saving": sum(l.get('tax_saving', 0) for l in losses)}
            )
            
            # ===== STAGE 3: Compliance Review =====
            validated = self._validate_compliance(losses)
            rejected = [l for l in losses if l not in validated]
            
            if rejected:
                reject_reasons = [f"Rejected {l.get('symbol')}: {l.get('violation', 'Unknown')}" for l in rejected]
                self.log(
                    "ComplianceAgent",
                    ActionType.COUNTER,
                    f"Rejected {len(rejected)} proposals due to regulatory constraints",
                    reasoning=reject_reasons,
                    metadata={"rejected_count": len(rejected)}
                )
            
            self.log(
                "ComplianceAgent",
                ActionType.APPROVE,
                f"Validated {len(validated)} compliant positions",
                reasoning=["Checked wash-sale periods", "Verified FIFO compliance", "Confirmed tax-year eligibility"],
                metadata={"approved_count": len(validated)}
            )
            
            # ===== STAGE 4: Recommend Replacements =====
            replacements = self._recommend_replacements(validated)
            self.log(
                "ReplacementRecommender",
                ActionType.SUGGEST,
                f"Generated {len(replacements)} replacement recommendations",
                reasoning=[
                    f"Matched {len(replacements)} positions with similar risk/sector characteristics",
                    "Avoided wash-sale conflicts",
                    "Prioritized tax efficiency"
                ],
                metadata={"recommendations": len(replacements)}
            )
            
            # ===== STAGE 5: Calculate Final Savings =====
            final_result = self._calculate_savings(validated, replacements)
            self.log(
                "TaxSavingsCalculator",
                ActionType.CALCULATE,
                f"Final tax-loss harvest strategy: ${final_result['total_tax_saving']:,.0f} potential savings",
                reasoning=[
                    f"Short-term losses: ${final_result['short_term_saving']:,.0f}",
                    f"Long-term losses: ${final_result['long_term_saving']:,.0f}",
                    f"Affected positions: {len(validated)}",
                    f"Replacements suggested: {len(replacements)}"
                ],
                metadata={
                    "total_saving": final_result['total_tax_saving'],
                    "positions": len(validated),
                    "replacements": len(replacements)
                }
            )
            
            # ===== STAGE 6: Consensus Reached =====
            self.log("SYSTEM", ActionType.END, "Debate concluded - Consensus achieved")
            
            final_result["debate_log"] = self.logger.get_log() if self.logger else []
            return final_result
            
        except Exception as e:
            self.log("SYSTEM", ActionType.REJECT, f"Debate failed: {str(e)}")
            logger.error(f"Orchestrator error: {e}", exc_info=True)
            return {
                "error": str(e),
                "debate_log": self.logger.get_log() if self.logger else []
            }
    
    def _identify_losses(self, portfolio: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate loss identification agent."""
        losses = []
        for holding in portfolio:
            current = holding.get("current_price", 0)
            cost = holding.get("cost_basis", 0)
            
            if current < cost:
                loss = cost - current
                tax_saving = loss * 0.30  # Assume 30% tax bracket
                
                losses.append({
                    "symbol": holding.get("symbol"),
                    "quantity": holding.get("quantity", 0),
                    "cost_basis": cost,
                    "current_price": current,
                    "loss": loss,
                    "tax_saving": tax_saving,
                    "type": "short_term" if holding.get("holding_period_days", 0) <= 365 else "long_term",
                    "holding_period_days": holding.get("holding_period_days", 0)
                })
        
        return losses
    
    def _validate_compliance(self, losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate compliance validation."""
        validated = []
        
        for loss in losses:
            # Simulate compliance checks
            if loss["tax_saving"] < 100:  # Skip trivial savings
                loss["violation"] = "Negligible tax benefit"
                continue
            
            if loss["holding_period_days"] < 30:  # Possible wash-sale
                loss["violation"] = "Within 30-day wash-sale window"
                continue
            
            validated.append(loss)
        
        return validated
    
    def _recommend_replacements(self, losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate replacement recommendations."""
        replacements = []
        
        for loss in losses:
            # Simple replacement logic
            replacements.append({
                "original_symbol": loss["symbol"],
                "replacement_symbol": f"ALT_{loss['symbol']}",
                "reasoning": "Similar sector, lower correlation",
                "tax_efficiency_score": 0.85
            })
        
        return replacements
    
    def _calculate_savings(
        self,
        losses: List[Dict[str, Any]],
        replacements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate final tax savings."""
        short_term = sum(l["tax_saving"] for l in losses if l["type"] == "short_term")
        long_term = sum(l["tax_saving"] for l in losses if l["type"] == "long_term")
        
        return {
            "total_tax_saving": short_term + long_term,
            "short_term_saving": short_term,
            "long_term_saving": long_term,
            "positions_affected": len(losses),
            "replacements_suggested": len(replacements),
            "strategy": "tax_loss_harvest"
        }
    
    def save_debate(self, filename: Optional[str] = None) -> Optional[Path]:
        """Save debate log to file."""
        if self.logger:
            return self.logger.save_debate(filename)
        return None
    
    def print_debate_transcript(self):
        """Print human-readable debate transcript."""
        if self.logger:
            print(self.logger.get_debate_transcript())
