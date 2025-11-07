"""
Main FastAPI application for tax-loss harvesting backend.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# Load environment variables from .env file - must be before other imports
load_dotenv()

# Import path utilities
from backend.utils.paths import get_tax_docs_dir
from backend.utils.env import EnvManager
from backend.utils.prometheus_metrics import PrometheusMiddleware, get_metrics

# Ensure environment is loaded
EnvManager.load_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes
from backend.routes import (
    portfolio, tax_loss, compliance, recommend, savings, explain
)
from backend.utils.vector_store import get_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting up Tax-Loss Harvesting Backend")
    
    # Initialize vector store and load documents
    try:
        vs = get_vector_store()
        tax_docs_dir = get_tax_docs_dir()
        vs.load_income_tax_documents(str(tax_docs_dir))
        logger.info("Vector store initialized and documents loaded")
    except Exception as e:
        logger.warning(f"Vector store initialization skipped: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Tax-Loss Harvesting Backend")


# Create FastAPI app
app = FastAPI(
    title="Tax-Loss Harvesting Multi-Agent System",
    description="Backend for intelligent tax-loss harvesting optimization using multi-agent LLM system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "OK",
        "service": "Tax-Loss Harvesting Backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "message": "Tax-Loss Harvesting Multi-Agent System",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "parse_portfolio": "/parse_portfolio",
            "identify_loss": "/identify_loss",
            "check_compliance": "/check_compliance",
            "recommend_replace": "/recommend_replace",
            "calculate_savings": "/calculate_savings",
            "explain": "/explain",
            "orchestrate": "/orchestrate"
        }
    }


# Include routers
app.include_router(portfolio.router, prefix="/api/v1", tags=["Portfolio"])
app.include_router(tax_loss.router, prefix="/api/v1", tags=["Tax Loss"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
app.include_router(recommend.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(savings.router, prefix="/api/v1", tags=["Savings"])
app.include_router(explain.router, prefix="/api/v1", tags=["Explanations"])


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "status": "error",
        "message": exc.detail,
        "error_type": "HTTPException"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return {
        "status": "error",
        "message": "Internal server error",
        "error_type": type(exc).__name__
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
