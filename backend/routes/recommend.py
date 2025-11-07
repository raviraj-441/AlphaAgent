"""
Replacement recommendation endpoint.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime

from backend.utils.data_models import PortfolioHolding, TaxLossOpportunity
from backend.utils.groq_client import GroqLLMClient
from backend.agents.replacement_recommender import ReplacementRecommenderAgent

logger = logging.getLogger(__name__)
router = APIRouter()


class RecommendationRequest(BaseModel):
    """Request model for replacement recommendations."""
    symbol: str
    stock_name: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: str
    unrealized_loss: float


@router.post("/recommend_replace")
async def recommend_replacement(request: RecommendationRequest = Body(...)):
    """
    Recommend replacement securities using correlation and semantic analysis.
    
    Args:
        request: RecommendationRequest
    
    Returns:
        List of recommended replacement securities
    """
    try:
        logger.info(f"Finding replacements for {request.symbol}")
        
        # Create holding and opportunity
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
        
        # Get recommendations
        llm_client = GroqLLMClient()
        recommender = ReplacementRecommenderAgent(llm_client)
        recommendations = recommender.recommend_replacements(opportunity)
        
        return {
            "status": "success",
            "message": f"Found {len(recommendations)} replacement recommendations for {request.symbol}",
            "data": {
                "original_symbol": request.symbol,
                "replacements": [
                    {
                        "recommended_symbol": rec.recommended_symbol,
                        "correlation_score": round(rec.correlation_score, 3),
                        "semantic_similarity": round(rec.semantic_similarity, 3),
                        "risk_profile_match": round(rec.risk_profile_match, 3),
                        "reason": rec.reason
                    }
                    for rec in recommendations
                ],
                "total_recommendations": len(recommendations)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check for recommendation service."""
    return {"status": "OK", "service": "replacement_recommender"}
