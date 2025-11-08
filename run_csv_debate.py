"""
Run portfolio debate from any CSV file
Usage: python run_csv_debate.py <path_to_csv>
"""

import csv
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from backend.core.multi_turn_debate_system import MultiTurnDebateSystem, StockPosition


def load_portfolio_from_csv(csv_path: str):
    """
    Load portfolio from CSV file and convert to StockPosition objects.
    
    Expected CSV format:
    Symbol,Quantity,PurchaseDate,PurchasePrice,CurrentPrice
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of StockPosition objects (only positions with losses)
    """
    positions = []
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    logger.info(f"Reading CSV file: {csv_path}")
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        # Validate required columns
        required_cols = {'Symbol', 'Quantity', 'PurchaseDate', 'PurchasePrice', 'CurrentPrice'}
        if not required_cols.issubset(reader.fieldnames):
            raise ValueError(
                f"CSV missing required columns. Expected: {required_cols}, "
                f"Found: {set(reader.fieldnames)}"
            )
        
        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            try:
                symbol = row['Symbol'].strip()
                quantity = int(row['Quantity'])
                purchase_date = datetime.strptime(row['PurchaseDate'].strip(), '%Y-%m-%d')
                purchase_price = float(row['PurchasePrice'])
                current_price = float(row['CurrentPrice'])
                
                # Calculate metrics
                cost_basis = purchase_price
                holding_days = (datetime.now() - purchase_date).days
                loss_amount = max(0, (purchase_price - current_price) * quantity)
                
                # Estimate tax saving (using Indian STCG/LTCG rates)
                if holding_days >= 365:
                    tax_rate = 0.125  # LTCG 12.5%
                else:
                    tax_rate = 0.20   # STCG 20%
                
                tax_saving = loss_amount * tax_rate
                
                # Only include positions with losses
                if loss_amount > 0:
                    position = StockPosition(
                        symbol=symbol,
                        quantity=quantity,
                        cost_basis=cost_basis,
                        current_price=current_price,
                        holding_days=holding_days,
                        loss_amount=loss_amount,
                        tax_saving=tax_saving
                    )
                    positions.append(position)
                    
                    logger.info(
                        f"  {symbol}: Qty={quantity}, "
                        f"Purchase=₹{purchase_price}, Current=₹{current_price}, "
                        f"Loss=₹{loss_amount:,.0f}, Days={holding_days}"
                    )
                else:
                    logger.debug(f"  {symbol}: Skipped (no loss)")
                    
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping row {row_num} due to error: {e}")
                continue
    
    return positions


def main():
    """Run debate on CSV portfolio."""
    parser = argparse.ArgumentParser(
        description='Run multi-agent portfolio debate on CSV data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example CSV format:
  Symbol,Quantity,PurchaseDate,PurchasePrice,CurrentPrice
  RELIANCE,15,2024-04-10,2600,2450
  HDFC,20,2023-12-15,1750,1600

Usage examples:
  python run_csv_debate.py data/test_portfolios/sample.csv
  python run_csv_debate.py my_portfolio.csv --rounds 5
  python run_csv_debate.py portfolio.csv --output results.txt
        """
    )
    
    parser.add_argument(
        'csv_file',
        type=str,
        help='Path to CSV file containing portfolio data'
    )
    
    parser.add_argument(
        '--rounds',
        type=int,
        default=3,
        help='Maximum number of debate rounds (default: 3)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between API calls in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: auto-generated with timestamp)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("  AlphaAgent - Portfolio Debate System")
    print("="*80 + "\n")
    
    # Load portfolio from CSV
    try:
        logger.info(f"Loading portfolio from: {args.csv_file}")
        positions = load_portfolio_from_csv(args.csv_file)
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        sys.exit(1)
    
    if not positions:
        logger.error("No positions with losses found in CSV!")
        logger.info("Note: Only stocks with unrealized losses are included in the debate.")
        sys.exit(1)
    
    logger.info(f"\n✅ Loaded {len(positions)} positions with losses")
    
    # Calculate totals
    total_loss = sum(p.loss_amount for p in positions)
    total_tax_saving = sum(p.tax_saving for p in positions)
    
    logger.info(f"   Total Unrealized Loss: ₹{total_loss:,.0f}")
    logger.info(f"   Total Tax Saving Potential: ₹{total_tax_saving:,.0f}")
    
    # Create context
    context = f"""
Market Condition: Neutral
Portfolio Size: {len(positions)} stocks with losses
Total Loss: ₹{total_loss:,.0f}
Total Tax Saving Potential: ₹{total_tax_saving:,.0f}

Indian Tax Context:
- STCG (< 1 year): 20%
- LTCG (>= 1 year): 12.5%
- LTCG exemption: ₹1,25,000/year
"""
    
    logger.info("\n" + "="*80)
    logger.info("STARTING MULTI-TURN PORTFOLIO DEBATE")
    logger.info("="*80 + "\n")
    
    # Initialize debate system
    debate_system = MultiTurnDebateSystem(
        max_rounds=args.rounds,
        api_delay=args.delay
    )
    
    try:
        # Run debate
        session = debate_system.debate_portfolio_strategy(positions, context)
        
        # Display results
        print("\n" + "="*80)
        print("  DEBATE RESULTS")
        print("="*80 + "\n")
        
        print(f"Session ID: {session.session_id}")
        print(f"Total Rounds: {session.total_rounds}")
        print(f"Final Status: {session.final_status.value}")
        print(f"\nFinal Strategy:")
        for symbol, decision in session.final_strategy.items():
            print(f"  {symbol}: {decision}")
        
        print(f"\nSupervisor Conclusion:")
        print(f"  {session.supervisor_conclusion[:200]}...")
        
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            csv_name = Path(args.csv_file).stem
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"debate_results_{csv_name}_{timestamp}.txt"
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("PORTFOLIO DEBATE RESULTS\n")
            f.write("="*80 + "\n\n")
            f.write(f"CSV File: {args.csv_file}\n")
            f.write(f"Session ID: {session.session_id}\n")
            f.write(f"Debate Rounds: {args.rounds} (max)\n")
            f.write(f"Total Rounds Completed: {session.total_rounds}\n")
            f.write(f"Final Status: {session.final_status.value}\n\n")
            
            f.write("PORTFOLIO SUMMARY:\n")
            f.write(f"  Stocks Analyzed: {len(positions)}\n")
            f.write(f"  Total Loss: ₹{total_loss:,.0f}\n")
            f.write(f"  Tax Saving Potential: ₹{total_tax_saving:,.0f}\n\n")
            
            f.write("FINAL STRATEGY:\n")
            for symbol, decision in session.final_strategy.items():
                f.write(f"  {symbol}: {decision}\n")
            
            f.write(f"\nSUPERVISOR CONCLUSION:\n")
            f.write(f"{session.supervisor_conclusion}\n\n")
            
            f.write("DEBATE ROUNDS:\n")
            f.write("="*80 + "\n")
            for round in session.rounds:
                f.write(f"\nROUND {round.round_number}:\n")
                f.write(f"Timestamp: {round.timestamp}\n")
                f.write(f"Consensus: {round.consensus_status}\n\n")
                
                for stmt in round.agent_statements:
                    f.write(f"{stmt.agent_role.value}:\n")
                    f.write(f"  Position: {stmt.position} ({stmt.confidence}% confidence)\n")
                    f.write(f"  Key Points: {', '.join(stmt.key_points)}\n\n")
                
                f.write(f"Supervisor Feedback:\n{round.supervisor_feedback}\n")
                f.write("-"*80 + "\n")
        
        print(f"\n✅ Full debate transcript saved to: {output_file}")
        
    except KeyboardInterrupt:
        logger.warning("\n\nDebate interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Debate failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
