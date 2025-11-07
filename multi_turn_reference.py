#!/usr/bin/env python3
"""
Multi-Turn Debate System - Quick Reference

This script shows how agents interact through multiple rounds of discussion
until reaching consensus, with a supervisor orchestrating the debate.
"""

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                  MULTI-TURN AGENT DEBATE SYSTEM                              ║
║                          Quick Reference                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

## WHAT IT DOES

Enables portfolio optimization agents to have continuous discussions where:
  ✓ Agents see and respond to each other's positions
  ✓ Positions can change based on peer arguments
  ✓ Supervisor evaluates consensus after each round
  ✓ Debate continues until consensus or max rounds
  ✓ Final strategy emerges from collaborative discussion

## THE AGENTS

1. TaxOptimizer
   └─ Goal: Maximize tax efficiency and tax loss harvesting
   └─ Bias: Prefers harvesting losses

2. RiskManager
   └─ Goal: Reduce portfolio concentration and risk
   └─ Bias: Prefers harvesting large losses

3. MarketStrategist
   └─ Goal: Optimize entry/exit timing using technical signals
   └─ Bias: Prefers keeping stocks with positive momentum

4. GrowthOptimizer
   └─ Goal: Preserve long-term growth and capital appreciation
   └─ Bias: Prefers keeping quality companies through downturns

## HOW THE DEBATE WORKS

Round 1: Initial Positions
┌─────────────────────────────────────────┐
│ Each agent sees portfolio data          │
│ Each provides initial position          │
│ Supervisor evaluates consensus          │
├─────────────────────────────────────────┤
│ TaxOptimizer:      HARVEST (85% conf)   │
│ RiskManager:       HARVEST (78% conf)   │
│ MarketStrategist:  KEEP    (70% conf)   │
│ GrowthOptimizer:   KEEP    (82% conf)   │
├─────────────────────────────────────────┤
│ Consensus: NONE                         │
│ Feedback: "2v2 split - debate why"      │
└─────────────────────────────────────────┘
                    ↓
Round 2: Refined Positions (seeing Round 1)
┌─────────────────────────────────────────┐
│ Each agent sees previous round           │
│ Can respond to specific arguments        │
│ May change position or strengthen it     │
├─────────────────────────────────────────┤
│ TaxOptimizer:      HARVEST (85% conf)   │
│ RiskManager:       KEEP    (62% conf)   │ ← Changed!
│ MarketStrategist:  KEEP    (72% conf)   │
│ GrowthOptimizer:   KEEP    (85% conf)   │
├─────────────────────────────────────────┤
│ Consensus: PARTIAL (3 for KEEP)         │
│ Feedback: "Growth momentum building"    │
└─────────────────────────────────────────┘
                    ↓
Round 3: Final Convergence
┌─────────────────────────────────────────┐
│ Agents stabilize on positions           │
│ Debate reaches natural conclusion        │
├─────────────────────────────────────────┤
│ TaxOptimizer:      KEEP    (75% conf)   │ ← Changed!
│ RiskManager:       KEEP    (70% conf)   │
│ MarketStrategist:  KEEP    (74% conf)   │
│ GrowthOptimizer:   KEEP    (87% conf)   │
├─────────────────────────────────────────┤
│ Consensus: FULL (4/4 agree on KEEP)     │
│ Supervisor: "Consensus reached!"        │
│ Debate Complete ✓                       │
└─────────────────────────────────────────┘

## SUPERVISOR'S ROLE

After each round, supervisor:
  1. Counts votes for each decision type (HARVEST, KEEP, PRIORITY_HARVEST)
  2. Identifies agreements (all agents agree)
  3. Identifies disagreements (agents split)
  4. Evaluates consensus status:
     • Full: All agents agree (exit debate)
     • Partial: Majority agrees (may continue)
     • None: Strong split (continue debate)
  5. Provides feedback for next round
  6. Decides if debate should continue

## KEY FEATURES

Multi-Round Loop
  ✓ Each round builds on previous rounds
  ✓ Agents refine positions based on discussion
  ✓ Context preserved across rounds

Confidence Scoring
  ✓ Each position includes confidence (0-100%)
  ✓ Used in final voting
  ✓ Shows agent conviction level

Supervisor Orchestration
  ✓ Active moderator, not passive observer
  ✓ Guides discussion based on progress
  ✓ Makes debate termination decision

Comprehensive Logging
  ✓ Every statement captured
  ✓ All positions recorded
  ✓ Supervisor feedback preserved
  ✓ Full JSON audit trail

## USAGE

from backend.core.multi_turn_debate_system import MultiTurnDebateSystem, StockPosition

# Create debate system
debate = MultiTurnDebateSystem(max_rounds=5)

# Prepare positions
positions = [
    StockPosition(symbol="RELIANCE", quantity=100, cost_basis=2000,
                  current_price=1000, holding_days=603, 
                  loss_amount=100000, tax_saving=30000),
    # ... more positions
]

# Run debate
session = debate.debate_portfolio_strategy(positions, context="Optional context")

# Check results
print(f"Rounds: {session.total_rounds}")
print(f"Status: {session.final_status}")
print(f"Strategy: {session.final_strategy}")
print(f"Conclusion: {session.supervisor_conclusion}")

## OUTPUT STRUCTURE

session = {
    "session_id": "20251108_024751",
    "total_rounds": 3,
    "final_status": "consensus_reached",
    "positions": [
        {"symbol": "RELIANCE", "loss": 100000, "tax_saving": 30000, ...},
        ...
    ],
    "rounds": [
        {
            "round_number": 1,
            "agent_statements": [
                {
                    "agent": "TaxOptimizer",
                    "position": "HARVEST",
                    "confidence": 85.0,
                    "key_points": ["Max tax saving", "Offsets gains"],
                    "statement": "Full LLM response..."
                },
                ...
            ],
            "supervisor_feedback": "2v2 split detected...",
            "consensus_status": "None",
            "agreements": {...},
            "disagreements": {...}
        },
        // More rounds...
    ],
    "final_strategy": {
        "RELIANCE": "KEEP",
        "INFY": "HARVEST",
        "HDFC": "KEEP"
    },
    "supervisor_conclusion": "All agents agree that..."
}

## CONFIGURATION

max_rounds=3   # Short debate (typically reaches consensus faster)
max_rounds=5   # Standard debate (recommended)
max_rounds=7   # Extended debate (thorough analysis)

## WHEN TO USE MULTI-TURN DEBATE

✓ Complex portfolio decisions with conflicting priorities
✓ When you want to see agent reasoning evolution
✓ Understanding why agents change their minds
✓ Building confidence in portfolio decisions
✓ Explaining decisions to stakeholders (full audit trail)

## WHEN TO USE SINGLE-ROUND DEBATE

✓ Quick decisions needed
✓ Simple portfolios with clear choices
✓ Real-time portfolio adjustments
✓ When speed matters more than reasoning depth

## FILES

backend/core/multi_turn_debate_system.py    Main implementation
test_multi_turn_debate.py                   Test and demo
MULTI_TURN_DEBATE.md                        Full documentation
MULTI_TURN_SUMMARY.md                       Detailed architecture

## PERFORMANCE

Typical Metrics:
  • Rounds to consensus: 2-3
  • Time per round: 30-60 seconds
  • Total debate duration: 1-3 minutes
  • Agent statements per round: 4 (one per agent)
  • Total statements per session: 8-20

## NEXT STEPS

1. Test with your portfolio:
   python test_multi_turn_debate.py

2. View debate results:
   cat logs/multi_turn_debates/multi_turn_debate_*.json | jq

3. Integrate with your portfolio system:
   from backend.core.multi_turn_debate_system import MultiTurnDebateSystem
   session = debate_system.debate_portfolio_strategy(your_positions)

4. Extend with custom agents:
   class ComplianceOfficer(AgentRole): ...

═══════════════════════════════════════════════════════════════════════════════
✓ Implementation Complete
✓ Pushed to GitHub
✓ Ready for Integration
═══════════════════════════════════════════════════════════════════════════════
""")
