# Project Structure - AlphaAgent

## Clean Structure Overview

```
AlphaAgent/
├── backend/
│   ├── core/
│   │   ├── multi_turn_debate_system.py    # Main debate engine (554 lines)
│   │   └── agent_orchestrator.py          # Legacy orchestrator (414 lines)
│   ├── agents/                             # Individual agent implementations
│   │   ├── compliance_checker.py
│   │   ├── explainability_agent.py
│   │   ├── orchestrator.py
│   │   ├── portfolio_parser.py
│   │   ├── replacement_recommender.py
│   │   ├── tax_loss_identifier.py
│   │   └── tax_savings_calculator.py
│   ├── routes/                             # FastAPI routes (optional)
│   │   ├── compliance.py
│   │   ├── explain.py
│   │   ├── portfolio.py
│   │   ├── recommend.py
│   │   ├── savings.py
│   │   └── tax_loss.py
│   ├── utils/                              # Utilities
│   │   ├── groq_client.py                 # LLM client
│   │   ├── market_data_fetcher.py         # Market data
│   │   ├── data_models.py                 # Data classes
│   │   ├── env.py                         # Environment
│   │   └── [others]
│   ├── config.py                           # Configuration
│   └── main.py                             # FastAPI app
├── data/
│   └── test_portfolios/                    # Test data
├── logs/
│   └── multi_turn_debates/                 # Debate logs
├── run_debate.py                           # Main entry point
├── test_multi_turn_debate.py               # Test suite
├── requirements.txt                        # Dependencies
├── README.md                               # Documentation
├── MULTI_TURN_DEBATE.md                    # Full API docs
├── DEPLOYMENT.md                           # Deployment guide
└── MONITORING.md                           # Monitoring guide
```

## Total Files: 33 Python files

### Main Components (2 files)
- `run_debate.py` - Main entry point for portfolio debates
- `test_multi_turn_debate.py` - Test suite

### Backend Core (2 files)
- `backend/core/multi_turn_debate_system.py` - Primary debate engine
- `backend/core/agent_orchestrator.py` - Legacy orchestrator

### Backend Agents (7 files)
Individual specialized agents for portfolio analysis

### Backend Routes (6 files)
FastAPI REST endpoints (optional, for API deployment)

### Backend Utils (10 files)
Utilities for LLM, market data, logging, etc.

### Backend Config (3 files)
- `backend/config.py` - Configuration
- `backend/main.py` - FastAPI application
- `backend/__init__.py`

## Files Removed (13 files)

### Redundant Test Files (5)
- `test_portfolio_debate.py` - Superseded by multi_turn
- `test_llm_debate_indian.py` - Superseded by multi_turn
- `test_indian_portfolio.py` - Superseded by multi_turn
- `test_debate_system.py` - Old test
- `simple_test.py` - Simple test

### Duplicate Entry Points (4)
- `app.py` - Duplicate
- `main.py` - Duplicate
- `crew.py` - Old crewAI implementation
- `run_server.py` - Duplicate server

### Redundant Utilities (2)
- `comprehensive_test.py` - Combined into test_multi_turn_debate.py
- `integration_test.py` - Combined into test_multi_turn_debate.py
- `verify_production_ready.py` - Not needed

### Reference Scripts (1)
- `multi_turn_reference.py` - Documentation only

### Superseded Backend Core (2)
- `backend/core/portfolio_debate_system.py` - Single-round (superseded)
- `backend/core/llm_debate_system.py` - Individual stock (superseded)

### Redundant Documentation (4)
- `IMPLEMENTATION_COMPLETE.md` - Consolidated into README
- `MULTI_TURN_SUMMARY.md` - Consolidated into MULTI_TURN_DEBATE.md
- `QUICK_START_DEBATE.md` - Consolidated into README
- `AGENT_DEBATE_SYSTEM.md` - Consolidated into MULTI_TURN_DEBATE.md

## What's Working

✅ Multi-turn debate system (`backend/core/multi_turn_debate_system.py`)
✅ Main entry point (`run_debate.py`)
✅ Test suite (`test_multi_turn_debate.py`)
✅ All backend utilities (Groq client, market data, etc.)
✅ FastAPI routes (optional, for API deployment)
✅ Configuration and logging
✅ Complete documentation (README + MULTI_TURN_DEBATE.md)

## How to Use

### Run Debate
```bash
python run_debate.py
```

### Run Tests
```bash
python test_multi_turn_debate.py
```

### Start API Server (Optional)
```bash
python -m uvicorn backend.main:app --reload
```

## Key Files to Understand

1. **run_debate.py** - Start here, main entry point
2. **backend/core/multi_turn_debate_system.py** - Core debate engine
3. **backend/utils/groq_client.py** - LLM interface
4. **test_multi_turn_debate.py** - Example usage
5. **README.md** - Quick reference
6. **MULTI_TURN_DEBATE.md** - Complete API documentation

## Next Steps

1. ✅ Clean structure complete
2. ✅ Documentation updated
3. ✅ Tests working
4. → Ready for production deployment
5. → Scale with more agents or custom logic
