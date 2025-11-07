# AlphaAgent - Testing Documentation Index

## 🎯 Start Here

**New to testing?** Read these in order:

1. **QUICK_REFERENCE.md** ← **START HERE** (2 min read)
   - Quick start in 2 commands
   - What gets tested
   - Success indicators

2. **TESTING_GUIDE.md** (10 min read)
   - Detailed testing procedures
   - Expected results explanation
   - Tax loss analysis
   - Troubleshooting guide

3. **TEST_SETUP_SUMMARY.md** (15 min read)
   - Complete overview of generated files
   - Testing checklist
   - API endpoint reference
   - Key features being tested

---

## 📂 What Was Generated

### Test Data (in `data/test_portfolios/`)

```
data/test_portfolios/
├── sample_portfolio.csv                    # Multi-lot portfolio
├── sample_portfolio_2lots.csv              # Loss-focused portfolio
├── income_tax_law_excerpt_india.txt        # Tax rules
└── test_api_requests.py                    # API test script
```

### Documentation (in project root)

```
├── QUICK_REFERENCE.md                      # Quick start guide
├── TESTING_GUIDE.md                        # Comprehensive guide
├── TEST_SETUP_SUMMARY.md                   # Setup overview
├── TEST_SETUP_INDEX.md                     # This file
└── notebooks/
    └── project_testing.ipynb               # Interactive notebook
```

### Tools (in project root)

```
├── run_quick_test.py                       # One-command test runner
└── quickstart.py                           # Start the server
```

---

## 🚀 Testing Flow

### Option 1: Quick Start (Fastest)

```bash
# Terminal 1
python quickstart.py

# Terminal 2
python run_quick_test.py
```

### Option 2: Comprehensive Testing (Detailed)

```bash
# Terminal 1
python quickstart.py

# Terminal 2
python data/test_portfolios/test_api_requests.py
```

### Option 3: Interactive Testing (Exploratory)

```bash
# Run Jupyter notebook
jupyter notebook notebooks/project_testing.ipynb

# Then use interactive cells to explore
```

---

## 📊 Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| API Health | 1 | ✓ |
| Portfolio Parsing | 1 | ✓ |
| Tax Loss ID | 1 | ✓ |
| Compliance | 1 | ✓ |
| Recommendations | 1 | ✓ |
| Savings Calc | 1 | ✓ |
| **Total** | **6** | **Ready** |

---

## 📈 Test Data Profile

### Portfolio 1: `sample_portfolio.csv`
- **Symbols**: RELIANCE, TCS, INFY, HDFC
- **Total Holdings**: 7 (5 lots)
- **Loss Opportunities**: RELIANCE (-2000), HDFC (-1200)
- **Use Case**: FIFO accounting, multi-lot handling

### Portfolio 2: `sample_portfolio_2lots.csv`
- **Symbols**: AXISBANK, SBIN, LT
- **Total Holdings**: 3
- **Loss Opportunities**: AXISBANK (-1400), SBIN (-1200), LT (-300)
- **Use Case**: Significant loss identification, recommendations

### Tax Document: `income_tax_law_excerpt_india.txt`
- **Coverage**: STCG, LTCG, FIFO, capital loss offset
- **Use Case**: RAG system validation, compliance checking

---

## ✅ Testing Checklist

### Before Testing
- [ ] Read QUICK_REFERENCE.md
- [ ] Ensure port 8000 is available
- [ ] Verify GROQ_API_KEY is set
- [ ] Check all test files exist in `data/test_portfolios/`

### During Testing
- [ ] Server starts without errors
- [ ] First test passes (health check)
- [ ] All 6 API endpoints respond
- [ ] Portfolio data parses correctly
- [ ] Tax losses are identified accurately

### After Testing
- [ ] Review results in terminal
- [ ] Check server logs for errors
- [ ] Verify calculations are correct
- [ ] Document any issues found

---

## 🔧 Troubleshooting Quick Links

**Issue**: Server won't start
→ See TESTING_GUIDE.md "Troubleshooting" section

**Issue**: API tests fail
→ See TESTING_GUIDE.md "Troubleshooting" section

**Issue**: Test data not found
→ Run `jupyter notebook notebooks/project_testing.ipynb`

**Issue**: Port 8000 in use
→ Edit `quickstart.py` to use different port

---

## 📚 Full Documentation Guide

### For Quick Start
**Read**: `QUICK_REFERENCE.md` (2 min)
- Perfect for: Getting started quickly
- Contains: Commands, success indicators, tips

### For Step-by-Step Testing
**Read**: `TESTING_GUIDE.md` (10 min)
- Perfect for: Following detailed procedures
- Contains: Setup, running tests, expected results, troubleshooting

### For Complete Understanding
**Read**: `TEST_SETUP_SUMMARY.md` (15 min)
- Perfect for: Understanding the whole system
- Contains: Files generated, data analysis, test checkl ist

### For API Reference
**Use**: http://127.0.0.1:8000/docs
- Perfect for: Testing individual endpoints
- Contains: Interactive Swagger UI with all endpoint details

### For Code Exploration
**Use**: `notebooks/project_testing.ipynb`
- Perfect for: Understanding data generation
- Contains: Interactive Python cells showing data creation

---

## 🎓 Learning Resources

### Understanding the Test Data

1. **CSV Format**: View raw files
   ```bash
   cat data/test_portfolios/sample_portfolio.csv
   ```

2. **Tax Rules**: View tax law excerpt
   ```bash
   cat data/test_portfolios/income_tax_law_excerpt_india.txt
   ```

3. **API Script**: View test requests
   ```bash
   cat data/test_portfolios/test_api_requests.py
   ```

### Understanding the System

1. **API Documentation**: http://127.0.0.1:8000/docs
2. **Backend README**: `BACKEND_README.md`
3. **Project README**: `README.md`
4. **Examples**: `examples.py`

---

## 🎯 Success Criteria

**All tests pass when:**
- ✓ Server starts on http://127.0.0.1:8000
- ✓ Health endpoint returns 200 OK
- ✓ All 6 API endpoints respond
- ✓ Tax losses identified correctly
- ✓ Compliance checks complete
- ✓ Savings calculations accurate

---

## 🚀 Next Steps After Testing

1. **Verify Results**: Check terminal output matches expectations
2. **Test Custom Data**: Replace CSV with your own portfolio
3. **Manual Testing**: Use Swagger UI at http://127.0.0.1:8000/docs
4. **Integration**: Test Tavily API for replacement recommendations
5. **Performance**: Load test with larger portfolios

---

## 📞 Quick Reference Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| QUICK_REFERENCE.md | Fast setup | 2 min |
| TESTING_GUIDE.md | Detailed steps | 10 min |
| TEST_SETUP_SUMMARY.md | Complete overview | 15 min |
| This File | Navigation index | 3 min |

---

## 🔍 File Structure

```
AlphaAgent/
├── README.md                          # Project overview
├── QUICK_REFERENCE.md                 # Quick start (READ THIS FIRST)
├── TESTING_GUIDE.md                   # Comprehensive guide
├── TEST_SETUP_SUMMARY.md              # Setup details
├── TEST_SETUP_INDEX.md                # This navigation file
├── BACKEND_README.md                  # API documentation
├── run_quick_test.py                  # Test runner
├── quickstart.py                      # Start server
│
├── data/test_portfolios/              # Test data
│   ├── sample_portfolio.csv
│   ├── sample_portfolio_2lots.csv
│   ├── income_tax_law_excerpt_india.txt
│   └── test_api_requests.py
│
├── notebooks/
│   ├── project_testing.ipynb          # Interactive notebook
│   └── ...other notebooks
│
├── backend/
│   ├── routes/                        # API endpoints
│   ├── agents/                        # 7 intelligent agents
│   ├── utils/                         # Utilities
│   └── config.py
│
└── config/
    ├── agents.yaml
    └── tasks.yaml
```

---

## 💡 Pro Tips

1. **Monitor logs** while tests run to understand system behavior
2. **Use Swagger UI** for interactive testing of individual endpoints
3. **Check exit codes** - 0 means success, non-zero means failure
4. **Save test outputs** for comparison with future runs
5. **Test incrementally** - run one endpoint test, then another

---

## ⏱️ Typical Test Timing

| Step | Time |
|------|------|
| Server startup | 5-10 sec |
| Health check | <100ms |
| Portfolio parsing | 100-500ms |
| Tax loss ID | 500-2000ms |
| Compliance check | 1-3 sec |
| Recommendations | 2-5 sec (with Tavily) |
| Savings calc | <500ms |
| **Total** | **5-15 min** |

---

## 📊 Generated Data Statistics

| Metric | Value |
|--------|-------|
| Test Portfolios | 2 |
| Total Holdings | 10 |
| Unique Symbols | 7 |
| Multiple Lot Groups | 6 |
| Total Unrealized Loss | -6,100 INR |
| Total Unrealized Gain | +6,200 INR |
| API Endpoints Tested | 6 |
| Test Scripts | 2 (Python + Notebook) |

---

## 🎉 You're Ready!

Everything is set up and ready to test your AlphaAgent backend system.

**Start with**: `QUICK_REFERENCE.md` → Run tests → Review `TESTING_GUIDE.md`

---

**Created**: November 7, 2025  
**Status**: ✅ Production Ready for Testing  
**Last Updated**: November 7, 2025
