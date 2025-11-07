# Project Testing Guide

This guide explains how to test the AlphaAgent tax-loss harvesting backend using sample portfolio data and API requests.

## Test Data Location

All test data is located in `data/test_portfolios/`:
- `sample_portfolio.csv` - Primary portfolio with multiple lots across different symbols
- `sample_portfolio_2lots.csv` - Alternative portfolio for testing realized gains/losses
- `income_tax_law_excerpt_india.txt` - Indian tax law excerpt for RAG system testing
- `test_api_requests.py` - Python script to test API endpoints

## Generated Test Data Overview

### Portfolio 1 (sample_portfolio.csv)
- **RELIANCE**: 15 total shares (2 lots)
- **TCS**: 12 total shares (2 lots)
- **INFY**: 20 total shares (2 lots)
- **HDFC**: 12 shares (1 lot)
- **Total Unrealized P&L**: Multiple loss opportunities for tax-loss harvesting

### Portfolio 2 (sample_portfolio_2lots.csv)
- **AXISBANK**: 20 shares with unrealized loss
- **SBIN**: 30 shares with unrealized loss
- **LT**: 6 shares with minimal loss
- **Focus**: Testing FIFO accounting and realized gains/losses

## How to Run Tests

### Step 1: Start the FastAPI Backend Server

From the project root directory:
```bash
python quickstart.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Run the Test API Script

In another terminal, navigate to the project directory and run:
```bash
python data/test_portfolios/test_api_requests.py
```

### What the Test Script Does

The test script performs the following operations in sequence:

1. **Parse Portfolio** - Uploads `sample_portfolio.csv` to `/parse_portfolio`
2. **Identify Tax Loss** - Requests tax loss opportunities via `/identify_loss`
3. **Check Compliance** - Validates a RELIANCE transaction via `/check_compliance`
4. **Get Recommendations** - Requests replacement stock recommendations via `/recommend_replace`
5. **Calculate Savings** - Computes tax savings via `/calculate_savings`

## Expected Test Results

### Test 1: Parse Portfolio
- **Endpoint**: POST `/parse_portfolio`
- **Status**: 200 OK
- **Response**: Portfolio structure with parsed holdings

### Test 2: Identify Tax Loss
- **Endpoint**: POST `/identify_loss`
- **Status**: 200 OK
- **Expected**: Found tax loss opportunities (RELIANCE, HDFC losses detected)

### Test 3: Check Compliance
- **Endpoint**: POST `/check_compliance`
- **Status**: 200 OK
- **Expected**: Compliance check based on Indian tax law

### Test 4: Recommend Replace
- **Endpoint**: POST `/recommend_replace`
- **Status**: 200 OK
- **Expected**: Similar stock recommendations to replace RELIANCE

### Test 5: Calculate Savings
- **Endpoint**: POST `/calculate_savings`
- **Status**: 200 OK
- **Expected**: Tax savings calculation based on actions

## Tax Loss Opportunities

### Portfolio 1 Analysis

**Unrealized Losses:**
- **RELIANCE**: 
  - Lot 1: 10 shares @ 2200 → 2100 = -1000 INR loss
  - Lot 2: 5 shares @ 2300 → 2100 = -1000 INR loss
  - **Total**: -2000 INR loss potential

- **HDFC**: 
  - 12 shares @ 2600 → 2500 = -1200 INR loss

**Unrealized Gains:**
- **TCS**: +3200 INR
- **INFY**: +3000 INR

### Portfolio 2 Analysis

**Significant Unrealized Losses:**
- **AXISBANK**: 20 shares @ 750 → 680 = -1400 INR loss
- **SBIN**: 30 shares @ 520 → 480 = -1200 INR loss
- **LT**: 6 shares @ 2300 → 2250 = -300 INR loss

## Indian Income Tax Considerations

The test data includes an excerpt of Indian income tax rules:

1. **STCG** (< 12 months): 15% on gains
2. **LTCG** (> 12 months): 10% on gains > 1 lakh, exempt up to 1 lakh
3. **Capital Loss Offset**: Can offset against gains
4. **FIFO Accounting**: First-In-First-Out used for cost basis
5. **No Wash Sale Rule**: India doesn't have explicit wash sale rules

## Manual API Testing

If you prefer to test endpoints manually using curl or Postman:

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Parse Portfolio
```bash
curl -X POST -F "file=@data/test_portfolios/sample_portfolio.csv" \
  http://127.0.0.1:8000/parse_portfolio
```

### Identify Tax Loss
```bash
curl -X POST http://127.0.0.1:8000/identify_loss \
  -H "Content-Type: application/json" \
  -d '{"source": "uploaded_sample", "top_k": 10}'
```

## Troubleshooting

### Server not starting
- Ensure port 8000 is not in use
- Check that all required dependencies are installed
- Verify GROQ_API_KEY and TAVILY_API_KEY are set

### API tests fail
- Confirm server is running (check http://127.0.0.1:8000/docs)
- Verify sample files exist in `data/test_portfolios/`
- Check server logs for error messages

### Data validation errors
- Ensure CSV files have correct headers: Symbol, Quantity, PurchaseDate, PurchasePrice, CurrentPrice
- Dates should be in YYYY-MM-DD format
- Prices should be numeric values

## Next Steps

After successful testing:

1. **Custom Portfolio Testing**: Replace sample CSV with actual portfolio data
2. **Tavily Integration**: Test market research capabilities once fully integrated
3. **Performance Testing**: Load test with larger portfolios
4. **Frontend Development**: Build dashboard to visualize recommendations

## Generated Test Files Summary

| File | Purpose | Size |
|------|---------|------|
| sample_portfolio.csv | Multi-lot portfolio for FIFO testing | ~400 bytes |
| sample_portfolio_2lots.csv | Alternative portfolio for testing | ~250 bytes |
| income_tax_law_excerpt_india.txt | Tax rules for RAG system | ~1.5 KB |
| test_api_requests.py | Automated API test script | ~3 KB |
| project_testing.ipynb | Jupyter notebook for data generation | Notebook format |

---

**Last Updated**: November 7, 2025
**Test Data Version**: 1.0
**System Ready**: Production Testing Phase
