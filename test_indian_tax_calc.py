"""Quick test of Indian tax calculator."""

from backend.agents.tax_savings_calculator import TaxSavingsCalculatorAgent
from backend.utils.data_models import TaxLossOpportunity, PortfolioHolding
from datetime import datetime, timedelta

# Helper to create holdings with calculated holding days
def create_holding_and_opportunity(symbol, quantity, purchase_price, current_price, days_ago, loss_pct, rank, reason):
    purchase_date = datetime.now() - timedelta(days=days_ago)
    
    holding = PortfolioHolding(
        stock_name=symbol,
        symbol=symbol,
        quantity=quantity,
        purchase_date=purchase_date,
        purchase_price=purchase_price,
        current_price=current_price,
        asset_class="equity"
    )
    
    # Calculate unrealized loss
    unrealized_loss = abs(holding.unrealized_gain_loss)
    
    # Add holding_days attribute (used by tax calculator)
    holding.holding_days = days_ago
    
    opportunity = TaxLossOpportunity(
        holding=holding,
        unrealized_loss=unrealized_loss,
        loss_percentage=loss_pct,
        eligible_for_harvesting=True,
        reason=reason,
        rank=rank
    )
    
    return opportunity

# Create test opportunities with different holding periods
opportunities = [
    # Long term (> 365 days) - LTCG 12.5%
    create_holding_and_opportunity(
        symbol="RELIANCE",
        quantity=100,
        purchase_price=2500,
        current_price=1500,
        days_ago=603,
        loss_pct=40.0,
        rank=1,
        reason="Long-term loss eligible for LTCG offset"
    ),
    # Short term (< 365 days) - STCG 20%
    create_holding_and_opportunity(
        symbol="INFY",
        quantity=50,
        purchase_price=1500,
        current_price=1250,
        days_ago=180,
        loss_pct=16.67,
        rank=3,
        reason="Short-term loss eligible for STCG offset"
    ),
    # Long term - LTCG 12.5%
    create_holding_and_opportunity(
        symbol="HDFC",
        quantity=75,
        purchase_price=2000,
        current_price=1200,
        days_ago=450,
        loss_pct=40.0,
        rank=2,
        reason="Long-term loss eligible for LTCG offset"
    )
]

print("="*80)
print("INDIAN TAX SAVINGS CALCULATOR TEST")
print("="*80)
print()

# Initialize calculator
calc = TaxSavingsCalculatorAgent()

# Calculate savings with capital gains rates
result = calc.calculate_savings(
    harvested_opportunities=opportunities,
    use_capital_gains_rate=True
)

print("INPUT POSITIONS:")
for opp in opportunities:
    holding = opp.holding
    holding_type = "LTCG (>1yr)" if holding.holding_days >= 365 else "STCG (<1yr)"
    rate = calc.LTCG_RATE if holding.holding_days >= 365 else calc.STCG_RATE
    print(f"  {holding.symbol}: ₹{opp.unrealized_loss:,} loss | {holding.holding_days} days | {holding_type} @ {rate*100}%")

print()
print("CALCULATED TAX SAVINGS:")
print(f"  Total Loss Harvested: ₹{result.total_harvested_loss:,.2f}")
print(f"  Weighted Tax Rate: {result.applicable_tax_rate*100:.2f}%")
print(f"  Immediate Tax Savings: ₹{result.immediate_tax_savings:,.2f}")
print()

print("10-YEAR PROJECTION (Reinvested):")
print(f"  Projected Value: ₹{result.projected_10yr_value:,.2f}")
print(f"  Growth: ₹{result.projected_value_increase:,.2f}")
print(f"  CAGR: {calc._calculate_cagr(result.immediate_tax_savings, result.projected_10yr_value, 10)*100:.2f}%")
print()

print("ASSUMPTIONS:")
for key, value in result.assumptions.items():
    print(f"  {key}: {value}")
print()

# Generate full report
report = calc.generate_savings_report(result)

print("="*80)
print("DETAILED REPORT")
print("="*80)
print()

import json
print(json.dumps(report, indent=2))
