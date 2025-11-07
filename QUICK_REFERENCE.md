# Quick Reference - Testing Your AlphaAgent System

## 🚀 Start Testing in 2 Steps

### Terminal 1: Start the Server
```bash
python quickstart.py
```
✓ Server runs on http://127.0.0.1:8000

### Terminal 2: Run Tests
```bash
python run_quick_test.py
```
✓ Runs all API tests automatically

---

## 📊 What Gets Tested

**API Endpoints (6 total):**
- ✓ Health Check
- ✓ Portfolio Parsing
- ✓ Tax Loss Identification
- ✓ Compliance Checking
- ✓ Replacement Recommendations
- ✓ Tax Savings Calculation

**Test Data:**
- Portfolio 1: RELIANCE, TCS, INFY, HDFC (multi-lot)
- Portfolio 2: AXISBANK, SBIN, LT (loss opportunities)
- Tax Rules: Indian income tax excerpt
- Total: 7 distinct holdings, 2 portfolio scenarios

**Expected Results:**
- 200 OK responses
- Accurate tax loss detection
- Valid compliance checks
- Realistic recommendations
- Correct savings calculations

---

## 📁 Files Generated

| File | Purpose | Location |
|------|---------|----------|
| sample_portfolio.csv | Test portfolio 1 | data/test_portfolios/ |
| sample_portfolio_2lots.csv | Test portfolio 2 | data/test_portfolios/ |
| income_tax_law_excerpt_india.txt | Tax rules | data/test_portfolios/ |
| test_api_requests.py | API test script | data/test_portfolios/ |
| project_testing.ipynb | Jupyter notebook | notebooks/ |
| run_quick_test.py | Quick test runner | root directory |
| TESTING_GUIDE.md | Full testing documentation | root directory |
| TEST_SETUP_SUMMARY.md | Setup summary | root directory |

---

## 🧪 Understanding Your Test Data

### Portfolio 1: Multi-Lot Analysis

**Holdings:**
```
RELIANCE:  10 @ 2200 + 5 @ 2300 → Current 2100 (Loss opportunity)
TCS:        8 @ 3200 + 4 @ 3300 → Current 3500 (Gain)
INFY:      15 @ 900  + 5 @ 1150 → Current 1100 (Gain)
HDFC:      12 @ 2600            → Current 2500 (Loss opportunity)
```

**Tax Loss Potential:** -3200 INR

### Portfolio 2: Significant Losses

**Holdings:**
```
AXISBANK: 20 @ 750  → Current 680 (Significant loss)
SBIN:     30 @ 520  → Current 480 (Significant loss)
LT:        6 @ 2300 → Current 2250 (Minimal loss)
```

**Tax Loss Potential:** -2900 INR

---

## 🔍 Viewing Results

### API Documentation
```
http://127.0.0.1:8000/docs
```
Interactive Swagger UI to test endpoints manually

### ReDoc Documentation
```
http://127.0.0.1:8000/redoc
```
API reference documentation

### Test Script Output
Run `python data/test_portfolios/test_api_requests.py` to see:
- API responses
- HTTP status codes
- Data processing results

---

## ✅ Success Indicators

**Server Started Successfully:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**API Tests Passing:**
```
[TEST 1] Health Endpoint - Status: 200 OK
[TEST 2] Identify Tax Loss - Status: 200 OK
[TEST 3] Parse Portfolio - Status: 200 OK
[TEST 4] Check Compliance - Status: 200 OK
[TEST 5] Calculate Savings - Status: 200 OK
```

**Expected Findings:**
- Tax losses identified in RELIANCE, HDFC
- FIFO accounting applied correctly
- Compliance checks completed
- Savings calculated accurately

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in quickstart.py |
| Test script not found | Ensure you're in project root |
| API returns 404 | Verify server is running |
| No test data found | Run project_testing.ipynb notebook |
| Environment variable error | Set GROQ_API_KEY and TAVILY_API_KEY |

---

## 📚 Full Guides

- **TESTING_GUIDE.md** - Comprehensive testing documentation
- **TEST_SETUP_SUMMARY.md** - Complete setup overview
- **README.md** - Project overview
- **BACKEND_README.md** - Backend API documentation

---

## 🎯 Next Steps After Testing

1. ✓ Verify all tests pass
2. ✓ Review API response times
3. ✓ Test with custom portfolio data
4. ✓ Check Tavily API integration
5. ✓ Build frontend dashboard
6. ✓ Deploy to cloud

---

## 💡 Tips

**Manual Testing:**
```bash
# Test health
curl http://127.0.0.1:8000/health

# Access API docs
open http://127.0.0.1:8000/docs

# View Jupyter notebook
jupyter notebook notebooks/project_testing.ipynb
```

**Check Logs:**
Look at server terminal for detailed logging information

**Inspect Test Files:**
```bash
# View portfolio
cat data/test_portfolios/sample_portfolio.csv

# View test script
cat data/test_portfolios/test_api_requests.py
```

---

**System Status: ✅ READY FOR TESTING**

Created: November 7, 2025
