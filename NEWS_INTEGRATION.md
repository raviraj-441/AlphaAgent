# News Integration with Tavily API

## Overview

The AlphaAgent system now uses **Tavily API** to fetch real-time news articles about stocks during portfolio debates. This provides agents with current market sentiment and recent developments to inform their recommendations.

## How It Works

### 1. **News Fetching** (Before Debate Starts)
```python
# In multi_turn_debate_system.py
symbols = ["RELIANCE", "HDFC", "INFY"]
news_context = news_fetcher.get_enriched_context(symbols)
```

When a debate starts, the system:
- Extracts all unique stock symbols from the portfolio
- Fetches the 3 most recent news articles for each symbol
- Analyzes sentiment (Positive/Negative/Neutral/Mixed)
- Creates a formatted news summary

### 2. **News Sources**
Tavily searches these trusted financial sources:
- Economic Times (economictimes.indiatimes.com)
- MoneyControl (moneycontrol.com)
- LiveMint (livemint.com)
- Business Standard (business-standard.com)
- Reuters (reuters.com)
- Bloomberg (bloomberg.com)

### 3. **News Context Format**
Example news context added to agent prompts:
```
=== RECENT MARKET NEWS ===

RELIANCE:
  Sentiment: Positive
  Top Headlines:
    1. Reliance share price rises 2% after 4-day losing streak
    2. Reliance Industries shares rise after purchase of Middle...
    3. Reliance Infra, Reliance Power tank up to 54% from June...

HDFC:
  Sentiment: Mixed
  Top Headlines:
    1. HDFC Bank Q2 results: Net profit rises 5.3% to Rs...
    2. HDFC Bank shares fall despite strong quarterly results
    3. Analysts bullish on HDFC Bank after strong asset quality

==============================
```

### 4. **Agent Usage**
Each agent receives the news context and can use it:

- **TaxOptimizer**: Uses news to time harvesting around earnings/events
- **RiskManager**: Identifies negative news indicating higher risk
- **MarketStrategist**: **Primary user** - analyzes sentiment for timing
- **GrowthOptimizer**: Evaluates company fundamentals from news

## Configuration

### Setup Tavily API Key

1. Get your API key from https://tavily.com
2. Add to `.env` file:
```bash
TAVILY_API_KEY=tvly-your-key-here
```

3. The system will automatically detect and use it

### Fallback Behavior

If Tavily API is not configured:
- The system logs a warning
- Debates continue **without news context**
- No errors or crashes - graceful degradation

## Implementation Files

### `backend/utils/news_fetcher.py`
Main news fetching class with methods:
- `fetch_stock_news()` - Fetch articles for one symbol
- `get_news_context_for_debate()` - Fetch for multiple symbols
- `analyze_sentiment()` - Simple keyword-based sentiment
- `get_enriched_context()` - Format news for agent prompts

### `backend/core/multi_turn_debate_system.py`
Integration into debate system:
- Line 20: Import `NewsFetcher`
- Line 108: Initialize `self.news_fetcher = NewsFetcher()`
- Lines 353-362: Fetch news before debate starts

## Token Usage Impact

**Before News Integration:**
- Average prompt: ~290 tokens
- Total debate: ~2,000-3,000 tokens

**After News Integration:**
- Average prompt: ~450 tokens (+55%)
- Total debate: ~3,500-4,500 tokens

The increase is acceptable because:
- News provides valuable real-time context
- Agents make better-informed decisions
- Rate limit handling auto-retries on limits

## Testing

### Test News Fetcher Directly
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); \
from backend.utils.news_fetcher import NewsFetcher; \
nf = NewsFetcher(); \
print(nf.get_enriched_context(['RELIANCE', 'HDFC']))"
```

### Run Debate with News
```bash
python run_csv_debate.py portfolio.csv --rounds 2
```

Check the logs for:
```
INFO - Fetching news for 3 symbols: HDFC, RELIANCE, INFY
INFO - Found 3 news articles for RELIANCE
```

## Benefits

✅ **Real-time Context**: Agents see current market developments  
✅ **Better Timing**: MarketStrategist can time harvesting around events  
✅ **Sentiment Analysis**: Simple keyword-based sentiment for each stock  
✅ **Trusted Sources**: Only reputable financial news sites  
✅ **Graceful Fallback**: Works without API key (just no news)  
✅ **Rate Limit Safe**: Fetches news once before debate, not per agent call

## Example Impact on Decisions

**Without News:**
- MarketStrategist: "Based on technical indicators..."
- Confidence: 70%

**With News:**
- MarketStrategist: "Recent positive news about Q2 earnings beat shows strong fundamentals. However, analyst downgrades suggest short-term caution..."
- Confidence: 85% (higher due to additional context)

## Future Enhancements

Potential improvements:
- [ ] LLM-based sentiment analysis (vs keyword matching)
- [ ] News importance scoring
- [ ] Company-specific news filtering
- [ ] Historical news comparison
- [ ] Sector-wide news aggregation
