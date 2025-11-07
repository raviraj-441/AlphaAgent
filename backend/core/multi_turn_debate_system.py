"""
Multi-Turn Agent Debate System with Supervisor

Agents engage in continuous rounds of debate:
- Each agent responds to others' positions
- Supervisor moderates and evaluates consensus
- Debate continues until all agents are satisfied or max rounds reached
- Final strategy emerges from collaborative discussion
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from backend.utils.groq_client import GroqLLMClient

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the portfolio debate."""
    TAX_OPTIMIZER = "TaxOptimizer"
    RISK_MANAGER = "RiskManager"
    MARKET_STRATEGIST = "MarketStrategist"
    GROWTH_OPTIMIZER = "GrowthOptimizer"
    SUPERVISOR = "Supervisor"


class DebateStatus(Enum):
    """Status of the debate."""
    IN_PROGRESS = "in_progress"
    CONSENSUS_REACHED = "consensus_reached"
    MAX_ROUNDS_REACHED = "max_rounds_reached"
    CONVERGED = "converged"


@dataclass
class StockPosition:
    """A stock position in the portfolio."""
    symbol: str
    quantity: int
    cost_basis: float
    current_price: float
    holding_days: int
    loss_amount: float
    tax_saving: float


@dataclass
class AgentStatement:
    """One agent's statement in a debate round."""
    agent_role: AgentRole
    round_number: int
    statement: str  # The agent's argument
    position: str  # HARVEST, KEEP, or PRIORITY_HARVEST
    confidence: float  # 0-100, how confident is the agent
    key_points: List[str]  # Key arguments
    references: Dict[str, Any] = field(default_factory=dict)  # Refers to other agents


@dataclass
class DebateRound:
    """One round of multi-agent debate."""
    round_number: int
    timestamp: str
    agent_statements: List[AgentStatement]
    supervisor_feedback: str
    consensus_status: str  # "Not reached", "Partial", "Full"
    agreements: Dict[str, List[str]] = field(default_factory=dict)  # Which agents agree
    disagreements: Dict[str, List[str]] = field(default_factory=dict)  # Which agents disagree


@dataclass
class DebateSession:
    """Complete multi-turn debate session."""
    session_id: str
    positions: List[StockPosition]
    rounds: List[DebateRound]
    final_status: DebateStatus
    final_strategy: Dict[str, str]  # symbol -> decision
    total_rounds: int
    supervisor_conclusion: str
    started_at: str
    ended_at: str


class MultiTurnDebateSystem:
    """
    Multi-turn debate system where agents discuss portfolio strategy.
    
    Process:
    1. Each agent provides initial position
    2. Supervisor asks agents to respond to others
    3. Agents refine positions based on discussion
    4. Supervisor evaluates consensus
    5. Repeat until consensus or max rounds
    """
    
    def __init__(self, max_rounds: int = 5):
        """Initialize multi-turn debate system."""
        self.llm = GroqLLMClient()
        self.max_rounds = max_rounds
        self.debate_log_dir = Path("logs/multi_turn_debates")
        self.debate_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Track agent positions across rounds
        self.agent_positions: Dict[AgentRole, str] = {}
        self.agent_statements: List[AgentStatement] = []
        self.debate_rounds: List[DebateRound] = []
    
    def _create_agent_prompt(
        self,
        agent_role: AgentRole,
        positions: List[StockPosition],
        context: str,
        previous_statements: List[AgentStatement],
        round_number: int
    ) -> Tuple[str, str]:
        """Create system and user prompts for an agent."""
        
        role_context = {
            AgentRole.TAX_OPTIMIZER: {
                "goal": "Maximize tax efficiency and tax loss harvesting benefits",
                "focus": "Tax saving amounts, capital gains offset, harvest priority",
                "bias": "Prefers harvesting losses to offset gains"
            },
            AgentRole.RISK_MANAGER: {
                "goal": "Reduce portfolio concentration and risk exposure",
                "focus": "Position sizing, concentration risk, volatility",
                "bias": "Prefers harvesting large losses to reduce risk"
            },
            AgentRole.MARKET_STRATEGIST: {
                "goal": "Optimize entry and exit timing using technical signals",
                "focus": "Market trends, momentum, support/resistance levels",
                "bias": "Prefers keeping stocks with positive momentum"
            },
            AgentRole.GROWTH_OPTIMIZER: {
                "goal": "Preserve long-term growth and capital appreciation",
                "focus": "Company fundamentals, recovery potential, dividend growth",
                "bias": "Prefers keeping quality companies through downturns"
            }
        }
        
        role_info = role_context[agent_role]
        
        system_prompt = f"""You are the {agent_role.value} agent in a portfolio debate.

Your Goal: {role_info['goal']}
Your Focus: {role_info['focus']}

You are part of a multi-agent discussion about which stocks to harvest vs keep.
Be assertive but open to discussion. Respond to other agents' points.
Format your response as:
POSITION: [HARVEST/KEEP/PRIORITY_HARVEST]
CONFIDENCE: [0-100]
KEY_POINTS: [Bullet list of 3-4 key arguments]
RESPONSE_TO_OTHERS: [Address specific points from other agents if applicable]
DETAILED_REASONING: [Your full analysis]"""
        
        positions_str = "\n".join([
            f"  {p.symbol}: Loss ${p.loss_amount:,.0f}, Tax Saving ${p.tax_saving:,.0f}, Days: {p.holding_days}"
            for p in positions
        ])
        
        # Build discussion context
        discussion_context = ""
        if previous_statements:
            discussion_context = "\n\n=== Previous Discussion ===\n"
            for stmt in previous_statements:
                discussion_context += f"\n{stmt.agent_role.value}:\n"
                discussion_context += f"Position: {stmt.position} (Confidence: {stmt.confidence}%)\n"
                discussion_context += f"Arguments: {', '.join(stmt.key_points)}\n"
        
        user_message = f"""Round {round_number} - Portfolio Discussion

Portfolio Positions:
{positions_str}

Additional Context:
{context}

{discussion_context}

Your Response:
Analyze the portfolio and state your position. Address other agents' arguments if applicable.
Remember to be concise but thorough in your reasoning."""
        
        return system_prompt, user_message
    
    def _get_agent_statement(
        self,
        agent_role: AgentRole,
        positions: List[StockPosition],
        context: str,
        previous_statements: List[AgentStatement],
        round_number: int
    ) -> AgentStatement:
        """Get a statement from an agent using LLM."""
        system_prompt, user_message = self._create_agent_prompt(
            agent_role, positions, context, previous_statements, round_number
        )
        
        response = self.llm.chat_with_system(system_prompt, user_message)
        
        # Parse response
        lines = response.split("\n")
        position = "KEEP"
        confidence = 50.0
        key_points = []
        response_to_others = ""
        detailed_reasoning = ""
        
        section = None
        for line in lines:
            if line.startswith("POSITION:"):
                position = line.replace("POSITION:", "").strip().upper()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip().rstrip("%"))
                except:
                    confidence = 50.0
            elif line.startswith("KEY_POINTS:"):
                section = "key_points"
            elif line.startswith("RESPONSE_TO_OTHERS:"):
                section = "response_to_others"
            elif line.startswith("DETAILED_REASONING:"):
                section = "detailed_reasoning"
            elif line.strip() and section:
                if section == "key_points":
                    if line.strip().startswith("-") or line.strip().startswith("•"):
                        key_points.append(line.strip()[1:].strip())
                    elif line.strip():
                        key_points.append(line.strip())
                elif section == "response_to_others":
                    response_to_others += line + "\n"
                elif section == "detailed_reasoning":
                    detailed_reasoning += line + "\n"
        
        statement = AgentStatement(
            agent_role=agent_role,
            round_number=round_number,
            statement=response,
            position=position,
            confidence=confidence,
            key_points=key_points[:4],  # Top 4 points
            references={"response_to_others": response_to_others, "reasoning": detailed_reasoning}
        )
        
        return statement
    
    def _supervisor_evaluate_consensus(
        self,
        round_number: int,
        positions: List[StockPosition],
        agent_statements: List[AgentStatement]
    ) -> Tuple[str, Dict[str, List[str]], Dict[str, List[str]]]:
        """Supervisor evaluates if consensus has been reached."""
        
        system_prompt = """You are the Debate Supervisor.
Evaluate the discussion and determine:
1. What consensus has been reached
2. What still needs discussion
3. Whether agents should continue debating

Be analytical and concise. Output format:
CONSENSUS_STATUS: [Full/Partial/None]
AGREEMENTS: [List what agents agree on]
DISAGREEMENTS: [List what agents still disagree on]
NEXT_STEPS: [What should be discussed next, if any]
SATISFACTION_LEVEL: [0-100, how satisfied are all agents]"""
        
        statements_summary = "\n".join([
            f"\n{stmt.agent_role.value}:\n"
            f"  Position: {stmt.position} (Confidence: {stmt.confidence}%)\n"
            f"  Key Points: {', '.join(stmt.key_points)}"
            for stmt in agent_statements
        ])
        
        user_message = f"""Round {round_number} Discussion Summary:

{statements_summary}

Evaluate:
1. Are the agents reaching consensus?
2. What do they agree on?
3. What conflicts remain?
4. Should they continue debating?"""
        
        response = self.llm.chat_with_system(system_prompt, user_message)
        
        # Parse supervisor feedback
        lines = response.split("\n")
        consensus_status = "Partial"
        agreements = {}
        disagreements = {}
        
        for line in lines:
            if "CONSENSUS_STATUS:" in line:
                consensus_status = line.split(":")[-1].strip()
            elif "AGREEMENTS:" in line or "AGREEMENT:" in line:
                # Parse agreements
                pass
            elif "DISAGREEMENTS:" in line or "DISAGREEMENT:" in line:
                # Parse disagreements
                pass
        
        # Extract from positions
        positions_map = {p.symbol: p for p in positions}
        
        # Group by decision
        by_decision = {}
        for stmt in agent_statements:
            decision = stmt.position
            if decision not in by_decision:
                by_decision[decision] = []
            by_decision[decision].append(stmt.agent_role.value)
        
        # Identify agreements and disagreements
        for symbol in positions_map:
            harvest_agents = [s.agent_role.value for s in agent_statements if s.position in ["HARVEST", "PRIORITY_HARVEST"]]
            keep_agents = [s.agent_role.value for s in agent_statements if s.position == "KEEP"]
            
            if harvest_agents and not keep_agents:
                if symbol not in agreements:
                    agreements[symbol] = []
                agreements[symbol].append(f"All agents agree to HARVEST")
            elif keep_agents and not harvest_agents:
                if symbol not in agreements:
                    agreements[symbol] = []
                agreements[symbol].append(f"All agents agree to KEEP")
            elif harvest_agents and keep_agents:
                if symbol not in disagreements:
                    disagreements[symbol] = []
                disagreements[symbol].append(f"Split decision: {len(harvest_agents)} for harvest, {len(keep_agents)} for keep")
        
        return consensus_status, agreements, disagreements
    
    def debate_portfolio_strategy(
        self,
        positions: List[StockPosition],
        context: str = ""
    ) -> DebateSession:
        """
        Run multi-turn debate until consensus or max rounds.
        
        Args:
            positions: List of stock positions
            context: Additional portfolio context
        
        Returns:
            Complete debate session with all rounds and final strategy
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
        started_at = datetime.now().isoformat()
        
        logger.info(f"Starting multi-turn debate session: {session_id}")
        
        all_agent_statements = []
        debate_rounds = []
        consensus_status = DebateStatus.IN_PROGRESS
        
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"  Round {round_num} - Getting agent statements")
            
            round_statements = []
            
            # Get statements from each agent
            for agent_role in [AgentRole.TAX_OPTIMIZER, AgentRole.RISK_MANAGER, 
                              AgentRole.MARKET_STRATEGIST, AgentRole.GROWTH_OPTIMIZER]:
                statement = self._get_agent_statement(
                    agent_role=agent_role,
                    positions=positions,
                    context=context,
                    previous_statements=all_agent_statements,
                    round_number=round_num
                )
                round_statements.append(statement)
                all_agent_statements.append(statement)
                
                logger.info(f"    {agent_role.value}: {statement.position} (Confidence: {statement.confidence}%)")
            
            # Supervisor evaluates consensus
            logger.info(f"  Round {round_num} - Supervisor evaluation")
            consensus_status_str, agreements, disagreements = self._supervisor_evaluate_consensus(
                round_num, positions, round_statements
            )
            
            # Get supervisor feedback
            supervisor_prompt = f"""You are the Debate Supervisor. Provide brief, actionable feedback.

Round {round_num} Summary:
- Consensus Status: {consensus_status_str}
- Agreements: {agreements}
- Disagreements: {disagreements}

Provide guidance for the next round (or declare consensus reached)."""
            
            supervisor_feedback = self.llm.chat_with_system(
                "You are a portfolio debate supervisor. Be concise and decisive.",
                supervisor_prompt
            )
            
            # Create debate round
            debate_round = DebateRound(
                round_number=round_num,
                timestamp=datetime.now().isoformat(),
                agent_statements=round_statements,
                supervisor_feedback=supervisor_feedback,
                consensus_status=consensus_status_str,
                agreements=agreements,
                disagreements=disagreements
            )
            debate_rounds.append(debate_round)
            
            logger.info(f"    Consensus Status: {consensus_status_str}")
            logger.info(f"    Agreements: {agreements}")
            logger.info(f"    Disagreements: {disagreements}")
            
            # Check if consensus reached
            if consensus_status_str == "Full" or (consensus_status_str == "Partial" and round_num >= 3):
                logger.info(f"  Consensus reached after {round_num} rounds")
                consensus_status = DebateStatus.CONSENSUS_REACHED
                break
            
            if round_num == self.max_rounds:
                logger.info(f"  Max rounds ({self.max_rounds}) reached")
                consensus_status = DebateStatus.MAX_ROUNDS_REACHED
        
        # Determine final strategy
        final_strategy = self._determine_final_strategy(all_agent_statements, positions)
        
        # Get supervisor conclusion
        conclusion_prompt = f"""Portfolio debate complete. 

Final Positions:
{json.dumps({p.symbol: final_strategy.get(p.symbol, 'KEEP') for p in positions}, indent=2)}

Provide a brief executive summary of the debate outcome and final strategy."""
        
        supervisor_conclusion = self.llm.chat_with_system(
            "You are a portfolio debate supervisor providing final recommendations.",
            conclusion_prompt
        )
        
        ended_at = datetime.now().isoformat()
        
        # Create session
        session = DebateSession(
            session_id=session_id,
            positions=positions,
            rounds=debate_rounds,
            final_status=consensus_status,
            final_strategy=final_strategy,
            total_rounds=len(debate_rounds),
            supervisor_conclusion=supervisor_conclusion,
            started_at=started_at,
            ended_at=ended_at
        )
        
        # Save session
        self._save_debate_session(session)
        
        return session
    
    def _determine_final_strategy(
        self,
        all_statements: List[AgentStatement],
        positions: List[StockPosition]
    ) -> Dict[str, str]:
        """Determine final strategy from all agent statements."""
        
        strategy = {}
        
        for position in positions:
            # Count votes for this position
            statements_for_position = [s for s in all_statements if s.position]
            
            harvest_votes = sum(1 for s in statements_for_position if s.position in ["HARVEST", "PRIORITY_HARVEST"])
            keep_votes = sum(1 for s in statements_for_position if s.position == "KEEP")
            
            # Weighted by confidence
            harvest_confidence = sum(s.confidence for s in statements_for_position if s.position in ["HARVEST", "PRIORITY_HARVEST"]) / max(harvest_votes, 1)
            keep_confidence = sum(s.confidence for s in statements_for_position if s.position == "KEEP") / max(keep_votes, 1)
            
            # Determine decision
            if harvest_votes > keep_votes:
                decision = "PRIORITY_HARVEST" if harvest_confidence > 70 else "HARVEST"
            elif keep_votes > harvest_votes:
                decision = "KEEP"
            else:
                # Tie: favor keeping high-conviction positions
                decision = "KEEP" if keep_confidence > harvest_confidence else "HARVEST"
            
            strategy[position.symbol] = decision
        
        return strategy
    
    def _save_debate_session(self, session: DebateSession) -> None:
        """Save complete debate session to JSON."""
        
        session_dict = {
            "session_id": session.session_id,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "total_rounds": session.total_rounds,
            "final_status": session.final_status.value,
            "positions": [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "cost_basis": p.cost_basis,
                    "current_price": p.current_price,
                    "holding_days": p.holding_days,
                    "loss_amount": p.loss_amount,
                    "tax_saving": p.tax_saving
                }
                for p in session.positions
            ],
            "rounds": [
                {
                    "round_number": r.round_number,
                    "timestamp": r.timestamp,
                    "agent_statements": [
                        {
                            "agent": s.agent_role.value,
                            "position": s.position,
                            "confidence": s.confidence,
                            "key_points": s.key_points,
                            "statement": s.statement[:500],  # Truncate for brevity
                            "references": s.references
                        }
                        for s in r.agent_statements
                    ],
                    "supervisor_feedback": r.supervisor_feedback,
                    "consensus_status": r.consensus_status,
                    "agreements": r.agreements,
                    "disagreements": r.disagreements
                }
                for r in session.rounds
            ],
            "final_strategy": session.final_strategy,
            "supervisor_conclusion": session.supervisor_conclusion
        }
        
        file_path = self.debate_log_dir / f"multi_turn_debate_{session.session_id}.json"
        with open(file_path, "w") as f:
            json.dump(session_dict, f, indent=2)
        
        logger.info(f"Saved debate session to {file_path}")
