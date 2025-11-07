"""
Tax Savings Calculator Agent - Computes immediate and projected tax savings.
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
    Calculates immediate tax savings and projects 10-year growth.
    Uses Monte Carlo simulation for future value estimation.
    """
    
    # Assumptions
    ANNUAL_RETURN_MEAN = 0.08      # 8% average annual return
    ANNUAL_RETURN_STD = 0.03       # 3% standard deviation
    INFLATION_RATE = 0.04          # 4% annual inflation
    TAX_BRACKETS = {
        0.10: 50000,      # 10% for income up to 50k
        0.20: 500000,     # 20% for 50k to 500k
        0.30: float('inf') # 30% for above 500k
    }
    
    def __init__(self):
        """Initialize Tax Savings Calculator Agent."""
        self.logger = logging.getLogger(__name__)
    
    def calculate_savings(
        self,
        harvested_opportunities: List[TaxLossOpportunity],
        applicable_tax_rate: float = None,
        annual_income: float = None
    ) -> TaxSavingsCalculation:
        """
        Calculate immediate and projected tax savings.
        
        Args:
            harvested_opportunities: List of opportunities being harvested
            applicable_tax_rate: Tax rate to apply (0.0-1.0). If None, estimated from income.
            annual_income: Annual income for bracket estimation
        
        Returns:
            TaxSavingsCalculation object
        """
        self.logger.info(f"Calculating savings for {len(harvested_opportunities)} opportunities")
        
        # Calculate total harvested loss
        total_loss = sum(opp.unrealized_loss for opp in harvested_opportunities)
        
        # Determine applicable tax rate
        if applicable_tax_rate is None:
            applicable_tax_rate = self._estimate_tax_bracket(annual_income or 400000)
        
        # Calculate immediate savings
        immediate_savings = total_loss * applicable_tax_rate
        
        # Project 10-year growth using Monte Carlo
        initial_invested = total_savings = immediate_savings
        
        # Simulate reinvesting tax savings
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
            "tax_rate_applied_percent": applicable_tax_rate * 100
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
    
    def _estimate_tax_bracket(self, annual_income: float) -> float:
        """
        Estimate applicable tax bracket from annual income.
        
        Args:
            annual_income: Annual income in rupees
        
        Returns:
            Estimated tax rate (0.0-1.0)
        """
        for rate, limit in sorted(self.TAX_BRACKETS.items()):
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
        self.logger.debug(f"Running {runs} Monte Carlo simulations for {years} years")
        
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
        self.logger.debug(f"Average projected value: ${avg_value:.2f}")
        
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
        Generate a comprehensive tax savings report.
        
        Args:
            calculation: TaxSavingsCalculation object
        
        Returns:
            Formatted report
        """
        return {
            "summary": {
                "transactions_harvested": calculation.transaction_count,
                "total_loss_harvested": f"${calculation.total_harvested_loss:,.2f}",
                "applicable_tax_rate": f"{calculation.applicable_tax_rate * 100}%"
            },
            "immediate_impact": {
                "tax_savings": f"${calculation.immediate_tax_savings:,.2f}",
                "effective_return": f"{(calculation.immediate_tax_savings / calculation.total_harvested_loss * 100):.1f}%"
            },
            "10_year_projection": {
                "initial_investment": f"${calculation.immediate_tax_savings:,.2f}",
                "projected_value": f"${calculation.projected_10yr_value:,.2f}",
                "value_increase": f"${calculation.projected_value_increase:,.2f}",
                "cagr": f"{(calculation.projected_10yr_value / calculation.immediate_tax_savings - 1) / 10 * 100:.2f}%"
            },
            "assumptions": calculation.assumptions
        }
