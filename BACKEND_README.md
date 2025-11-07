# Tax-Loss Harvesting Multi-Agent LLM System

A sophisticated backend for intelligent tax-loss harvesting optimization using multiple coordinated LLM agents with negotiation capabilities.

## 🎯 Overview

This system leverages a multi-agent architecture to provide comprehensive tax-loss harvesting recommendations. It combines:

- **Portfolio Parsing Agent**: Extracts holdings from CSV, PDF, or Excel files
- **Tax Loss Identifier Agent**: Identifies optimal harvesting opportunities using FIFO accounting
- **Regulatory Compliance Agent**: Validates against Indian tax law using RAG and ChromaDB
- **Replacement Recommender Agent**: Suggests alternative securities using correlation and semantic analysis
- **Tax Savings Calculator Agent**: Projects immediate and 10-year tax savings using Monte Carlo simulation
- **Explainability Agent**: Provides SHAP-based explanations and counterfactuals
- **Agent Orchestrator**: Coordinates agents through multi-iteration negotiation loops

## ✨ Features

### 1. **Modular Architecture**
```
backend/
├── main.py                 # FastAPI application
├── agents/                 # Individual agent implementations
│   ├── portfolio_parser.py
│   ├── tax_loss_identifier.py
│   ├── compliance_checker.py
│   ├── replacement_recommender.py
│   ├── tax_savings_calculator.py
│   ├── explainability_agent.py
│   └── orchestrator.py
├── routes/                 # FastAPI endpoints
│   ├── portfolio.py
│   ├── tax_loss.py
│   ├── compliance.py
│   ├── recommend.py
│   ├── savings.py
│   └── explain.py
└── utils/                  # Shared utilities
    ├── groq_client.py      # Groq API integration
    ├── vector_store.py     # ChromaDB for tax law
    ├── data_models.py      # Pydantic models
    └── logging_config.py   # Centralized logging
```

### 2. **Groq LLM Integration**
- Uses Llama 3.1 70B model via Groq API
- Error handling and retry logic
- Batch processing support
- JSON response parsing

### 3. **RAG-Based Compliance Checking**
- ChromaDB vector store for Income Tax Act documents
- Semantic search for relevant regulations
- LLM-powered reasoning on compliance
- Wash-sale rule checking
- Exemption limit validation

### 4. **Advanced Recommendation**
- Correlation analysis (Pearson coefficient)
- Semantic similarity via LLM
- Risk profile matching
- Sector-peer analysis

### 5. **Financial Projections**
- 10-year Monte Carlo simulation
- Configurable annual return assumptions (mean 8%, std 3%)
- Inflation adjustment
- CAGR calculation
- Sensitivity analysis

### 6. **Explainability**
- SHAP value-based feature importance
- Counterfactual explanations via LLM
- Decision tree visualization
- Batch explanation generation

### 7. **Multi-Agent Negotiation**
- Up to 3 iteration rounds
- Proposal-based coordination
- Consensus tracking
- Detailed negotiation flow visualization

### 8. **Logging & Error Handling**
- Centralized logging with rotation
- Context-aware logging (user_id, session_id)
- Structured error responses
- Debug mode support

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Groq API key
- 2GB+ disk space (for ChromaDB)

### Installation

1. **Clone and setup:**
```bash
cd c:\Major_project\AlphaAgent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
$env:GROQ_API_KEY = "your_groq_api_key_here"
```

On Linux/Mac:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

3. **Prepare tax law documents (optional):**
```bash
mkdir -p data/income_tax_law_texts
# Add .txt or .md files with Income Tax Act sections
```

### Running the Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000/docs` for interactive API documentation

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns: `{"status": "OK", ...}`

### Portfolio Management
```
POST /api/v1/parse_portfolio
```
Upload and parse portfolio file (CSV, PDF, Excel)

### Tax Loss Analysis
```
POST /api/v1/identify_loss
```
Identify top tax-loss harvesting opportunities
```json
{
  "holdings": [
    {
      "stock_name": "Tata Consultancy Services",
      "symbol": "TCS",
      "quantity": 100,
      "purchase_date": "2023-01-15",
      "purchase_price": 3500,
      "current_price": 3200
    }
  ],
  "top_n": 10
}
```

### Compliance Check
```
POST /api/v1/check_compliance
```
Validate against Indian tax regulations

### Replacement Recommendations
```
POST /api/v1/recommend_replace
```
Get alternative securities based on correlation and semantics

### Tax Savings Calculation
```
POST /api/v1/calculate_savings
```
Project immediate and 10-year tax savings
```json
{
  "opportunities": [...],
  "annual_income": 500000,
  "tax_rate": null
}
```

### Explainability
```
POST /api/v1/explain
```
Get SHAP-based explanations and counterfactuals
```json
{
  "symbol": "TCS",
  "stock_name": "TCS",
  "quantity": 100,
  "purchase_price": 3500,
  "current_price": 3200,
  "purchase_date": "2023-01-15",
  "unrealized_loss": 30000,
  "eligible_for_harvesting": true
}
```

## 🏗️ Agent Details

### Portfolio Parser Agent
**Input:** Binary file data (CSV/PDF/Excel)
**Output:** Parsed holdings with prices and dates
**Methods:**
- `parse_portfolio()`: Main parsing method
- `_parse_csv()`: CSV-specific parsing with heuristics
- `_parse_pdf()`: PDF parsing using LLM reasoning
- `_parse_excel()`: Excel parsing with column detection

### Tax Loss Identifier Agent
**Input:** Portfolio holdings
**Output:** Top 10 tax-loss opportunities with rankings
**Features:**
- FIFO accounting method
- $100 minimum loss threshold
- 5% minimum loss percentage
- Wash-sale period awareness
**Methods:**
- `identify_opportunities()`: Main analysis
- `calculate_fifo_cost_basis()`: Cost calculation
- `estimate_tax_impact()`: Tax bracket-based savings

### Compliance Checker Agent
**Input:** Tax-loss opportunity
**Output:** Compliance status with explanation
**Features:**
- RAG-based regulation search
- LLM-powered reasoning
- Wash-sale rule checking
- Risk level assessment
**Methods:**
- `check_compliance()`: Single opportunity check
- `check_wash_sale_rule()`: Wash-sale validation
- `check_exemption_limits()`: Limit verification

### Replacement Recommender Agent
**Input:** Tax-loss opportunity
**Output:** Top 5 replacement securities
**Features:**
- Pearson correlation analysis
- Semantic similarity via LLM
- Risk profile matching
- Sector-peer detection
**Methods:**
- `recommend_replacements()`: Main recommendation
- `_calculate_correlation()`: Correlation score
- `_check_semantic_similarity()`: LLM semantic check

### Tax Savings Calculator Agent
**Input:** Harvested opportunities
**Output:** Immediate and projected savings
**Features:**
- Tax bracket estimation
- Monte Carlo simulation (1000 runs)
- 10-year projection
- Sensitivity analysis
- Scenario comparison
**Methods:**
- `calculate_savings()`: Main calculation
- `_monte_carlo_projection()`: Future value projection
- `sensitivity_analysis()`: Parameter sensitivity
- `compare_scenarios()`: Multi-scenario analysis

### Explainability Agent
**Input:** Opportunity and optional scenario
**Output:** SHAP explanation and counterfactual
**Features:**
- Mock SHAP value calculation
- Counterfactual explanation via LLM
- Decision tree visualization
- Batch processing
**Methods:**
- `get_shap_explanation()`: SHAP analysis
- `get_counterfactual_explanation()`: LLM counterfactual
- `explain_batch_recommendations()`: Batch processing
- `create_decision_tree_explanation()`: Decision path

### Agent Orchestrator
**Responsibilities:**
- Coordinates all agents
- Manages multi-iteration negotiation
- Tracks proposals and consensus
- Generates final recommendations
**Methods:**
- `orchestrate()`: Main orchestration
- `get_negotiation_flow()`: Flow visualization
- `visualize_negotiation_flow()`: Text-based flow

## 📊 Data Models

### PortfolioHolding
```python
@dataclass
class PortfolioHolding:
    stock_name: str
    symbol: str
    quantity: float
    purchase_date: datetime
    purchase_price: float
    current_price: float
    
    @property
    def cost_basis(self) -> float
    @property
    def current_value(self) -> float
    @property
    def unrealized_gain_loss(self) -> float
```

### TaxLossOpportunity
```python
@dataclass
class TaxLossOpportunity:
    holding: PortfolioHolding
    unrealized_loss: float
    loss_percentage: float
    eligible_for_harvesting: bool
    reason: str
    rank: int
```

### ComplianceCheckResult
```python
@dataclass
class ComplianceCheckResult:
    is_compliant: bool
    status: ComplianceStatus
    regulation_references: List[str]
    explanation: str
    risk_level: str  # low, medium, high
```

### TaxSavingsCalculation
```python
@dataclass
class TaxSavingsCalculation:
    transaction_count: int
    total_harvested_loss: float
    applicable_tax_rate: float
    immediate_tax_savings: float
    projected_10yr_value: float
    projected_value_increase: float
    monte_carlo_runs: int
    assumptions: Dict[str, Any]
```

## 🔐 Environment Variables

```
GROQ_API_KEY=your_groq_api_key_here
LOG_LEVEL=INFO
```

## 📝 Logging

Logs are stored in `./logs/` with:
- **Timestamp**: Precise execution time
- **Module name**: Source of the log
- **Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Function & line**: Exact code location
- **Context ID**: Session/user tracking

Example log:
```
2024-01-15 14:32:45 - [backend.agents.orchestrator] - INFO - orchestrate:123 - Starting orchestration for session abc123
```

## 🧪 Testing

Run tests:
```bash
pytest tests/ -v
```

Test with sample data:
```python
from backend.agents.tax_loss_identifier import TaxLossIdentifierAgent
from backend.utils.data_models import PortfolioHolding
from datetime import datetime

# Create sample holdings
holdings = [
    PortfolioHolding(
        stock_name="TCS",
        symbol="TCS",
        quantity=100,
        purchase_date=datetime(2023, 1, 15),
        purchase_price=3500,
        current_price=3200
    )
]

# Identify opportunities
agent = TaxLossIdentifierAgent()
result = agent.identify_opportunities(holdings)
print(result)
```

## 🎨 Response Format

All endpoints return consistent JSON:
```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "data": {
    // Endpoint-specific data
  },
  "timestamp": "2024-01-15T14:32:45.123456"
}
```

Error response:
```json
{
  "status": "error",
  "message": "Error description",
  "error_type": "ExceptionClassName",
  "timestamp": "2024-01-15T14:32:45.123456"
}
```

## 🚨 Error Handling

- **Groq API errors**: Retried with exponential backoff
- **File parsing errors**: Detailed error messages
- **LLM failures**: Graceful fallback with default values
- **Compliance check failures**: Marked as "needs_review"
- **Vector store issues**: Logged but system continues

## 🔄 Negotiation Flow Example

```
Iteration 1:
  ComplianceAgent: REVIEW - Compliance check completed. 8/10 compliant.
  ReplacementAgent: APPROVE - Identified replacements for 8 opportunities.
  SavingsAgent: APPROVE - Calculated immediate savings: $15,000

Iteration 2:
  Consensus REACHED
  Final Status: CONSENSUS REACHED
```

## 📈 Future Enhancements

- [ ] Real-time market data integration (Yahoo Finance)
- [ ] Machine learning-based feature importance
- [ ] Real SHAP integration with trained models
- [ ] Blockchain-based transaction verification
- [ ] Mobile app with real-time notifications
- [ ] Portfolio optimization using efficient frontier
- [ ] Advanced wash-sale prediction
- [ ] Tax loss carryforward tracking

## 📚 References

- [Indian Income Tax Act, 1961](https://incometaxindia.gov.in/)
- [Groq API Documentation](https://console.groq.com/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [SHAP Documentation](https://shap.readthedocs.io/)

## 📄 License

Proprietary - All rights reserved

## 👨‍💻 Author

Multi-Agent LLM System v1.0

## 📧 Support

For issues or questions, please contact support@taxharvesting.ai

---

**Last Updated**: January 2024
**Status**: Production Ready ✅
