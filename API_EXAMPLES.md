"""
API Usage Examples - cURL Commands & Python Snippets
"""

# ============================================================================
# CURL EXAMPLES
# ============================================================================

CURL_EXAMPLES = """
# 1. HEALTH CHECK
curl -X GET http://localhost:8000/health

# 2. PARSE PORTFOLIO (CSV FILE)
curl -X POST http://localhost:8000/api/v1/parse_portfolio \\
  -F "file=@portfolio.csv"

# 3. IDENTIFY TAX LOSS OPPORTUNITIES
curl -X POST http://localhost:8000/api/v1/identify_loss \\
  -H "Content-Type: application/json" \\
  -d '{
    "holdings": [
      {
        "stock_name": "TCS",
        "symbol": "TCS",
        "quantity": 100,
        "purchase_date": "2023-01-15",
        "purchase_price": 3500,
        "current_price": 3200
      }
    ],
    "top_n": 10
  }'

# 4. CHECK COMPLIANCE
curl -X POST http://localhost:8000/api/v1/check_compliance \\
  -H "Content-Type: application/json" \\
  -d '{
    "symbol": "TCS",
    "stock_name": "TCS",
    "quantity": 100,
    "purchase_price": 3500,
    "current_price": 3200,
    "purchase_date": "2023-01-15",
    "unrealized_loss": 30000
  }'

# 5. GET REPLACEMENT RECOMMENDATIONS
curl -X POST http://localhost:8000/api/v1/recommend_replace \\
  -H "Content-Type: application/json" \\
  -d '{
    "symbol": "TCS",
    "stock_name": "TCS",
    "quantity": 100,
    "purchase_price": 3500,
    "current_price": 3200,
    "purchase_date": "2023-01-15",
    "unrealized_loss": 30000
  }'

# 6. CALCULATE TAX SAVINGS
curl -X POST http://localhost:8000/api/v1/calculate_savings \\
  -H "Content-Type: application/json" \\
  -d '{
    "opportunities": [
      {
        "symbol": "TCS",
        "stock_name": "TCS",
        "quantity": 100,
        "purchase_price": 3500,
        "current_price": 3200,
        "purchase_date": "2023-01-15",
        "unrealized_loss": 30000
      }
    ],
    "annual_income": 500000,
    "tax_rate": null
  }'

# 7. GET EXPLAINABILITY
curl -X POST http://localhost:8000/api/v1/explain \\
  -H "Content-Type: application/json" \\
  -d '{
    "symbol": "TCS",
    "stock_name": "TCS",
    "quantity": 100,
    "purchase_price": 3500,
    "current_price": 3200,
    "purchase_date": "2023-01-15",
    "unrealized_loss": 30000,
    "eligible_for_harvesting": true
  }'
"""

# ============================================================================
# PYTHON SNIPPETS
# ============================================================================

PYTHON_SNIPPETS = """
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. HEALTH CHECK
def check_health():
    response = requests.get(f"{BASE_URL}/health")
    print(response.json())

# 2. PARSE PORTFOLIO
def parse_portfolio(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/api/v1/parse_portfolio",
            files={'file': f}
        )
    return response.json()

# 3. IDENTIFY TAX LOSSES
def identify_losses():
    payload = {
        "holdings": [
            {
                "stock_name": "TCS",
                "symbol": "TCS",
                "quantity": 100,
                "purchase_date": "2023-01-15",
                "purchase_price": 3500,
                "current_price": 3200
            }
        ],
        "top_n": 10
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/identify_loss",
        json=payload
    )
    return response.json()

# 4. CHECK COMPLIANCE
def check_compliance():
    payload = {
        "symbol": "TCS",
        "stock_name": "TCS",
        "quantity": 100,
        "purchase_price": 3500,
        "current_price": 3200,
        "purchase_date": "2023-01-15",
        "unrealized_loss": 30000
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/check_compliance",
        json=payload
    )
    return response.json()

# 5. GET RECOMMENDATIONS
def get_recommendations():
    payload = {
        "symbol": "TCS",
        "stock_name": "TCS",
        "quantity": 100,
        "purchase_price": 3500,
        "current_price": 3200,
        "purchase_date": "2023-01-15",
        "unrealized_loss": 30000
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/recommend_replace",
        json=payload
    )
    return response.json()

# 6. CALCULATE SAVINGS
def calculate_savings():
    payload = {
        "opportunities": [
            {
                "symbol": "TCS",
                "stock_name": "TCS",
                "quantity": 100,
                "purchase_price": 3500,
                "current_price": 3200,
                "purchase_date": "2023-01-15",
                "unrealized_loss": 30000
            }
        ],
        "annual_income": 500000,
        "tax_rate": None
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/calculate_savings",
        json=payload
    )
    return response.json()

# 7. GET EXPLANATION
def get_explanation():
    payload = {
        "symbol": "TCS",
        "stock_name": "TCS",
        "quantity": 100,
        "purchase_price": 3500,
        "current_price": 3200,
        "purchase_date": "2023-01-15",
        "unrealized_loss": 30000,
        "eligible_for_harvesting": True
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/explain",
        json=payload
    )
    return response.json()

# 8. FULL WORKFLOW EXAMPLE
def full_workflow():
    # Check health
    print("1. Health Check:")
    check_health()
    
    # Parse portfolio
    print("\\n2. Parse Portfolio:")
    portfolio = parse_portfolio("portfolio.csv")
    print(json.dumps(portfolio, indent=2))
    
    # Identify losses
    print("\\n3. Identify Tax Losses:")
    losses = identify_losses()
    print(json.dumps(losses, indent=2))
    
    # Check compliance
    print("\\n4. Check Compliance:")
    compliance = check_compliance()
    print(json.dumps(compliance, indent=2))
    
    # Get recommendations
    print("\\n5. Get Recommendations:")
    recommendations = get_recommendations()
    print(json.dumps(recommendations, indent=2))
    
    # Calculate savings
    print("\\n6. Calculate Savings:")
    savings = calculate_savings()
    print(json.dumps(savings, indent=2))
    
    # Get explanation
    print("\\n7. Get Explanation:")
    explanation = get_explanation()
    print(json.dumps(explanation, indent=2))

if __name__ == "__main__":
    full_workflow()
"""

# ============================================================================
# JAVASCRIPT/FETCH EXAMPLES
# ============================================================================

JAVASCRIPT_EXAMPLES = """
const BASE_URL = "http://localhost:8000";

// 1. HEALTH CHECK
async function checkHealth() {
  const response = await fetch(`${BASE_URL}/health`);
  const data = await response.json();
  console.log(data);
}

// 2. PARSE PORTFOLIO
async function parsePortfolio(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/api/v1/parse_portfolio`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  return data;
}

// 3. IDENTIFY TAX LOSSES
async function identifyLosses() {
  const payload = {
    holdings: [
      {
        stock_name: "TCS",
        symbol: "TCS",
        quantity: 100,
        purchase_date: "2023-01-15",
        purchase_price: 3500,
        current_price: 3200
      }
    ],
    top_n: 10
  };
  
  const response = await fetch(`${BASE_URL}/api/v1/identify_loss`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  return data;
}

// 4. CHECK COMPLIANCE
async function checkCompliance() {
  const payload = {
    symbol: "TCS",
    stock_name: "TCS",
    quantity: 100,
    purchase_price: 3500,
    current_price: 3200,
    purchase_date: "2023-01-15",
    unrealized_loss: 30000
  };
  
  const response = await fetch(`${BASE_URL}/api/v1/check_compliance`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  return data;
}

// 5. ERROR HANDLING
async function safeApiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// 6. USAGE IN REACT
import React, { useState } from 'react';

function TaxLossHarvester() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  
  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const data = await identifyLosses();
      setResults(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Portfolio'}
      </button>
      {results && <pre>{JSON.stringify(results, null, 2)}</pre>}
    </div>
  );
}

export default TaxLossHarvester;
"""

# ============================================================================
# RESPONSE EXAMPLES
# ============================================================================

RESPONSE_EXAMPLES = """
// 1. HEALTH CHECK RESPONSE
{
  "status": "OK",
  "service": "Tax-Loss Harvesting Backend",
  "version": "1.0.0"
}

// 2. IDENTIFY LOSS RESPONSE
{
  "status": "success",
  "message": "Identified 2 top opportunities",
  "data": {
    "total_opportunities": 3,
    "opportunities": [
      {
        "symbol": "TCS",
        "stock_name": "Tata Consultancy Services",
        "quantity": 100,
        "purchase_price": 3500,
        "current_price": 3200,
        "unrealized_loss": 30000,
        "loss_percentage": 8.57,
        "eligible": true,
        "reason": "Eligible for tax-loss harvesting",
        "rank": 1
      }
    ],
    "summary": {
      "total_unrealized_loss": 45000,
      "eligible_loss": 40000,
      "top_opportunities_loss": 40000,
      "total_holdings_analyzed": 3,
      "eligible_holdings": 2,
      "ineligible_count": 1
    }
  },
  "timestamp": "2024-01-15T14:32:45.123456"
}

// 3. COMPLIANCE CHECK RESPONSE
{
  "status": "success",
  "message": "Compliance check completed for TCS",
  "data": {
    "symbol": "TCS",
    "is_compliant": true,
    "status": "compliant",
    "risk_level": "low",
    "explanation": "Transaction complies with Indian tax regulations.",
    "suggested_fix": null,
    "regulation_references": ["Section 45", "Section 71"]
  },
  "timestamp": "2024-01-15T14:32:45.123456"
}

// 4. TAX SAVINGS RESPONSE
{
  "status": "success",
  "message": "Tax savings calculated successfully",
  "data": {
    "summary": {
      "transactions_harvested": 1,
      "total_loss_harvested": "$30,000.00",
      "applicable_tax_rate": "30%"
    },
    "immediate_impact": {
      "tax_savings": "$9,000.00",
      "effective_return": "30.0%"
    },
    "10_year_projection": {
      "initial_investment": "$9,000.00",
      "projected_value": "$18,542.35",
      "value_increase": "$9,542.35",
      "cagr": "7.84%"
    },
    "assumptions": {
      "annual_return_mean_percent": 8,
      "annual_return_std_percent": 3,
      "inflation_rate_percent": 4,
      "projection_years": 10,
      "monte_carlo_runs": 1000,
      "tax_rate_applied_percent": 30
    }
  },
  "timestamp": "2024-01-15T14:32:45.123456"
}

// 5. ERROR RESPONSE
{
  "status": "error",
  "message": "Failed to parse portfolio",
  "error_type": "FileNotFoundError",
  "timestamp": "2024-01-15T14:32:45.123456"
}
"""

# ============================================================================
# INTEGRATION EXAMPLES
# ============================================================================

INTEGRATION_EXAMPLES = """
# FASTAPI + FRONTEND INTEGRATION

## React Integration Example

1. Install dependencies:
   npm install axios

2. Create API client:
   // api/client.ts
   import axios from 'axios';

   const API_BASE = 'http://localhost:8000/api/v1';

   export const apiClient = axios.create({
     baseURL: API_BASE,
     headers: {
       'Content-Type': 'application/json'
     }
   });

   export const parsePortfolio = (file: File) => {
     const formData = new FormData();
     formData.append('file', file);
     return apiClient.post('/parse_portfolio', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     });
   };

   export const identifyLosses = (holdings: any[]) => {
     return apiClient.post('/identify_loss', {
       holdings,
       top_n: 10
     });
   };

3. Use in component:
   import { identifyLosses } from './api/client';

   function Portfolio() {
     const [losses, setLosses] = useState([]);
     
     const handleAnalyze = async () => {
       const result = await identifyLosses(holdings);
       setLosses(result.data.opportunities);
     };
     
     return (
       <button onClick={handleAnalyze}>Analyze</button>
     );
   }


## MOBILE APP INTEGRATION (React Native)

import { fetch as fetchAPI } from 'react-native';

const API_BASE = 'http://your-server.com/api/v1';

async function analyzeTaxLosses(portfolio) {
  try {
    const response = await fetchAPI(`${API_BASE}/identify_loss`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        holdings: portfolio,
        top_n: 10
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}
"""

# ============================================================================
# DEPLOYMENT EXAMPLES
# ============================================================================

DEPLOYMENT_EXAMPLES = """
# 1. DOCKER DEPLOYMENT

Dockerfile:
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV GROQ_API_KEY=your_key_here
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0"]

Build & Run:
docker build -t tax-harvester .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key tax-harvester


# 2. HEROKU DEPLOYMENT

Procfile:
web: gunicorn backend.main:app

Deploy:
git push heroku main


# 3. AWS DEPLOYMENT

requirements.txt should include:
gunicorn==21.2.0

Then use Elastic Beanstalk or Lambda


# 4. DOCKER COMPOSE

docker-compose.yml:
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      GROQ_API_KEY: ${GROQ_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

Run with:
docker-compose up
"""

if __name__ == "__main__":
    print("API USAGE EXAMPLES")
    print("="*60)
    print("\n1. CURL EXAMPLES:")
    print(CURL_EXAMPLES)
    print("\n2. PYTHON EXAMPLES:")
    print(PYTHON_SNIPPETS)
    print("\n3. JAVASCRIPT/FETCH:")
    print(JAVASCRIPT_EXAMPLES)
    print("\n4. RESPONSE EXAMPLES:")
    print(RESPONSE_EXAMPLES)
