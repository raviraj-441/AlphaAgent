# CSV Portfolio Debate - Usage Guide

## Overview
Run AI-powered multi-agent debates on any portfolio CSV file to get tax-loss harvesting recommendations.

## Quick Start

### Basic Usage
```bash
python run_csv_debate.py <path_to_csv>
```

### Example
```bash
python run_csv_debate.py data/test_portfolios/my_portfolio.csv
```

## CSV Format Required

Your CSV file must have these **exact column names**:

```csv
Symbol,Quantity,PurchaseDate,PurchasePrice,CurrentPrice
RELIANCE,15,2024-04-10,2600,2450
HDFC,20,2023-12-15,1750,1600
INFY,10,2022-05-20,1700,1600
```

### Column Descriptions:
- **Symbol**: Stock ticker/name (e.g., RELIANCE, HDFC)
- **Quantity**: Number of shares owned
- **PurchaseDate**: Date purchased in `YYYY-MM-DD` format
- **PurchasePrice**: Price per share when purchased (in ₹)
- **CurrentPrice**: Current market price per share (in ₹)

## Command-Line Options

### Control Debate Rounds
```bash
python run_csv_debate.py portfolio.csv --rounds 5
```
Default: 3 rounds

### Adjust API Delay (for rate limits)
```bash
python run_csv_debate.py portfolio.csv --delay 1.5
```
Default: 1.0 second between API calls

### Combine Options
```bash
python run_csv_debate.py data/portfolio.csv --rounds 4 --delay 2.0
```

## Output

All debate results are automatically saved to the **logs directory** in JSON format:

```
logs/multi_turn_debates/multi_turn_debate_<session_id>.json
```

This follows the same logging structure as `run_debate.py` - ensuring consistent, structured logs for all debate sessions.

### Console Output
You'll see:
- Portfolio summary (total loss, tax saving potential)
- Live progress through debate rounds
- Final strategy for each stock
- Supervisor conclusion
- Path to saved log file

### Log File Contents
The JSON log contains:
- Session metadata (ID, timestamps, rounds)
- All stock positions analyzed
- Complete debate rounds with:
  - Each agent's statement, position, confidence
  - Key points and reasoning
  - Supervisor feedback
  - Consensus status
- Final strategy recommendations

## What Gets Analyzed?

- ✅ Only stocks with **unrealized losses** are included in the debate
- ✅ Tax rates automatically calculated based on holding period:
  - **LTCG (≥ 1 year)**: 12.5%
  - **STCG (< 1 year)**: 20%
- ✅ Four AI agents debate each position:
  - **TaxOptimizer**: Focuses on tax savings
  - **RiskManager**: Analyzes risk exposure
  - **MarketStrategist**: Considers market timing
  - **GrowthOptimizer**: Evaluates growth potential

## Sample Workflow

1. **Prepare your CSV**:
   ```bash
   # Make sure it has the required columns
   Symbol,Quantity,PurchaseDate,PurchasePrice,CurrentPrice
   ```

2. **Run debate**:
   ```bash
   python run_csv_debate.py my_portfolio.csv
   ```

3. **Review results**:
   - Check console for summary
   - Open `logs/multi_turn_debates/multi_turn_debate_<session_id>.json` for complete data
   - All debates follow the same JSON structure for easy analysis

4. **Adjust if needed**:
   ```bash
   # Want more debate rounds?
   python run_csv_debate.py my_portfolio.csv --rounds 5
   
   # Getting rate limited?
   python run_csv_debate.py my_portfolio.csv --delay 2.0
   ```

## Tips

- **Rate Limits**: The tool automatically retries on rate limits with smart waiting
- **No Losses?**: If your CSV has no stocks with losses, you'll get a message and the debate won't run
- **Bad Data?**: Rows with errors are skipped with warnings in the log
- **Multiple CSVs**: Just run the command again with different CSV file - no code changes needed!

## Error Messages

### "CSV file not found"
- Check your file path
- Use absolute or relative path from where you run the command

### "CSV missing required columns"
- Verify your CSV has: Symbol, Quantity, PurchaseDate, PurchasePrice, CurrentPrice
- Column names are case-sensitive

### "No positions with losses found"
- Your portfolio has no unrealized losses
- Only stocks trading below purchase price are analyzed

## Advanced Usage

### Get Help
```bash
python run_csv_debate.py --help
```

### Process Multiple Files
```bash
# Windows
for %f in (*.csv) do python run_csv_debate.py %f

# Linux/Mac
for file in *.csv; do python run_csv_debate.py "$file"; done
```

## Examples

### Conservative Analysis (fewer rounds)
```bash
python run_csv_debate.py portfolio.csv --rounds 2
```

### Thorough Analysis (more rounds)
```bash
python run_csv_debate.py portfolio.csv --rounds 5 --delay 1.5
```

### Save to Specific Location
```bash
python run_csv_debate.py portfolio.csv --output reports/analysis_today.txt
```
