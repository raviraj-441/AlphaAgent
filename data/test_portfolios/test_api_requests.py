"""
Test script for AlphaAgent FastAPI backend.

Usage: 
    python test_api_requests.py

Prerequisites:
    - Ensure your FastAPI server is running at http://127.0.0.1:8000
    - Sample portfolio and tax files are in: c:\Major_project\AlphaAgent\data\test_portfolios

This script will:
    - Upload sample_portfolio.csv to /parse_portfolio
    - Request identification of tax loss opportunities via /identify_loss
    - Check compliance for a sample transaction via /check_compliance
    - Request replacement recommendations via /recommend_replace
    - Compute savings via /calculate_savings
"""
import requests
import json
from pathlib import Path

BASE = "http://127.0.0.1:8000"

def upload_file(endpoint, file_path):
    """Upload a file to the specified endpoint."""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(f"{BASE}{endpoint}", files=files)
    print(f"POST {endpoint} -> {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)

def post_json(endpoint, data):
    """Send JSON data to the specified endpoint."""
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{BASE}{endpoint}", data=json.dumps(data), headers=headers)
    print(f"POST {endpoint} -> {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)

if __name__ == "__main__":
    sample1 = Path("c:\Major_project\AlphaAgent\data\test_portfolios\sample_portfolio.csv").absolute()
    sample2 = Path("c:\Major_project\AlphaAgent\data\test_portfolios\sample_portfolio_2lots.csv").absolute()
    taxfile = Path("c:\Major_project\AlphaAgent\data\test_portfolios\income_tax_law_excerpt_india.txt").absolute()

    print("=" * 60)
    print("AlphaAgent Backend Test Suite")
    print("=" * 60)

    print("\n[TEST 1] Uploading primary portfolio...")
    if sample1.exists():
        upload_file("/parse_portfolio", sample1)
    else:
        print(f"File not found: {sample1}")

    print("\n[TEST 2] Identifying tax loss opportunities...")
    post_json("/identify_loss", {"source": "uploaded_sample", "top_k": 10})

    print("\n[TEST 3] Checking compliance for RELIANCE transaction...")
    txn = {"symbol": "RELIANCE", "quantity": 5, "purchase_date": "2023-01-10", "sell_price": 2100.0}
    post_json("/check_compliance", {"transaction": txn, "tax_documents_path": str(taxfile)})

    print("\n[TEST 4] Requesting replacement recommendations...")
    post_json("/recommend_replace", {"symbol": "RELIANCE", "quantity": 5})

    print("\n[TEST 5] Calculating tax savings...")
    actions = [{"symbol":"RELIANCE","quantity":5,"sell_price":2100.0,"purchase_price":2200.0,"holding_period_days": 700}]
    post_json("/calculate_savings", {"actions": actions, "tax_rate": 0.20})

    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
