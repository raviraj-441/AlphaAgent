"""
Market Analyzer - Combines news sentiment with market data for comprehensive analysis

Provides agents with:
- News sentiment scores
- Price volatility metrics
- Support/resistance levels
- Risk-return analysis
- Harvest timing recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from backend.utils.news_fetcher import NewsFetcher
from backend.utils.market_data_fetcher import MarketDataFetcher

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Combines sentiment and market data for comprehensive stock analysis."""
    
    def __init__(self):
        """Initialize news and market data fetchers."""
        self.news_fetcher = NewsFetcher()
        self.market_fetcher = MarketDataFetcher()
        logger.info("Market Analyzer initialized (News + Market Data)")
    
    def analyze_stock(
        self,
        symbol: str,
        current_price: float,
        cost_basis: float,
        holding_days: int,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis combining news sentiment and market data.
        
        Args:
            symbol: Stock ticker
            current_price: Current market price
            cost_basis: Purchase price
            holding_days: Days held
            company_name: Optional full company name
            
        Returns:
            Dict with sentiment, volatility, risk metrics, and recommendations
        """
        logger.info(f"Analyzing {symbol}: Current=₹{current_price}, Basis=₹{cost_basis}, Days={holding_days}")
        
        analysis = {
            "symbol": symbol,
            "current_price": current_price,
            "cost_basis": cost_basis,
            "holding_days": holding_days,
            "loss_pct": ((current_price - cost_basis) / cost_basis) * 100
        }
        
        # 1. NEWS SENTIMENT ANALYSIS
        logger.info(f"  Fetching news sentiment for {symbol}...")
        articles = self.news_fetcher.fetch_stock_news(symbol, company_name, days=7, max_results=5)
        sentiment = self.news_fetcher.analyze_sentiment(articles)
        
        analysis['sentiment'] = {
            'sentiment_score': sentiment,
            'article_count': len(articles),
            'headlines': [a['title'][:80] for a in articles[:3]]
        }
        
        # 2. MARKET DATA & VOLATILITY
        logger.info(f"  Fetching market statistics for {symbol}...")
        stats = self.market_fetcher.get_stats(symbol, period="6mo")
        
        if stats:
            analysis['market_stats'] = {
                'volatility': stats['volatility'],
                'avg_return_daily': stats['avg_return_daily'],
                'sharpe_ratio': stats['sharpe_ratio'],
                'total_return_6m': stats['total_return'],
                'price_range': {
                    'min': stats['min_price'],
                    'max': stats['max_price'],
                    'current': stats['current_price']
                }
            }
            
            # Calculate support/resistance
            analysis['technical'] = {
                'support_level': stats['min_price'],
                'resistance_level': stats['max_price'],
                'distance_from_support': ((current_price - stats['min_price']) / stats['min_price']) * 100,
                'distance_from_resistance': ((stats['max_price'] - current_price) / current_price) * 100
            }
        else:
            logger.warning(f"  Could not fetch market stats for {symbol}")
            analysis['market_stats'] = None
            analysis['technical'] = None
        
        # 3. RISK ASSESSMENT
        analysis['risk_assessment'] = self._assess_risk(analysis)
        
        # 4. HARVEST TIMING RECOMMENDATION
        analysis['harvest_timing'] = self._recommend_timing(analysis)
        
        logger.info(f"  ✓ Analysis complete for {symbol}")
        return analysis
    
    def _assess_risk(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level based on volatility and sentiment."""
        risk_level = "Medium"
        risk_score = 50
        risk_factors = []
        
        # Sentiment risk
        if analysis['sentiment']['sentiment_score'] == "Negative":
            risk_score += 20
            risk_factors.append("Negative news sentiment")
        elif analysis['sentiment']['sentiment_score'] == "Positive":
            risk_score -= 10
            risk_factors.append("Positive news sentiment (lower risk)")
        
        # Volatility risk
        if analysis.get('market_stats') and analysis['market_stats']:
            vol = analysis['market_stats']['volatility']
            if vol > 0.03:  # >3% daily volatility
                risk_score += 25
                risk_factors.append(f"High volatility ({vol:.2%} daily)")
            elif vol < 0.015:  # <1.5% daily volatility
                risk_score -= 15
                risk_factors.append(f"Low volatility ({vol:.2%} daily)")
        
        # Loss magnitude risk
        loss_pct = abs(analysis['loss_pct'])
        if loss_pct > 15:
            risk_score += 15
            risk_factors.append(f"Large loss ({loss_pct:.1f}%)")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score <= 35:
            risk_level = "Low"
        
        return {
            'risk_level': risk_level,
            'risk_score': min(100, max(0, risk_score)),
            'risk_factors': risk_factors
        }
    
    def _recommend_timing(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend harvest timing based on technical and sentiment factors."""
        timing_score = 50  # Neutral = 50
        timing_factors = []
        recommendation = "WAIT"
        
        # Sentiment timing
        sentiment = analysis['sentiment']['sentiment_score']
        if sentiment == "Negative":
            timing_score += 25
            timing_factors.append("Negative sentiment suggests harvest now")
        elif sentiment == "Positive":
            timing_score -= 20
            timing_factors.append("Positive sentiment suggests wait for recovery")
        
        # Technical timing
        if analysis.get('technical'):
            tech = analysis['technical']
            
            # Near support = good time to harvest
            if tech['distance_from_support'] < 5:
                timing_score += 20
                timing_factors.append("Near support level - good harvest point")
            
            # Far from resistance = unlikely quick recovery
            if tech['distance_from_resistance'] > 20:
                timing_score += 15
                timing_factors.append("Far from resistance - recovery may take time")
        
        # Market stats timing
        if analysis.get('market_stats') and analysis['market_stats']:
            stats = analysis['market_stats']
            
            # Negative 6-month trend
            if stats['total_return_6m'] < -0.05:
                timing_score += 15
                timing_factors.append("Downtrend over 6 months")
            
            # High volatility = uncertain, maybe harvest
            if stats['volatility'] > 0.025:
                timing_score += 10
                timing_factors.append("High volatility increases uncertainty")
        
        # Determine recommendation
        if timing_score >= 70:
            recommendation = "HARVEST_NOW"
        elif timing_score >= 55:
            recommendation = "HARVEST_SOON"
        elif timing_score <= 40:
            recommendation = "HOLD_FOR_RECOVERY"
        else:
            recommendation = "WAIT"
        
        return {
            'recommendation': recommendation,
            'timing_score': min(100, max(0, timing_score)),
            'timing_factors': timing_factors,
            'confidence': "HIGH" if abs(timing_score - 50) > 25 else "MEDIUM"
        }
    
    def get_portfolio_analysis(
        self,
        positions: List[Dict[str, Any]],
        company_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze entire portfolio with combined metrics.
        
        Args:
            positions: List of stock positions with symbol, current_price, cost_basis, holding_days
            company_names: Optional mapping of symbols to company names
            
        Returns:
            Portfolio-level analysis with per-stock details
        """
        logger.info(f"Analyzing portfolio of {len(positions)} positions...")
        
        portfolio_analysis = {
            'total_positions': len(positions),
            'analysis_timestamp': datetime.now().isoformat(),
            'stocks': {}
        }
        
        # Analyze each stock
        for pos in positions:
            symbol = pos['symbol']
            company_name = company_names.get(symbol) if company_names else None
            
            stock_analysis = self.analyze_stock(
                symbol=symbol,
                current_price=pos['current_price'],
                cost_basis=pos['cost_basis'],
                holding_days=pos['holding_days'],
                company_name=company_name
            )
            
            portfolio_analysis['stocks'][symbol] = stock_analysis
        
        # Portfolio-level summary
        portfolio_analysis['summary'] = self._create_portfolio_summary(portfolio_analysis['stocks'])
        
        logger.info(f"✓ Portfolio analysis complete")
        return portfolio_analysis
    
    def _create_portfolio_summary(self, stocks: Dict[str, Any]) -> Dict[str, Any]:
        """Create portfolio-level summary from individual stock analyses."""
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0, "Mixed": 0}
        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        harvest_recommendations = []
        
        for symbol, analysis in stocks.items():
            sentiment_counts[analysis['sentiment']['sentiment_score']] += 1
            risk_counts[analysis['risk_assessment']['risk_level']] += 1
            
            if analysis['harvest_timing']['recommendation'] in ['HARVEST_NOW', 'HARVEST_SOON']:
                harvest_recommendations.append({
                    'symbol': symbol,
                    'recommendation': analysis['harvest_timing']['recommendation'],
                    'confidence': analysis['harvest_timing']['confidence'],
                    'timing_score': analysis['harvest_timing']['timing_score']
                })
        
        # Sort by timing score (highest = most urgent to harvest)
        harvest_recommendations.sort(key=lambda x: x['timing_score'], reverse=True)
        
        return {
            'sentiment_distribution': sentiment_counts,
            'risk_distribution': risk_counts,
            'harvest_recommendations': harvest_recommendations,
            'high_priority_harvests': [r for r in harvest_recommendations if r['recommendation'] == 'HARVEST_NOW']
        }
    
    def format_for_agents(self, portfolio_analysis: Dict[str, Any]) -> str:
        """
        Format analysis into readable context string for agents.
        
        Args:
            portfolio_analysis: Output from get_portfolio_analysis()
            
        Returns:
            Formatted string for agent prompts
        """
        lines = ["\n=== MARKET ANALYSIS ==="]
        
        for symbol, analysis in portfolio_analysis['stocks'].items():
            lines.append(f"\n{symbol}:")
            
            # Sentiment
            sent = analysis['sentiment']
            lines.append(f"  News Sentiment: {sent['sentiment_score']} ({sent['article_count']} articles)")
            
            # Risk
            risk = analysis['risk_assessment']
            lines.append(f"  Risk Level: {risk['risk_level']} (score: {risk['risk_score']}/100)")
            
            # Market stats
            if analysis.get('market_stats'):
                stats = analysis['market_stats']
                lines.append(f"  Volatility: {stats['volatility']:.2%} daily")
                lines.append(f"  6M Return: {stats['total_return_6m']:.1%}")
                lines.append(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
            
            # Technical levels
            if analysis.get('technical'):
                tech = analysis['technical']
                lines.append(f"  Support: ₹{tech['support_level']:.1f} ({tech['distance_from_support']:.1f}% away)")
                lines.append(f"  Resistance: ₹{tech['resistance_level']:.1f} ({tech['distance_from_resistance']:.1f}% away)")
            
            # Harvest timing
            timing = analysis['harvest_timing']
            lines.append(f"  Harvest Timing: {timing['recommendation']} (confidence: {timing['confidence']})")
            
        lines.append("\n" + "="*30)
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = MarketAnalyzer()
    
    # Test single stock
    analysis = analyzer.analyze_stock(
        symbol="RELIANCE.NS",
        current_price=2450,
        cost_basis=2600,
        holding_days=210
    )
    
    print("\nStock Analysis:")
    import json
    print(json.dumps(analysis, indent=2))
