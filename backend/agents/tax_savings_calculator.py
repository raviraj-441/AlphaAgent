"""
Tax Savings Calculator Agent - Computes immediate and projected tax savings.
Configured for Indian Income Tax and Capital Gains Tax rules.
"""

import logging
import random
from typing import List, Dict, Any
from dataclasses import dataclass

from backend.utils.data_models import TaxLossOpportunity, TaxSavingsCalculation

logger = logging.getLogger(__name__)


@dataclass
class MonteCarloResult:
    """Result of Monte Carlo simulation."""
    initial_value: float
    final_value: float
    annualized_return: float
    total_return_percent: float


class TaxSavingsCalculatorAgent:
    """
    Calculates immediate tax savings and projects 10-year growth for Indian market.
    Uses Monte Carlo simulation for future value estimation.
    
    Indian Tax Rules (FY 2024-25):
    - Short Term Capital Gains (STCG): 20% on equities held < 1 year
    - Long Term Capital Gains (LTCG): 12.5% on equities held >= 1 year (no indexation on equities)
    - Income Tax: Progressive slabs under new regime
    """
    
    # Indian Market Assumptions
    ANNUAL_RETURN_MEAN = 0.12      # 12% average annual return (Indian equities historical)
    ANNUAL_RETURN_STD = 0.15       # 15% standard deviation (higher volatility)
    INFLATION_RATE = 0.06          # 6% annual inflation (India CPI average)
    
    # Capital Gains Tax Rates (Indian Market)
    STCG_RATE = 0.20               # 20% for equity held < 1 year
    LTCG_RATE = 0.125              # 12.5% for equity held >= 1 year
    LTCG_EXEMPTION = 125000        # ₹1.25 lakh exemption per year on LTCG
    
    # Income Tax Slabs (New Regime FY 2024-25) - applicable for offsetting gains
    INCOME_TAX_SLABS = {
        0.00: 300000,              # 0% up to ₹3 lakh
        0.05: 700000,              # 5% from ₹3L to ₹7L
        0.10: 1000000,             # 10% from ₹7L to ₹10L
        0.15: 1200000,             # 15% from ₹10L to ₹12L
        0.20: 1500000,             # 20% from ₹12L to ₹15L
        0.30: float('inf')         # 30% above ₹15L
    }
    
    def __init__(self):
        """Initialize Tax Savings Calculator Agent for Indian market."""
        self.logger = logging.getLogger(__name__)
    
    def calculate_savings(
        self,
        harvested_opportunities: List[TaxLossOpportunity],
        applicable_tax_rate: float = None,
        annual_income: float = None,
        use_capital_gains_rate: bool = True
    ) -> TaxSavingsCalculation:
        """
        Calculate immediate and projected tax savings using Indian tax rules.
        
        Args:
            harvested_opportunities: List of opportunities being harvested
            applicable_tax_rate: Tax rate to apply (0.0-1.0). If None, calculated from holding period
            annual_income: Annual income for income tax bracket estimation
            use_capital_gains_rate: If True, use STCG/LTCG rates based on holding period
        
        Returns:
            TaxSavingsCalculation object
        """
        self.logger.info(f"Calculating savings for {len(harvested_opportunities)} opportunities (Indian tax rules)")
        
        # Calculate total harvested loss
        total_loss = sum(opp.unrealized_loss for opp in harvested_opportunities)
        
        # Determine applicable tax rate
        if applicable_tax_rate is None:
            if use_capital_gains_rate:
                # Calculate weighted average capital gains rate based on holding periods
                applicable_tax_rate = self._calculate_weighted_cg_rate(harvested_opportunities)
            else:
                # Use income tax bracket
                applicable_tax_rate = self._estimate_income_tax_bracket(annual_income or 1000000)
        
        # Calculate immediate savings (losses can offset gains)
        immediate_savings = total_loss * applicable_tax_rate
        
        # For LTCG, consider annual exemption if applicable
        ltcg_count = sum(1 for opp in harvested_opportunities 
                        if opp.holding and opp.holding.holding_days >= 365)
        if ltcg_count > 0 and use_capital_gains_rate:
            # Proportional exemption benefit
            exemption_benefit = min(self.LTCG_EXEMPTION * self.LTCG_RATE, immediate_savings * 0.1)
            immediate_savings += exemption_benefit
        
        # Project 10-year growth using Monte Carlo (reinvesting tax savings in Indian equities)
        projected_value = self._monte_carlo_projection(
            initial_value=immediate_savings,
            years=10,
            annual_return_mean=self.ANNUAL_RETURN_MEAN,
            annual_return_std=self.ANNUAL_RETURN_STD,
            runs=1000
        )
        
        assumptions = {
            "annual_return_mean_percent": self.ANNUAL_RETURN_MEAN * 100,
            "annual_return_std_percent": self.ANNUAL_RETURN_STD * 100,
            "inflation_rate_percent": self.INFLATION_RATE * 100,
            "projection_years": 10,
            "monte_carlo_runs": 1000,
            "tax_rate_applied_percent": applicable_tax_rate * 100,
            "market": "India",
            "stcg_rate_percent": self.STCG_RATE * 100,
            "ltcg_rate_percent": self.LTCG_RATE * 100,
            "ltcg_exemption_inr": self.LTCG_EXEMPTION
        }
        
        return TaxSavingsCalculation(
            transaction_count=len(harvested_opportunities),
            total_harvested_loss=total_loss,
            applicable_tax_rate=applicable_tax_rate,
            immediate_tax_savings=immediate_savings,
            projected_10yr_value=projected_value,
            projected_value_increase=projected_value - immediate_savings,
            monte_carlo_runs=1000,
            assumptions=assumptions
        )
    
    def _calculate_weighted_cg_rate(self, opportunities: List[TaxLossOpportunity]) -> float:
        """
        Calculate weighted average capital gains tax rate based on holding periods.
        
        Args:
            opportunities: List of tax loss opportunities
        
        Returns:
            Weighted average tax rate
        """
        if not opportunities:
            return self.LTCG_RATE
        
        total_loss = sum(opp.unrealized_loss for opp in opportunities)
        if total_loss == 0:
            return self.LTCG_RATE
        
        weighted_rate = 0.0
        for opp in opportunities:
            weight = opp.unrealized_loss / total_loss
            # STCG if held < 365 days, LTCG otherwise
            holding_days = opp.holding.holding_days if opp.holding else 0
            rate = self.STCG_RATE if holding_days < 365 else self.LTCG_RATE
            weighted_rate += rate * weight
        
        return weighted_rate
    
    def _estimate_income_tax_bracket(self, annual_income: float) -> float:
        """
        Estimate applicable income tax bracket from annual income (New Tax Regime).
        
        Args:
            annual_income: Annual income in rupees
        
        Returns:
            Estimated tax rate (0.0-1.0)
        """
        for rate, limit in sorted(self.INCOME_TAX_SLABS.items()):
            if annual_income <= limit:
                return rate
        
        return 0.30
    
    def _monte_carlo_projection(
        self,
        initial_value: float,
        years: int = 10,
        annual_return_mean: float = 0.08,
        annual_return_std: float = 0.03,
        runs: int = 1000
    ) -> float:
        """
        Project future value using Monte Carlo simulation.
        
        Args:
            initial_value: Starting investment amount
            years: Number of years to project
            annual_return_mean: Mean annual return
            annual_return_std: Standard deviation of annual return
            runs: Number of simulation runs
        
        Returns:
            Average projected value across runs
        """
        self.logger.debug(f"Running {runs} Monte Carlo simulations for {years} years (Indian market assumptions)")
        
        final_values = []
        
        for _ in range(runs):
            value = initial_value
            
            for year in range(years):
                # Random annual return from normal distribution
                annual_return = random.gauss(annual_return_mean, annual_return_std)
                value *= (1 + annual_return)
            
            final_values.append(value)
        
        # Return average projected value
        avg_value = sum(final_values) / len(final_values)
        self.logger.debug(f"Average projected value: ₹{avg_value:,.2f}")
        
        return avg_value
    
    def sensitivity_analysis(
        self,
        base_calculation: TaxSavingsCalculation,
        parameter: str,
        variations: List[float]
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on tax savings calculation.
        
        Args:
            base_calculation: Base TaxSavingsCalculation
            parameter: Parameter to vary ('tax_rate', 'annual_return', 'inflation')
            variations: List of variation values to test
        
        Returns:
            Sensitivity analysis results
        """
        results = []
        
        for variation in variations:
            if parameter == "tax_rate":
                savings = base_calculation.total_harvested_loss * variation
                future_val = self._monte_carlo_projection(
                    savings,
                    years=10
                )
            
            elif parameter == "annual_return":
                future_val = self._monte_carlo_projection(
                    base_calculation.immediate_tax_savings,
                    years=10,
                    annual_return_mean=variation
                )
            
            elif parameter == "inflation":
                # Adjust returns for inflation
                real_return = self.ANNUAL_RETURN_MEAN - variation
                future_val = self._monte_carlo_projection(
                    base_calculation.immediate_tax_savings,
                    years=10,
                    annual_return_mean=real_return
                )
            
            else:
                future_val = base_calculation.projected_10yr_value
            
            results.append({
                "parameter_value": variation,
                "projected_10yr_value": round(future_val, 2)
            })
        
        return {
            "parameter": parameter,
            "base_value": getattr(base_calculation, f"{parameter}_rate" if parameter.endswith("_rate") else parameter, 0),
            "results": results
        }
    
    def compare_scenarios(
        self,
        harvested_opportunities: List[TaxLossOpportunity],
        scenarios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Compare tax savings across different scenarios.
        
        Args:
            harvested_opportunities: List of opportunities
            scenarios: List of scenario configs with 'tax_rate' and optional 'annual_income'
        
        Returns:
            List of scenario results
        """
        results = []
        
        for scenario in scenarios:
            calc = self.calculate_savings(
                harvested_opportunities,
                applicable_tax_rate=scenario.get("tax_rate"),
                annual_income=scenario.get("annual_income")
            )
            
            results.append({
                "scenario": scenario.get("name", "Scenario"),
                "tax_rate": scenario.get("tax_rate"),
                "immediate_savings": round(calc.immediate_tax_savings, 2),
                "projected_10yr_value": round(calc.projected_10yr_value, 2),
                "projected_increase": round(calc.projected_value_increase, 2),
                "cagr": self._calculate_cagr(
                    calc.immediate_tax_savings,
                    calc.projected_10yr_value,
                    10
                )
            })
        
        return results
    
    def _calculate_cagr(
        self,
        initial: float,
        final: float,
        years: int
    ) -> float:
        """
        Calculate Compound Annual Growth Rate.
        
        Args:
            initial: Initial value
            final: Final value
            years: Number of years
        
        Returns:
            CAGR as decimal (0.08 = 8%)
        """
        if initial <= 0 or years <= 0:
            return 0.0
        
        cagr = (final / initial) ** (1 / years) - 1
        return round(cagr, 4)
    
    def generate_savings_report(
        self,
        calculation: TaxSavingsCalculation
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive tax savings report for Indian market.
        
        Args:
            calculation: TaxSavingsCalculation object
        
        Returns:
            Formatted report with Indian currency (INR)
        """
        return {
            "summary": {
                "transactions_harvested": calculation.transaction_count,
                "total_loss_harvested": f"₹{calculation.total_harvested_loss:,.2f}",
                "applicable_tax_rate": f"{calculation.applicable_tax_rate * 100}%"
            },
            "immediate_impact": {
                "tax_savings": f"₹{calculation.immediate_tax_savings:,.2f}",
                "effective_return": f"{(calculation.immediate_tax_savings / calculation.total_harvested_loss * 100):.1f}%"
            },
            "10_year_projection": {
                "initial_investment": f"₹{calculation.immediate_tax_savings:,.2f}",
                "projected_value": f"₹{calculation.projected_10yr_value:,.2f}",
                "value_increase": f"₹{calculation.projected_value_increase:,.2f}",
                "cagr": f"{self._calculate_cagr(calculation.immediate_tax_savings, calculation.projected_10yr_value, 10) * 100:.2f}%"
            },
            "assumptions": calculation.assumptions,
            "tax_notes": {
                "stcg_info": "Short Term Capital Gains (holding < 1 year): 20%",
                "ltcg_info": "Long Term Capital Gains (holding >= 1 year): 12.5%",
                "ltcg_exemption": f"Annual LTCG exemption: ₹{self.LTCG_EXEMPTION:,}",
                "market": "Indian Equities"
            }
        }
