"""
Tax loss identification endpoint.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime

from backend.utils.data_models import PortfolioHolding
from backend.agents.tax_loss_identifier import TaxLossIdentifierAgent

logger = logging.getLogger(__name__)
router = APIRouter()


class HoldingInput(BaseModel):
    """Portfolio holding input."""
    stock_name: str
    symbol: str
    quantity: float
    purchase_date: str
    purchase_price: float
    current_price: float


class IdentifyLossRequest(BaseModel):
    """Request model for tax loss identification."""
    holdings: List[HoldingInput]
    top_n: int = 10


@router.post("/identify_loss")
async def identify_loss(request: IdentifyLossRequest = Body(...)):
    """
    Identify top tax-loss harvesting opportunities.
    
    Args:
        request: IdentifyLossRequest with holdings
    
    Returns:
        Top opportunities with calculations
    """
    try:
        logger.info(f"Identifying tax loss opportunities for {len(request.holdings)} holdings")
        
        # Convert input to PortfolioHolding objects
        holdings = []
        for h in request.holdings:
            try:
                purchase_date = datetime.strptime(h.purchase_date, "%Y-%m-%d")
            except ValueError:
                purchase_date = datetime.now()
            
            holding = PortfolioHolding(
                stock_name=h.stock_name,
                symbol=h.symbol,
                quantity=h.quantity,
                purchase_date=purchase_date,
                purchase_price=h.purchase_price,
                current_price=h.current_price
            )
            holdings.append(holding)
        
        # Identify opportunities
        agent = TaxLossIdentifierAgent()
        result = agent.identify_opportunities(holdings, top_n=request.top_n)
        
        return {
            "status": result.get("status", "success"),
            "message": result.get("message", ""),
            "data": {
                "total_opportunities": result.get("total_opportunities", 0),
                "opportunities": [
                    {
                        "symbol": opp.holding.symbol,
                        "stock_name": opp.holding.stock_name,
                        "quantity": opp.holding.quantity,
                        "purchase_price": opp.holding.purchase_price,
                        "current_price": opp.holding.current_price,
                        "unrealized_loss": round(opp.unrealized_loss, 2),
                        "loss_percentage": round(opp.loss_percentage, 2),
                        "eligible": opp.eligible_for_harvesting,
                        "reason": opp.reason,
                        "rank": opp.rank
                    }
                    for opp in result.get("opportunities", [])
                ],
                "summary": result.get("summary", {})
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Tax loss identification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check for tax loss service."""
    return {"status": "OK", "service": "tax_loss_identifier"}
