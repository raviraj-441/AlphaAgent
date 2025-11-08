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
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from backend.utils.groq_client import GroqLLMClient
from backend.utils.news_fetcher import NewsFetcher

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
    news_context: Dict[str, Any] = field(default_factory=dict)  # News data used in debate


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
    
    def __init__(self, max_rounds: int = 5, api_delay: float = 0.5):
        """
        Initialize multi-turn debate system.
        
        Args:
            max_rounds: Maximum number of debate rounds
            api_delay: Delay in seconds between API calls to avoid rate limits
        """
        self.llm = GroqLLMClient()
        self.news_fetcher = NewsFetcher()  # Initialize news fetcher
        self.max_rounds = max_rounds
        self.api_delay = api_delay  # Delay between API calls
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
        
        system_prompt = f"""You are {agent_role.value} in a portfolio debate.
Goal: {role_info['goal']}
Focus: {role_info['focus']}

Format:
POSITION: [HARVEST/KEEP/PRIORITY_HARVEST]
CONFIDENCE: [0-100]
KEY_POINTS: [3 brief arguments]
REASONING: [Short analysis]"""
        
        # OPTIMIZED: Summarize portfolio instead of listing all details
        total_loss = sum(p.loss_amount for p in positions)
        total_saving = sum(p.tax_saving for p in positions)
        
        # OPTIMIZED: Compact position format
        positions_str = ", ".join([
            f"{p.symbol}(${p.loss_amount/1000:.0f}k loss, {p.holding_days}d)"
            for p in positions
        ])
        
        # OPTIMIZED: Only include last round, not all history
        discussion_context = ""
        if previous_statements:
            last_round = [s for s in previous_statements if s.round_number == round_number - 1]
            if last_round:
                discussion_context = "\n\nLast Round:\n"
                for stmt in last_round:
                    # Only first key point to save tokens
                    point = stmt.key_points[0] if stmt.key_points else "N/A"
                    discussion_context += f"{stmt.agent_role.value}: {stmt.position} ({stmt.confidence:.0f}%) - {point}\n"
        
        user_message = f"""Round {round_number}

Portfolio ({len(positions)} stocks): Total Loss ${total_loss/1000:.0f}k, Tax Save ${total_saving/1000:.0f}k
{positions_str}
{context}{discussion_context}

Your analysis:"""
        
        return system_prompt, user_message
    
    def _get_agent_statement(
        self,
        agent_role: AgentRole,
        positions: List[StockPosition],
        context: str,
        previous_statements: List[AgentStatement],
        round_number: int
    ) -> AgentStatement:
        """Get a statement from an agent using LLM with rate limit protection."""
        system_prompt, user_message = self._create_agent_prompt(
            agent_role, positions, context, previous_statements, round_number
        )
        
        # Add delay to avoid rate limits
        time.sleep(self.api_delay)
        
        response = self.llm.chat_with_system(system_prompt, user_message, max_tokens=500)
        
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
        """Supervisor evaluates if consensus has been reached - OPTIMIZED."""
        
        system_prompt = """You are Debate Supervisor. Evaluate consensus.

Output:
CONSENSUS_STATUS: [Full/Partial/None]
AGREEMENTS: [Brief summary]
DISAGREEMENTS: [Brief summary]
NEXT_STEPS: [If any]"""
        
        # OPTIMIZED: Compact summary
        statements_summary = "\n".join([
            f"{stmt.agent_role.value}: {stmt.position} ({stmt.confidence:.0f}%)"
            for stmt in agent_statements
        ])
        
        user_message = f"""Round {round_number}

{statements_summary}

Consensus?"""
        
        response = self.llm.chat_with_system(system_prompt, user_message, max_tokens=200)
        
        # Parse supervisor feedback
        lines = response.split("\n")
        consensus_status = "Partial"
        agreements = {}
        disagreements = {}
        
        for line in lines:
            if "CONSENSUS_STATUS:" in line:
                consensus_status = line.split(":")[-1].strip()
        
        # OPTIMIZED: Quick analysis by grouping positions
        positions_map = {p.symbol: p for p in positions}
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
        
        # Fetch news context for all symbols in portfolio
        symbols = list(set([p.symbol for p in positions]))
        logger.info(f"Fetching news for {len(symbols)} symbols: {', '.join(symbols)}")
        
        # Get detailed news data for logging
        news_data = self.news_fetcher.get_news_context_for_debate(symbols)
        news_context_string = self.news_fetcher.get_enriched_context(symbols)
        
        # Append news to existing context
        if context:
            context = context + "\n" + news_context_string
        else:
            context = news_context_string
        
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
            time.sleep(self.api_delay)  # Rate limit protection
            consensus_status_str, agreements, disagreements = self._supervisor_evaluate_consensus(
                round_num, positions, round_statements
            )
            
            # Get supervisor feedback
            supervisor_prompt = f"""Round {round_num} - Consensus: {consensus_status_str}

Feedback (brief):"""
            
            time.sleep(self.api_delay)  # Rate limit protection
            supervisor_feedback = self.llm.chat_with_system(
                "You are a debate supervisor. Be very brief.",
                supervisor_prompt,
                max_tokens=150
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
            ended_at=ended_at,
            news_context=news_data  # Include news data in session
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
            "news_context": session.news_context,  # Include news articles and sentiment
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
