"""
Tax savings calculation endpoint.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime

from backend.utils.data_models import PortfolioHolding, TaxLossOpportunity
from backend.agents.tax_savings_calculator import TaxSavingsCalculatorAgent

logger = logging.getLogger(__name__)
router = APIRouter()


class OpportunityInput(BaseModel):
    """Tax loss opportunity input."""
    symbol: str
    stock_name: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: str
    unrealized_loss: float


class SavingsCalculationRequest(BaseModel):
    """Request model for tax savings calculation."""
    opportunities: List[OpportunityInput]
    annual_income: Optional[float] = 400000
    tax_rate: Optional[float] = None


@router.post("/calculate_savings")
async def calculate_savings(request: SavingsCalculationRequest = Body(...)):
    """
    Calculate immediate and projected tax savings.
    
    Args:
        request: SavingsCalculationRequest
    
    Returns:
        Tax savings calculations
    """
    try:
        logger.info(f"Calculating savings for {len(request.opportunities)} opportunities")
        
        # Convert inputs to TaxLossOpportunity objects
        opportunities = []
        for opp_input in request.opportunities:
            purchase_date = datetime.strptime(opp_input.purchase_date, "%Y-%m-%d") if opp_input.purchase_date else datetime.now()
            
            holding = PortfolioHolding(
                stock_name=opp_input.stock_name,
                symbol=opp_input.symbol,
                quantity=opp_input.quantity,
                purchase_date=purchase_date,
                purchase_price=opp_input.purchase_price,
                current_price=opp_input.current_price
            )
            
            opportunity = TaxLossOpportunity(
                holding=holding,
                unrealized_loss=opp_input.unrealized_loss,
                loss_percentage=(opp_input.unrealized_loss / holding.cost_basis * 100) if holding.cost_basis > 0 else 0,
                eligible_for_harvesting=True
            )
            opportunities.append(opportunity)
        
        # Calculate savings
        calculator = TaxSavingsCalculatorAgent()
        result = calculator.calculate_savings(
            opportunities,
            applicable_tax_rate=request.tax_rate,
            annual_income=request.annual_income
        )
        
        report = calculator.generate_savings_report(result)
        
        return {
            "status": "success",
            "message": "Tax savings calculated successfully",
            "data": {
                "summary": {
                    "transactions_harvested": report["summary"]["transactions_harvested"],
                    "total_loss_harvested": report["summary"]["total_loss_harvested"],
                    "applicable_tax_rate": report["summary"]["applicable_tax_rate"]
                },
                "immediate_impact": report["immediate_impact"],
                "10_year_projection": report["10_year_projection"],
                "assumptions": report["assumptions"]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Savings calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check for savings calculation service."""
    return {"status": "OK", "service": "tax_savings_calculator"}
