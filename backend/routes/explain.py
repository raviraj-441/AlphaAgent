"""
Explainability endpoint.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from datetime import datetime

from backend.utils.data_models import PortfolioHolding, TaxLossOpportunity
from backend.utils.groq_client import GroqLLMClient
from backend.agents.explainability_agent import ExplainabilityAgent

logger = logging.getLogger(__name__)
router = APIRouter()


class ExplainabilityRequest(BaseModel):
    """Request model for explainability."""
    symbol: str
    stock_name: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: str
    unrealized_loss: float
    eligible_for_harvesting: bool


@router.post("/explain")
async def explain(request: ExplainabilityRequest = Body(...)):
    """
    Get SHAP-based explanation for tax-loss recommendation.
    
    Args:
        request: ExplainabilityRequest
    
    Returns:
        SHAP explanation and counterfactual
    """
    try:
        logger.info(f"Generating explanation for {request.symbol}")
        
        # Create opportunity object
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
            eligible_for_harvesting=request.eligible_for_harvesting
        )
        
        # Generate explanations
        llm_client = GroqLLMClient()
        explainer = ExplainabilityAgent(llm_client)
        
        # Get SHAP explanation
        shap_exp = explainer.get_shap_explanation(opportunity)
        
        # Get counterfactual explanation
        counterfactual = explainer.get_counterfactual_explanation(opportunity)
        
        # Get decision tree
        decision_tree = explainer.create_decision_tree_explanation(opportunity)
        
        return {
            "status": "success",
            "message": f"Generated explanation for {request.symbol}",
            "data": {
                "symbol": request.symbol,
                "recommendation": "HARVEST" if request.eligible_for_harvesting else "HOLD",
                "shap_explanation": {
                    "feature_importance": shap_exp.get("feature_importance", []),
                    "base_value": shap_exp.get("base_value"),
                    "predicted_value": shap_exp.get("predicted_value")
                },
                "counterfactual": counterfactual,
                "decision_path": decision_tree.get("root"),
                "confidence": decision_tree.get("confidence")
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Explainability generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/batch")
async def explain_batch(
    symbols: List[str] = Query(...)
):
    """
    Get explanations for multiple symbols (demo endpoint).
    
    Args:
        symbols: List of stock symbols
    
    Returns:
        Explanations for all symbols
    """
    try:
        logger.info(f"Generating batch explanations for {len(symbols)} symbols")
        
        return {
            "status": "success",
            "message": f"Batch explanation endpoint. Provide multiple opportunities via POST.",
            "data": {
                "symbols_provided": symbols,
                "total": len(symbols)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Batch explanation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check for explainability service."""
    return {"status": "OK", "service": "explainability_agent"}
