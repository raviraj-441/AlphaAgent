"""
Portfolio parsing endpoint.
"""

import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from backend.utils.groq_client import GroqLLMClient
from backend.agents.portfolio_parser import PortfolioParserAgent

logger = logging.getLogger(__name__)
router = APIRouter()


class PortfolioResponse(BaseModel):
    """Response model for portfolio parsing."""
    status: str
    message: str
    data: dict
    timestamp: str


@router.post("/parse_portfolio")
async def parse_portfolio(file: UploadFile = File(...)):
    """
    Parse uploaded portfolio file.
    
    Args:
        file: Portfolio file (CSV, PDF, or Excel)
    
    Returns:
        Parsed portfolio data
    """
    try:
        logger.info(f"Parsing portfolio file: {file.filename}")
        
        # Validate file type
        file_type = None
        if file.filename.endswith('.csv'):
            file_type = 'csv'
        elif file.filename.endswith('.pdf'):
            file_type = 'pdf'
        elif file.filename.endswith(('.xlsx', '.xls')):
            file_type = 'excel'
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use CSV, PDF, or Excel."
            )
        
        # Read file data
        file_data = await file.read()
        
        # Parse portfolio
        llm_client = GroqLLMClient()
        parser = PortfolioParserAgent(llm_client)
        result = parser.parse_portfolio(file_data, file_type)
        
        from datetime import datetime
        
        return {
            "status": result.get("status", "error"),
            "message": result.get("message", ""),
            "data": {
                "total_holdings": result.get("total_holdings", 0),
                "holdings": [
                    {
                        "stock_name": h.stock_name if hasattr(h, 'stock_name') else str(h),
                        "symbol": h.symbol if hasattr(h, 'symbol') else 'N/A',
                        "quantity": h.quantity if hasattr(h, 'quantity') else 0,
                        "purchase_price": h.purchase_price if hasattr(h, 'purchase_price') else 0,
                        "current_price": h.current_price if hasattr(h, 'current_price') else 0,
                        "cost_basis": h.cost_basis if hasattr(h, 'cost_basis') else 0,
                        "current_value": h.current_value if hasattr(h, 'current_value') else 0,
                        "unrealized_gain_loss": h.unrealized_gain_loss if hasattr(h, 'unrealized_gain_loss') else 0
                    }
                    for h in result.get("holdings", [])
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio parsing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check for portfolio service."""
    return {"status": "OK", "service": "portfolio_parser"}
