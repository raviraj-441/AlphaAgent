# AlphaAgent - Multi-Agent Tax Loss Harvesting System# AlphaAgent

An implementation of the AlphaAgent paper published by BlackRock. 

AI-powered portfolio optimization using multi-agent debate for tax loss harvesting decisions.Instead of AutoGen for orchestrating debates which is used in the original paper, we used crewAI as it is easier to onboard new Agents.

https://arxiv.org/abs/2508.11152

## Features



- 🤖 **Multi-Turn Agent Debate**: Agents discuss strategies across multiple rounds

- 👔 **Supervisor Orchestration**: AI moderator evaluates consensus## 🎯 Features

- 💡 **4 Specialized Agents**: Tax, Risk, Market Timing, Growth perspectives

- 📊 **Confidence Voting**: Weighted decisions based on agent certainty- **Multi-Agent Analysis**: Three specialized agents analyze different aspects of investment

- 📝 **Full Audit Trail**: Complete JSON logs of all debates- **RAG Integration**: Semantic search through financial documents using ChromaDB

- **Real-time Data**: Yahoo Finance integration for live market data

## Quick Start- **News Sentiment**: Advanced news analysis using Tavily API

- **Structured Debate**: Moderated discussion between agents for consensus building

```bash- **Comprehensive Reports**: Detailed analysis with clear BUY/SELL/HOLD recommendations

# Install

pip install -r requirements.txt## 🏗️ Architecture



# Configure### Agents

echo 'GROQ_API_KEY=your_key' > .env1. **Fundamental Analyst** - Analyzes financial reports and balance sheets

echo 'TAVILY_API_KEY=your_key' >> .env2. **Valuation Analyst** - Calculates returns, volatility, and risk metrics

3. **Sentiment Analyst** - Processes news and market sentiment

# Run4. **Moderator** - Facilitates structured debate between analysts

python run_debate.py5. **Conclusion Agent** - Provides final investment decision

```

### Tools

## How It Works- **CustomRagTool** - RAG-based financial document analysis that uses SemanticChunking

- **fundamentalAnalysisTool** - Balance sheet analysis

### The Agents- **getAnnualisedVolatilityTool** - Volatility calculation

- **getAnnualisedReturnTool** - Return analysis

| Agent | Focus | Recommendation |- **getNewsBodyTool** - News content extraction

|-------|-------|----------------|

| TaxOptimizer | Tax savings | Harvest losses |## 📋 Prerequisites

| RiskManager | Risk reduction | Reduce concentration |

| MarketStrategist | Technical timing | Follow momentum |- Python 3.8+

| GrowthOptimizer | Long-term growth | Keep quality stocks |- UV package manager

- OpenAI API key

### Debate Flow- Tavily API key



```## 🚀 Installation

Round 1: Initial positions

  → TaxOptimizer: HARVEST (85%)1. **Install dependencies using UV**

  → RiskManager: HARVEST (78%)   ```bash

  → MarketStrategist: KEEP (70%)   uv sync

  → GrowthOptimizer: KEEP (82%)   ```

  Supervisor: "2v2 split, continue"

2. **Set up environment variables**

Round 2: Refined (agents respond to each other)   ```bash

  → TaxOptimizer: HARVEST (85%)   # Create .env file

  → RiskManager: KEEP (62%) ← Changed!   echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env

  → MarketStrategist: KEEP (72%)   echo "TAVILY_API_KEY=your_tavily_api_key_here" >> .env

  → GrowthOptimizer: KEEP (85%)   ```

  Supervisor: "Converging on KEEP"



Round 3: Consensus## ⚙️ Configuration

  → All agents: KEEP (70-87% confidence)

  Supervisor: "Consensus reached!"### Agent Configuration (config/agents.yaml)

  The agents are configured with specific roles, goals, and backstories as defined in the provided YAML structure.

Final: KEEP all positions

```### Task Configuration (config/tasks.yaml)

Tasks define the workflow and expected outputs for each analysis phase.

## API Usage

## 🎮 Usage

```python

from backend.core.multi_turn_debate_system import MultiTurnDebateSystem, StockPosition### Running with UV

```bash

# Create portfolio# Activate the virtual environment

positions = [uv run python main.py --stock <ticker> --doc </path/to/your/pdfdocs>

    StockPosition(```

        symbol="RELIANCE", quantity=100, cost_basis=2600,Alternatively, you can directly put multiple docs in the "assets/rag_assets" folder

        current_price=2450, holding_days=210,

        loss_amount=15000, tax_saving=4500## 📊 Analysis Workflow

    ),

]1. **Fundamental Analysis**

   - Extracts financial data from uploaded documents

# Run debate   - Analyzes balance sheet using Yahoo Finance

debate = MultiTurnDebateSystem(max_rounds=5)   - Provides comprehensive financial metrics

session = debate.debate_portfolio_strategy(positions)

2. **Valuation Analysis**

# Results   - Calculates 3-month annualized returns

print(f"Strategy: {session.final_strategy}")   - Computes volatility metrics

print(f"Conclusion: {session.supervisor_conclusion}")   - Performs risk-return analysis

```

3. **Sentiment Analysis**

## Project Structure   - Fetches recent news articles

   - Analyzes market sentiment

```   - Identifies key opportunities and risks

AlphaAgent/

├── backend/4. **Moderated Debate**

│   ├── core/   - Structured discussion between analysts

│   │   └── multi_turn_debate_system.py  # Main system   - Challenges and defenses of positions

│   ├── agents/                          # Agent implementations   - Consensus building process

│   └── utils/                           # Utilities

├── run_debate.py                        # Main entry point5. **Final Conclusion**

├── test_multi_turn_debate.py            # Tests   - Synthesizes all analyses

└── requirements.txt   - Provides clear investment recommendation

```   - Justifies decision with evidence



## Configuration## 📝 Output Format



```pythonEach analysis phase produces structured reports including:

# Quick (3 rounds)- Key metrics and findings

MultiTurnDebateSystem(max_rounds=3)- Risk assessments

- Clear BUY/SELL/HOLD recommendations

# Standard (5 rounds, recommended)- Supporting evidence and reasoning

MultiTurnDebateSystem(max_rounds=5)



# Extended (7 rounds)## 🛠️ Adding New Agents and Tools

MultiTurnDebateSystem(max_rounds=7)

```### Adding a New Agent



## Output1. **Define the Agent in YAML Configuration**

   

Debates saved to: `logs/multi_turn_debates/multi_turn_debate_*.json`   Add to `config/agents.yaml`:

   ```yaml

```json   technical_analyst:

{     role: >

  "session_id": "20251108_143052",       Technical Analysis Specialist

  "total_rounds": 3,     goal: >

  "final_status": "consensus_reached",       Analyze price patterns, technical indicators, and chart formations

  "final_strategy": {       to provide trading insights and price predictions.

    "RELIANCE": "KEEP",     backstory: >

    "HDFC": "KEEP"       You are an expert technical analyst with deep knowledge of chart

  }       patterns, technical indicators, and market psychology. You use

}       historical price data to identify trends and potential entry/exit points.

```   ```



## Testing2. **Create the Agent Method**

   

```bash   Add to your `InvestmentCrew` class:

# Run test   ```python

python test_multi_turn_debate.py   @agent

   def technical_analyst(self) -> Agent:

# View logs       return Agent(

cat logs/multi_turn_debates/*.json | python -m json.tool           config=self.agents_config["technical_analyst"],

```           tools=[your_technical_tools],  # Add relevant tools

           llm=self.llm,

## Performance       )

   ```

- **Consensus Time**: 2-3 rounds typical

- **Duration**: 1-3 minutes per portfolio3. **Update the Crew Configuration**

- **API Calls**: 4-20 (4 agents × 1-5 rounds)   

   Add the new agent to your crew:

## Documentation   ```python

   @crew

- **MULTI_TURN_DEBATE.md** - Complete API reference   def crew(self) -> Crew:

- **DEPLOYMENT.md** - Production setup       return Crew(

- **MONITORING.md** - Metrics guide           agents=[

               self.fundamental_analyst(),

## Requirements               self.valuation_analyst(),

               self.sentiment_analyst(),

- Python 3.11+               self.technical_analyst(),  # New agent

- Groq API key (LLM)               self.moderator(),

- Tavily API key (news, optional)               self.conclusion_agent()

           ],

## License           tasks=self.tasks,

           process=Process.sequential,

MIT License           verbose=True,

       )

## Support   ```



GitHub Issues: https://github.com/raviraj-441/AlphaAgent/issues### Adding a New Tool



---#### Method 1: Function-based Tool (Recommended for simple tools)



**Status**: Production Ready ✅```python

@tool
def get_technical_indicators(*args, **kwargs) -> dict:
    """
    Calculate technical indicators for a stock
    Args:
        period (str): Time period for analysis (e.g., '1mo', '3mo', '1y')
    Returns:
        dict: Technical indicators including RSI, MACD, Bollinger Bands
    """
    import talib
    
    # Get stock data
    ticker = yf.Ticker(f"{InvestmentCrew.stock}.NS")
    df = ticker.history(period=kwargs.get('period', '3mo'))
    
    # Calculate indicators
    indicators = {
        'rsi': talib.RSI(df['Close'].values),
        'macd': talib.MACD(df['Close'].values),
        'bb_upper': talib.BBANDS(df['Close'].values)[0],
        'bb_lower': talib.BBANDS(df['Close'].values)[2],
    }
    
    return indicators
```

#### Method 2: Class-based Tool (For complex tools with state)

```python
class TechnicalAnalysisInput(BaseModel):
    """Input schema for Technical Analysis Tool."""
    indicator: str = Field(..., description="Technical indicator to calculate (rsi, macd, bollinger)")
    period: str = Field(default="3mo", description="Time period for analysis")

class TechnicalAnalysisTool(BaseTool):
    name: str = "TechnicalAnalysisTool"
    description: str = "Calculate and analyze technical indicators for stock analysis"
    args_schema: Type[BaseModel] = TechnicalAnalysisInput
    
    def _run(self, indicator: str, period: str = "3mo") -> str:
        """Execute technical analysis"""
        try:
            ticker = yf.Ticker(f"{InvestmentCrew.stock}.NS")
            df = ticker.history(period=period)
            
            if indicator.lower() == "rsi":
                import talib
                rsi = talib.RSI(df['Close'].values)
                current_rsi = rsi[-1]
                return f"Current RSI: {current_rsi:.2f} - {'Overbought' if current_rsi > 70 else 'Oversold' if current_rsi < 30 else 'Neutral'}"
            
            # Add more indicators as needed
            return f"Indicator {indicator} calculated successfully"
            
        except Exception as e:
            return f"Error calculating {indicator}: {str(e)}"
```

### Adding a New Task

1. **Define Task in YAML Configuration**
   
   Add to `config/tasks.yaml`:
   ```yaml
   technical_analysis_task:
     description: >
       Perform comprehensive technical analysis on the stock using various
       indicators including RSI, MACD, Bollinger Bands, and moving averages.
       Identify key support and resistance levels, trend direction, and
       potential entry/exit points.
     expected_output: >
       A technical analysis report including:
         1) Current trend direction and strength,
         2) Key technical indicators (RSI, MACD, Bollinger Bands),
         3) Support and resistance levels,
         4) Technical BUY/SELL/HOLD recommendation with price targets.
     agent: technical_analyst
   ```

2. **Create Task Method**
   
   Add to your `InvestmentCrew` class:
   ```python
   @task
   def technical_analysis_task(self) -> Task:
       return Task(config=self.tasks_config["technical_analysis_task"])
   ```

3. **Update Dependent Tasks**
   
   Add context to tasks that should use this analysis:
   ```yaml
   investment_debate_task:
     # ... existing configuration ...
     context: [valuation_task, sentiment_task, fundamental_task, technical_analysis_task]
   ```

### Tool Integration Examples

#### External API Tool
```python
@tool
def get_insider_trading_data(*args, **kwargs) -> str:
    """Fetch insider trading information for the stock"""
    import requests
    
    # Example API call (replace with actual API)
    response = requests.get(f"https://api.example.com/insider/{InvestmentCrew.stock}")
    return response.json()
```

#### Database Tool
```python
class DatabaseQueryTool(BaseTool):
    name: str = "DatabaseQueryTool"
    description: str = "Query internal database for historical analysis data"
    
    def _run(self, query: str) -> str:
        """Execute database query"""
        # Connect to your database
        # Execute query
        # Return results
        pass
```

#### File Processing Tool
```python
@tool
def process_earnings_transcript(*args, **kwargs) -> str:
    """Process and analyze earnings call transcripts"""
    # Read transcript files
    # Perform NLP analysis
    # Extract key insights
    pass
```


## 🔧 Dependencies

Key packages managed by UV:
- `crewai` - Multi-agent framework
- `langchain` - LLM orchestration
- `yfinance` - Yahoo Finance data
- `tavily-python` - News API
- `chromadb` - Vector database
- `pandas` - Data manipulation
- `numpy` - Numerical computations
