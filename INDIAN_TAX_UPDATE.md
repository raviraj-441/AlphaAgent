# Indian Tax Calculator Update - Summary

## Changes Made

Updated `backend/agents/tax_savings_calculator.py` to align with Indian market tax rules and regulations.

### Key Updates

#### 1. **Capital Gains Tax Rates** (Indian Market)
- **STCG (Short Term)**: 20% for equities held < 1 year
- **LTCG (Long Term)**: 12.5% for equities held >= 1 year
- **LTCG Exemption**: ₹1,25,000 annual exemption on long-term gains

#### 2. **Income Tax Slabs** (New Tax Regime FY 2024-25)
```
₹0 - ₹3,00,000:     0%
₹3,00,000 - ₹7,00,000:    5%
₹7,00,000 - ₹10,00,000:   10%
₹10,00,000 - ₹12,00,000:  15%
₹12,00,000 - ₹15,00,000:  20%
Above ₹15,00,000:         30%
```

#### 3. **Market Assumptions** (Indian Equities)
- **Annual Return Mean**: 12% (vs 8% for US market)
- **Annual Return Std Dev**: 15% (higher volatility)
- **Inflation Rate**: 6% (Indian CPI average)

#### 4. **New Features**
- Weighted capital gains rate calculation based on holding periods
- Automatic STCG/LTCG classification (365-day threshold)
- LTCG exemption benefit calculation
- Currency formatting in INR (₹)
- Indian tax notes in reports

### Test Results

```
INPUT POSITIONS:
  RELIANCE: ₹100,000 loss | 603 days | LTCG (>1yr) @ 12.5%
  INFY: ₹12,500 loss | 180 days | STCG (<1yr) @ 20.0%
  HDFC: ₹60,000 loss | 450 days | LTCG (>1yr) @ 12.5%

CALCULATED TAX SAVINGS:
  Total Loss Harvested: ₹172,500.00
  Weighted Tax Rate: 13.04%
  Immediate Tax Savings: ₹24,750.00

10-YEAR PROJECTION:
  Projected Value: ₹75,189.68
  Growth: ₹50,439.68
  CAGR: 11.75%
```

### API Changes

The `calculate_savings()` method now accepts:
- `use_capital_gains_rate` (bool): Use STCG/LTCG rates instead of income tax rates
- Automatically calculates weighted rate based on holding periods

### Files Modified
- `backend/agents/tax_savings_calculator.py` - Updated with Indian tax rules
- `test_indian_tax_calc.py` - Test script demonstrating Indian tax calculations

### Compliance Notes
All calculations follow current Indian Income Tax Act provisions for FY 2024-25.
