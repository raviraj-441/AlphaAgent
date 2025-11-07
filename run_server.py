#!/usr/bin/env python
"""Simple script to run the backend server."""

import sys
import os
import logging
import warnings

# Suppress ChromaDB deprecation warning
warnings.filterwarnings('ignore', category=DeprecationWarning)
logging.getLogger('chromadb').setLevel(logging.ERROR)

# Change to the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from backend.main import app
    
    print("Starting AlphaAgent Backend Server...")
    print("Server will be available at http://127.0.0.1:8000")
    print("API endpoints available at http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
