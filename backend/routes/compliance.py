"""
Compliance checking endpoint.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime

from backend.utils.data_models import PortfolioHolding, TaxLossOpportunity
from backend.utils.groq_client import GroqLLMClient
from backend.agents.compliance_checker import RegulatoryComplianceAgent

logger = logging.getLogger(__name__)
router = APIRouter()


class ComplianceCheckRequest(BaseModel):
    """Request model for compliance check."""
    symbol: str
    stock_name: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: str
    unrealized_loss: float


@router.post("/check_compliance")
async def check_compliance(request: ComplianceCheckRequest = Body(...)):
    """
    Check tax-loss harvesting compliance with Indian regulations.
    
    Args:
        request: ComplianceCheckRequest
    
    Returns:
        Compliance check result
    """
    try:
        logger.info(f"Checking compliance for {request.symbol}")
        
        # Create holding and opportunity objects
        purchase_date = datetime.strptime(request.purchase_date, "%Y-%m-%d") if request.purchase_date else datetime.now()
        
        holding = PortfolioHolding(
            stock_name=request.stock_name,
            symbol=request.symbol,
            quantity=request.quantity,
            purchase_date=purchase_date,
            purchase_price=request.purchase_price,
            current_price=request.current_price
        )
        
        opportunity = TaxLossOpportunity(
            holding=holding,
            unrealized_loss=request.unrealized_loss,
            loss_percentage=(request.unrealized_loss / holding.cost_basis * 100) if holding.cost_basis > 0 else 0,
            eligible_for_harvesting=True
        )
        
        # Check compliance
        llm_client = GroqLLMClient()
        checker = RegulatoryComplianceAgent(llm_client)
        result = checker.check_compliance(opportunity)
        
        return {
            "status": "success",
            "message": f"Compliance check completed for {request.symbol}",
            "data": {
                "symbol": request.symbol,
                "is_compliant": result.is_compliant,
                "status": result.status.value,
                "risk_level": result.risk_level,
                "explanation": result.explanation,
                "suggested_fix": result.suggested_fix,
                "regulation_references": result.regulation_references
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Compliance check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check for compliance service."""
    return {"status": "OK", "service": "compliance_checker"}
