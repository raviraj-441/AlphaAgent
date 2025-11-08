"""
AlphaAgent - Multi-Agent Tax Loss Harvesting System
Main Entry Point for Portfolio Debate System
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from backend.core.multi_turn_debate_system import MultiTurnDebateSystem, StockPosition


def create_sample_portfolio() -> List[StockPosition]:
    """Create a sample Indian portfolio for testing."""
    return [
        StockPosition(
            symbol="RELIANCE",
            quantity=100,
            cost_basis=2600,
            current_price=2450,
            holding_days=210,
            loss_amount=15000,
            tax_saving=4500
        ),
        StockPosition(
            symbol="HDFC",
            quantity=75,
            cost_basis=1750,
            current_price=1600,
            holding_days=328,
            loss_amount=11250,
            tax_saving=3375
        ),
        StockPosition(
            symbol="INFY",
            quantity=50,
            cost_basis=1700,
            current_price=1600,
            holding_days=945,
            loss_amount=5000,
            tax_saving=1500
        ),
        StockPosition(
            symbol="SBIN",
            quantity=150,
            cost_basis=650,
            current_price=600,
            holding_days=275,
            loss_amount=7500,
            tax_saving=2250
        ),
    ]


def run_portfolio_debate(
    positions: List[StockPosition],
    max_rounds: int = 5,
    context: str = ""
) -> Dict[str, Any]:
    """
    Run multi-turn portfolio debate.
    
    Args:
        positions: List of stock positions
        max_rounds: Maximum debate rounds
        context: Additional portfolio context
    
    Returns:
        Dict with debate results
    """
    logger.info("="*80)
    logger.info("STARTING MULTI-TURN PORTFOLIO DEBATE")
    logger.info("="*80)
    
    # Initialize debate system
    debate_system = MultiTurnDebateSystem(max_rounds=max_rounds)
    
    # Display portfolio
    logger.info(f"\nPortfolio: {len(positions)} positions")
    total_loss = sum(p.loss_amount for p in positions)
    total_tax_saving = sum(p.tax_saving for p in positions)
    logger.info(f"Total Unrealized Loss: INR {total_loss:,.0f}")
    logger.info(f"Total Tax Saving Potential: INR {total_tax_saving:,.0f}\n")
    
    for p in positions:
        logger.info(f"  {p.symbol:10} | Loss: INR {p.loss_amount:7,.0f} | "
                   f"Tax Saving: INR {p.tax_saving:6,.0f} | Days: {p.holding_days}")
    
    # Run debate
    logger.info("\n" + "="*80)
    logger.info("DEBATE IN PROGRESS...")
    logger.info("="*80 + "\n")
    
    try:
        session = debate_system.debate_portfolio_strategy(positions, context)
        
        # Display results
        logger.info("\n" + "="*80)
        logger.info("DEBATE COMPLETE")
        logger.info("="*80)
        logger.info(f"\nSession ID: {session.session_id}")
        logger.info(f"Total Rounds: {session.total_rounds}")
        logger.info(f"Final Status: {session.final_status.value}")
        logger.info(f"\nFinal Strategy:")
        
        for symbol, decision in session.final_strategy.items():
            logger.info(f"  {symbol:10} -> {decision}")
        
        logger.info(f"\nSupervisor Conclusion:")
        logger.info(f"  {session.supervisor_conclusion}\n")
        
        # Display round-by-round summary
        logger.info("="*80)
        logger.info("ROUND SUMMARY")
        logger.info("="*80)
        
        for round_data in session.rounds:
            logger.info(f"\nRound {round_data.round_number}:")
            logger.info(f"  Consensus Status: {round_data.consensus_status}")
            
            # Show agent positions
            for stmt in round_data.agent_statements:
                logger.info(f"    {stmt.agent_role.value:20} -> {stmt.position:15} "
                          f"(Confidence: {stmt.confidence:.0f}%)")
        
        logger.info("\n" + "="*80)
        logger.info(f"Debate log saved to: logs/multi_turn_debates/multi_turn_debate_{session.session_id}.json")
        logger.info("="*80 + "\n")
        
        return {
            "success": True,
            "session_id": session.session_id,
            "total_rounds": session.total_rounds,
            "final_status": session.final_status.value,
            "final_strategy": session.final_strategy,
            "supervisor_conclusion": session.supervisor_conclusion
        }
        
    except Exception as e:
        logger.error(f"Debate failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("  AlphaAgent - Multi-Agent Tax Loss Harvesting System")
    print("="*80 + "\n")
    
    # Create sample portfolio
    positions = create_sample_portfolio()
    
    # Portfolio context
    context = """
    Market Conditions: Neutral
    Tax Year: 2024-25
    Investor Profile: Long-term growth focused
    Capital Gains: INR 50,000 (to offset)
    Risk Tolerance: Moderate
    """
    
    # Run debate
    result = run_portfolio_debate(
        positions=positions,
        max_rounds=5,
        context=context.strip()
    )
    
    if result.get("success"):
        print("\n[SUCCESS] Debate completed successfully!")
        print(f"   Final Strategy: {result['final_strategy']}")
    else:
        print(f"\n[ERROR] Debate failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
