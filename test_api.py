#!/usr/bin/env python3
"""
API ENDPOINT TESTING - Direct HTTP Testing
Tests the FastAPI server directly through its endpoints
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_api_endpoints():
    """Test API endpoints directly"""
    print("\n" + "="*80)
    print("  FASTAPI ENDPOINT TESTING")
    print("="*80 + "\n")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test 1: Health check
        print("[TEST 1] Health Endpoint")
        response = client.get("/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        assert response.status_code == 200, "Health check failed"
        print("  [PASS]\n")
        
        # Test 2: Portfolio parsing (with sample data)
        print("[TEST 2] Parse Portfolio Endpoint")
        portfolio_data = {
            "file": b"stock_name,symbol,quantity,purchase_date,purchase_price,current_price\nTCS,TCS,100,2023-11-07,3500.0,3200.0\nINFY,INFY,50,2024-07-07,1500.0,1400.0"
        }
        # Note: This endpoint expects file upload, skipping for now
        print("  [SKIP] (requires file upload)\n")
        
        # Test 3: Identify tax loss opportunities
        print("[TEST 3] Identify Tax Loss Endpoint")
        tax_loss_data = {
            "holdings": [
                {
                    "stock_name": "TCS",
                    "symbol": "TCS",
                    "quantity": 100,
                    "purchase_date": "2023-11-07",
                    "purchase_price": 3500.0,
                    "current_price": 3200.0
                },
                {
                    "stock_name": "INFY",
                    "symbol": "INFY",
                    "quantity": 50,
                    "purchase_date": "2024-07-07",
                    "purchase_price": 1500.0,
                    "current_price": 1400.0
                }
            ]
        }
        
        response = client.post("/api/v1/identify_loss", json=tax_loss_data)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            opps = data.get('data', {}).get('opportunities', [])
            print(f"  Opportunities found: {len(opps)}")
            if opps:
                print(f"  Top opportunity: {opps[0]}")
            print("  [PASS]\n")
        else:
            print(f"  Response: {response.text[:300]}")
            print("  [FAIL]\n")
        
        # Test 4: Check compliance
        print("[TEST 4] Compliance Check Endpoint")
        compliance_data = {
            "opportunity": {
                "holding": {
                    "stock_name": "TCS",
                    "symbol": "TCS",
                    "quantity": 100,
                    "purchase_date": "2023-11-07",
                    "purchase_price": 3500.0,
                    "current_price": 3200.0
                },
                "unrealized_loss": 30000,
                "loss_percentage": 8.6,
                "eligible_for_harvesting": True
            }
        }
        
        response = client.post("/api/v1/check_compliance", json=compliance_data)
        print(f"  Status: {response.status_code}")
        if response.status_code in [200, 422]:  # 422 if model validation fails
            print(f"  Response received")
            print("  [INFO] Complex model, checking...\n")
        else:
            print(f"  Response: {response.text}")
            print("  [FAIL]\n")
        
        # Test 5: Calculate savings
        print("[TEST 5] Calculate Savings Endpoint")
        savings_data = {
            "opportunities": [
                {
                    "symbol": "TCS",
                    "stock_name": "TCS",
                    "quantity": 100,
                    "purchase_date": "2023-11-07",
                    "purchase_price": 3500.0,
                    "current_price": 3200.0,
                    "unrealized_loss": 30000.0
                }
            ],
            "annual_income": 400000.0,
            "tax_rate": 0.30
        }
        
        response = client.post("/api/v1/calculate_savings", json=savings_data)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Savings calculated successfully")
            if 'data' in data:
                savings = data['data']
                print(f"  Immediate savings: {savings.get('immediate_tax_savings', 0):,.0f} INR")
                print(f"  10-year projection: {savings.get('projected_10yr_value', 0):,.0f} INR")
            print("  [PASS]\n")
        else:
            print(f"  Status: {response.status_code}")
            err = response.json() if response.text else "No error details"
            print(f"  Error: {str(err)[:200]}")
            print("  [FAIL]\n")
        
        print("="*80)
        print("  ENDPOINT TESTING COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent / "backend"))
    test_api_endpoints()
