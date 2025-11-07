# Multi-Turn Agent Debate System

## Overview

The Multi-Turn Agent Debate System enables continuous, collaborative discussion between portfolio optimization agents with a supervisor orchestrating the conversation until consensus is reached.

## Architecture

### Components

```
MultiTurnDebateSystem
├── Agent Roles
│   ├── TaxOptimizer
│   ├── RiskManager
│   ├── MarketStrategist
│   └── GrowthOptimizer
├── Supervisor
│   ├── Evaluates consensus
│   ├── Provides feedback
│   └── Determines next steps
└── Debate Mechanism
    ├── Multi-round discussion
    ├── Inter-agent responses
    └── Confidence-weighted voting
```

### Key Features

1. **Multi-Turn Discussion Loop**
   - Agents see previous statements from peers
   - Each agent refines their position based on discussion
   - Iterative refinement until convergence

2. **Supervisor Orchestration**
   - Evaluates consensus status (Full/Partial/None)
   - Identifies agreements and disagreements
   - Provides guidance for next round
   - Declares debate conclusion

3. **Confidence-Weighted Voting**
   - Agent positions include confidence scores (0-100%)
   - Final strategy determined by:
     - Vote counts
     - Confidence levels
     - Agent specialization

4. **Comprehensive Debate Logging**
   - Each round captured with all statements
   - Supervisor feedback recorded
   - Agreement/disagreement tracking
   - JSON persistence for audit trail

## How It Works

### Initialization

```python
from backend.core.multi_turn_debate_system import MultiTurnDebateSystem, StockPosition

# Create debate system with max 5 rounds
debate_system = MultiTurnDebateSystem(max_rounds=5)

# Prepare portfolio positions
positions = [
    StockPosition(
        symbol="RELIANCE",
        quantity=100,
        cost_basis=2000,
        current_price=1000,
        holding_days=603,
        loss_amount=100000,
        tax_saving=30000
    ),
    # ... more positions
]
```

### Running a Debate

```python
# Start debate
session = debate_system.debate_portfolio_strategy(
    positions=positions,
    context="Portfolio context and constraints"
)

# Results
print(f"Final Status: {session.final_status}")
print(f"Total Rounds: {session.total_rounds}")
print(f"Strategy: {session.final_strategy}")
```

### Debate Flow

**Round 1-N:**

1. **Agent Statements** (TaxOptimizer → RiskManager → MarketStrategist → GrowthOptimizer)
   - Each agent sees previous agents' positions
   - Provides position: HARVEST, KEEP, or PRIORITY_HARVEST
   - Includes confidence score (0-100%)
   - Provides key arguments
   - May respond to other agents' points

2. **Supervisor Evaluation**
   - Evaluates consensus status:
     - `Full`: All agents agree
     - `Partial`: Majority agreement with dissent
     - `None`: Strong disagreement
   - Identifies agreements (e.g., "All agree to KEEP")
   - Identifies disagreements (e.g., "Split: 2 HARVEST vs 2 KEEP")
   - Provides feedback and guidance

3. **Consensus Check**
   - If consensus reached → Debate ends
   - If max rounds reached → Debate ends
   - Otherwise → Continue to next round

## Agent Roles

### TaxOptimizer
- **Goal**: Maximize tax efficiency
- **Focus**: Tax saving amounts, capital gains offset
- **Bias**: Prefers harvesting losses

### RiskManager
- **Goal**: Reduce portfolio concentration and risk
- **Focus**: Position sizing, concentration risk, volatility
- **Bias**: Prefers harvesting large losses

### MarketStrategist
- **Goal**: Optimize entry/exit timing
- **Focus**: Market trends, momentum, technical signals
- **Bias**: Prefers keeping stocks with positive momentum

### GrowthOptimizer
- **Goal**: Preserve long-term growth potential
- **Focus**: Company fundamentals, recovery potential
- **Bias**: Prefers keeping quality companies through downturns

## Output Format

### Final Strategy

```python
session.final_strategy = {
    "RELIANCE": "KEEP",
    "INFY": "HARVEST",
    "HDFC": "PRIORITY_HARVEST"
}
```

### Debate Session Structure

```json
{
  "session_id": "20251108_024751123",
  "started_at": "2025-11-08T02:47:51",
  "ended_at": "2025-11-08T02:52:15",
  "total_rounds": 3,
  "final_status": "consensus_reached",
  "positions": [...],
  "rounds": [
    {
      "round_number": 1,
      "agent_statements": [
        {
          "agent": "TaxOptimizer",
          "position": "HARVEST",
          "confidence": 85.0,
          "key_points": ["High tax saving", "Offset gains", "Low tax bracket"]
        }
      ],
      "supervisor_feedback": "...",
      "consensus_status": "None",
      "agreements": {},
      "disagreements": {"RELIANCE": ["Split decision"]}
    },
    {
      "round_number": 2,
      "agent_statements": [...],
      "supervisor_feedback": "Moving toward partial consensus...",
      "consensus_status": "Partial"
    },
    {
      "round_number": 3,
      "agent_statements": [...],
      "supervisor_feedback": "Full consensus reached",
      "consensus_status": "Full"
    }
  ],
  "final_strategy": {...},
  "supervisor_conclusion": "All agents agree to KEEP positions for growth..."
}
```

## Configuration

### Max Rounds

Control how long debate can continue:

```python
# Debate for max 5 rounds
debate_system = MultiTurnDebateSystem(max_rounds=5)

# Shorter debate
debate_system = MultiTurnDebateSystem(max_rounds=3)
```

### Consensus Criteria

- **Early Exit**: If "Full" consensus reached before max rounds
- **Partial Exit**: After round 3 with "Partial" consensus
- **Max Exit**: Always exit after max_rounds

## Testing

Run the test to see multi-turn debate in action:

```bash
python test_multi_turn_debate.py
```

Example output:
```
===========================
MULTI-TURN AGENT DEBATE
===========================

[PORTFOLIO POSITIONS]
  RELIANCE: Loss 100,000 | Tax Saving 30,000 | Days: 603
  INFY: Loss 12,500 | Tax Saving 3,750 | Days: 280
  HDFC: Loss 60,000 | Tax Saving 18,000 | Days: 450

[STARTING MULTI-TURN DEBATE...]

ROUND 1
-------
Consensus Status: None
Agreements: {}
Disagreements: {"RELIANCE": ["Split: 2 HARVEST vs 2 KEEP"]}

[AGENT] TaxOptimizer
  Position: HARVEST (Confidence: 85%)
  Key Points:
    - Maximum tax saving of 30,000
    - Offset capital gains
    - No wash-sale concerns for 603 days

[AGENT] RiskManager
  Position: PRIORITY_HARVEST (Confidence: 78%)
  Key Points:
    - Concentration risk on RELIANCE at 58%
    - Reduce exposure to single stock
    - Rebalance portfolio

...

FINAL CONSENSUS STRATEGY
------------------------
RELIANCE: KEEP
INFY: HARVEST
HDFC: KEEP

[SUPERVISOR CONCLUSION]
All agents agree that growth potential and timing concerns override tax optimization for blue-chip stocks like RELIANCE and HDFC. However, INFY should be harvested due to lower growth outlook and tax benefits.
```

## Logging and Persistence

All debate sessions are saved to:
```
logs/multi_turn_debates/multi_turn_debate_YYYYMMDD_HHMMSS.json
```

Access debate history:
```bash
# View latest debate
cat logs/multi_turn_debates/multi_turn_debate_20251108_024751.json | jq

# Summary of all debates
ls -lh logs/multi_turn_debates/
```

## Integration with Portfolio Analysis

The multi-turn debate system complements the existing portfolio analysis:

1. **Individual Stock Analysis** → LLM Debate System
   - Single stock news-based debate
   - 4 agents discuss one position

2. **Portfolio Strategy** → Multi-Turn Debate System
   - Cross-stock comparison
   - Iterative refinement
   - Supervisor orchestration
   - Consensus-driven decisions

## Advanced Usage

### Custom Agent Roles

Extend with additional agents:

```python
class DebtAnalyst(AgentRole):
    """Analyze debt ratios and financial health"""
    def __init__(self):
        self.focus = "Debt levels, interest coverage, credit ratings"
```

### Real-Time Monitoring

Monitor ongoing debates:

```python
# Get current round status
for round_data in session.rounds:
    print(f"Round {round_data.round_number}: {round_data.consensus_status}")
    
# Track agent evolution
for agent_role in [TaxOptimizer, RiskManager, ...]:
    statements = [s for s in all_statements if s.agent_role == agent_role]
    print(f"{agent_role}: Position evolution: {[s.position for s in statements]}")
```

### Debate Analytics

Analyze debate patterns:

```python
# Calculate consensus stability
agreement_rate = len(agreements) / total_positions

# Track agent confidence trends
confidence_evolution = {
    agent: [stmt.confidence for stmt in agent_statements]
    for agent, agent_statements in grouped_by_agent.items()
}

# Identify swing factors
swing_factors = identify_positions_that_changed_agent_minds()
```

## Performance Notes

- **Round Duration**: ~30-60 seconds per round (LLM inference + supervisor evaluation)
- **Token Usage**: ~1,000-1,500 tokens per round per agent
- **Max Recommended Positions**: 10-15 (beyond that, debate becomes verbose)
- **Max Recommended Rounds**: 5-7 (diminishing returns on refinement)

## Future Enhancements

1. **Parallel Agent Discussion**
   - Agents respond simultaneously instead of sequentially
   - Faster consensus reaching

2. **Debate Metrics**
   - Agreement rate tracking
   - Confidence convergence analysis
   - Swing factor identification

3. **Scenario Analysis**
   - "What if we ignore growth?" → Show harvest scenario
   - "What if we prioritize risk?" → Show risk-based scenario
   - Compare outcomes across scenarios

4. **Long-Form Debates**
   - Enable debates to continue beyond consensus
   - Explore alternative strategies
   - "Devil's Advocate" mode

5. **External Agent Integration**
   - Compliance officer agent
   - Dividend specialist agent
   - ESG analyst agent

## Related Files

- `backend/core/multi_turn_debate_system.py` - Main system implementation
- `test_multi_turn_debate.py` - Test and demo script
- `backend/core/portfolio_debate_system.py` - Single-round portfolio debate (predecessor)
- `backend/core/llm_debate_system.py` - Individual stock debate system

## References

- [Agent Orchestration Patterns](AGENT_DEBATE_SYSTEM.md)
- [Portfolio Analysis Framework](QUICKSTART.md)
- [LLM Integration](backend/utils/groq_client.py)
