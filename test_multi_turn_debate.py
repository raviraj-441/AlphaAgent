"""
Test Multi-Turn Debate System

Run a complete debate cycle with agents discussing and refining positions
until consensus is reached or max rounds exceeded.
"""

import json
from datetime import datetime
from backend.core.multi_turn_debate_system import MultiTurnDebateSystem, StockPosition

def test_multi_turn_debate():
    """Test the multi-turn debate system."""
    
    print("\n" + "="*100)
    print("  MULTI-TURN AGENT DEBATE WITH SUPERVISOR")
    print("="*100 + "\n")
    
    # Create test portfolio
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
        StockPosition(
            symbol="INFY",
            quantity=50,
            cost_basis=1000,
            current_price=750,
            holding_days=280,
            loss_amount=12500,
            tax_saving=3750
        ),
        StockPosition(
            symbol="HDFC",
            quantity=75,
            cost_basis=2000,
            current_price=1200,
            holding_days=450,
            loss_amount=60000,
            tax_saving=18000
        ),
    ]
    
    context = """
    Portfolio Summary:
    - Total unrealized loss: 172500 INR
    - Total tax saving potential: 51750 INR
    - Market condition: Neutral
    - Portfolio concentration: Moderate (RELIANCE 58%, HDFC 35%, INFY 7%)
    """
    
    print("[PORTFOLIO POSITIONS]")
    for p in positions:
        print(f"  {p.symbol}: Loss INR{p.loss_amount:,.0f} | Tax Saving INR{p.tax_saving:,.0f} | Days: {p.holding_days}")
    
    print(f"\n[PORTFOLIO CONTEXT]: {context.strip()}\n")
    
    # Initialize debate system
    debate_system = MultiTurnDebateSystem(max_rounds=5)
    
    print("[STARTING MULTI-TURN DEBATE...]\n")
    print("Agents will discuss and refine their positions until consensus is reached.")
    print("Supervisor will orchestrate the debate and evaluate progress.\n")
    
    # Run debate
    session = debate_system.debate_portfolio_strategy(positions, context)
    
    # Display results
    print("\n" + "="*100)
    print("  DEBATE RESULTS")
    print("="*100 + "\n")
    
    print(f"Session ID: {session.session_id}")
    print(f"Status: {session.final_status.value}")
    print(f"Total Rounds: {session.total_rounds}")
    print(f"Duration: {session.started_at} to {session.ended_at}\n")
    
    # Display each round
    for i, round_data in enumerate(session.rounds, 1):
        print(f"\n{'-'*100}")
        print(f"ROUND {i}")
        print(f"{'-'*100}\n")
        
        print(f"Consensus Status: {round_data.consensus_status}")
        print(f"Agreements: {round_data.agreements}")
        print(f"Disagreements: {round_data.disagreements}\n")
        
        for stmt in round_data.agent_statements:
            print(f"\n  [AGENT] {stmt.agent_role.value}")
            print(f"     Position: {stmt.position} (Confidence: {stmt.confidence}%)")
            print(f"     Key Points:")
            for point in stmt.key_points:
                print(f"       - {point}")
        
        print(f"\n  [SUPERVISOR FEEDBACK]")
        print(f"     {round_data.supervisor_feedback[:300]}...")
    
    # Display final strategy
    print(f"\n{'='*100}")
    print("  FINAL CONSENSUS STRATEGY")
    print(f"{'='*100}\n")
    
    for symbol, decision in session.final_strategy.items():
        print(f"  {symbol}: {decision}")
    
    print(f"\n[SUPERVISOR CONCLUSION]:\n")
    print(f"  {session.supervisor_conclusion}\n")
    
    # Save summary
    print(f"\n[OK] Full debate log saved to: logs/multi_turn_debates/multi_turn_debate_{session.session_id}.json")
    
    return session

if __name__ == "__main__":
    session = test_multi_turn_debate()
    print("\n[COMPLETE] Debate complete!\n")
