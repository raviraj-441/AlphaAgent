"""
News Fetcher using Tavily API

Fetches recent news articles about stocks and provides sentiment context
for the multi-agent debate system.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch and analyze news using Tavily API."""
    
    def __init__(self):
        """Initialize Tavily client."""
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self.client = None
        
        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily News Fetcher initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily client: {e}")
                self.client = None
        else:
            logger.warning("TAVILY_API_KEY not found in environment variables")
    
    def fetch_stock_news(
        self,
        symbol: str,
        company_name: Optional[str] = None,
        days: int = 7,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent news articles about a stock.
        
        Args:
            symbol: Stock ticker symbol (e.g., "RELIANCE")
            company_name: Optional full company name for better search
            days: Number of days to look back
            max_results: Maximum number of articles to return
            
        Returns:
            List of news articles with title, content, URL, and published date
        """
        if not self.client:
            logger.warning(f"Tavily client not available, skipping news for {symbol}")
            return []
        
        try:
            # Construct search query
            if company_name:
                query = f"{company_name} ({symbol}) stock news India"
            else:
                query = f"{symbol} stock news India market"
            
            logger.info(f"Fetching news for {symbol}: '{query}'")
            
            # Search news with Tavily
            response = self.client.search(
                query=query,
                search_depth="basic",  # Use "advanced" for more comprehensive results
                max_results=max_results,
                include_domains=[
                    "economictimes.indiatimes.com",
                    "moneycontrol.com",
                    "livemint.com",
                    "business-standard.com",
                    "reuters.com",
                    "bloomberg.com"
                ],
                days=days
            )
            
            # Extract and format results
            articles = []
            if response and 'results' in response:
                for result in response['results']:
                    article = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', ''),
                        'score': result.get('score', 0),
                        'published_date': result.get('published_date', '')
                    }
                    articles.append(article)
                
                logger.info(f"Found {len(articles)} news articles for {symbol}")
            else:
                logger.warning(f"No news results for {symbol}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def get_news_summary(self, articles: List[Dict[str, Any]]) -> str:
        """
        Create a concise summary of news articles for agent context.
        
        Args:
            articles: List of news articles
            
        Returns:
            Formatted summary string
        """
        if not articles:
            return "No recent news available."
        
        summary_lines = [f"Recent News ({len(articles)} articles):"]
        
        for i, article in enumerate(articles, 1):
            title = article['title'][:100]  # Truncate long titles
            summary_lines.append(f"  {i}. {title}")
        
        return "\n".join(summary_lines)
    
    def get_news_context_for_debate(
        self,
        symbols: List[str],
        company_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch news context for multiple stocks for debate.
        
        Args:
            symbols: List of stock symbols
            company_names: Optional dict mapping symbols to company names
            
        Returns:
            Dict mapping symbols to their news data
        """
        news_context = {}
        
        for symbol in symbols:
            company_name = company_names.get(symbol) if company_names else None
            articles = self.fetch_stock_news(symbol, company_name, days=7, max_results=3)
            
            news_context[symbol] = {
                'articles': articles,
                'summary': self.get_news_summary(articles),
                'article_count': len(articles)
            }
        
        return news_context
    
    def analyze_sentiment(self, articles: List[Dict[str, Any]]) -> str:
        """
        Analyze overall sentiment from news articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            Sentiment assessment (Positive/Negative/Neutral/Mixed)
        """
        if not articles:
            return "Neutral"
        
        # Simple keyword-based sentiment (could be enhanced with LLM)
        positive_keywords = ['surge', 'gain', 'profit', 'growth', 'bullish', 'rally', 'outperform', 'upgrade']
        negative_keywords = ['fall', 'loss', 'decline', 'bearish', 'downgrade', 'concern', 'risk', 'weak']
        
        positive_count = 0
        negative_count = 0
        
        for article in articles:
            text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
            
            for keyword in positive_keywords:
                if keyword in text:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in text:
                    negative_count += 1
        
        if positive_count > negative_count * 1.5:
            return "Positive"
        elif negative_count > positive_count * 1.5:
            return "Negative"
        elif abs(positive_count - negative_count) <= 1:
            return "Neutral"
        else:
            return "Mixed"
    
    def get_enriched_context(
        self,
        symbols: List[str],
        company_names: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Get enriched context string with news for all symbols.
        
        Args:
            symbols: List of stock symbols
            company_names: Optional dict mapping symbols to company names
            
        Returns:
            Formatted string with news context for agents
        """
        if not self.client:
            return "\nMarket News: Not available (Tavily API not configured)"
        
        news_context = self.get_news_context_for_debate(symbols, company_names)
        
        context_lines = ["\n=== RECENT MARKET NEWS ==="]
        
        for symbol in symbols:
            news_data = news_context.get(symbol, {})
            articles = news_data.get('articles', [])
            sentiment = self.analyze_sentiment(articles)
            
            context_lines.append(f"\n{symbol}:")
            context_lines.append(f"  Sentiment: {sentiment}")
            
            if articles:
                context_lines.append(f"  Top Headlines:")
                for i, article in enumerate(articles[:3], 1):
                    title = article['title'][:80]
                    context_lines.append(f"    {i}. {title}")
            else:
                context_lines.append(f"  No recent news found")
        
        context_lines.append("=" * 30)
        
        return "\n".join(context_lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = NewsFetcher()
    
    # Test fetch
    symbols = ["RELIANCE", "HDFC", "INFY"]
    enriched_context = fetcher.get_enriched_context(symbols)
    print(enriched_context)
