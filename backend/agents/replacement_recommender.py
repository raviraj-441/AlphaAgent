"""
Replacement Security Recommender Agent - Suggests alternative securities.
"""

import logging
import math
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

from backend.utils.data_models import ReplacementSecurity, TaxLossOpportunity
from backend.utils.groq_client import GroqLLMClient

logger = logging.getLogger(__name__)


class ReplacementRecommenderAgent:
    """
    Recommends replacement securities for tax-loss harvested stocks.
    Uses correlation analysis and semantic similarity checking.
    """
    
    CORRELATION_THRESHOLD = 0.85
    SEMANTIC_SIMILARITY_THRESHOLD = 0.75
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize Replacement Recommender Agent.
        
        Args:
            llm_client: GroqLLMClient instance for semantic checking
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        
        # Mock historical price data (in real system, fetch from Yahoo Finance)
        self.mock_price_data = self._load_mock_price_data()
    
    def recommend_replacements(
        self,
        opportunity: TaxLossOpportunity,
        candidate_symbols: List[str] = None
    ) -> List[ReplacementSecurity]:
        """
        Recommend replacement securities for a sold stock.
        
        Args:
            opportunity: TaxLossOpportunity being harvested
            candidate_symbols: List of candidate symbols to consider
        
        Returns:
            List of ReplacementSecurity recommendations
        """
        self.logger.info(f"Finding replacements for {opportunity.holding.symbol}")
        
        if candidate_symbols is None:
            # Generate candidates (similar sector, market cap, etc.)
            candidate_symbols = self._generate_candidates(opportunity.holding.symbol)
        
        recommendations = []
        
        for candidate_symbol in candidate_symbols:
            try:
                # Calculate correlation
                correlation = self._calculate_correlation(
                    opportunity.holding.symbol,
                    candidate_symbol
                )
                
                if correlation >= self.CORRELATION_THRESHOLD:
                    # Check semantic similarity
                    semantic_score = self._check_semantic_similarity(
                        opportunity.holding.symbol,
                        candidate_symbol,
                        opportunity.holding.stock_name
                    )
                    
                    if semantic_score >= self.SEMANTIC_SIMILARITY_THRESHOLD:
                        rec = ReplacementSecurity(
                            original_symbol=opportunity.holding.symbol,
                            recommended_symbol=candidate_symbol,
                            correlation_score=correlation,
                            semantic_similarity=semantic_score,
                            reason=f"High correlation ({correlation:.2f}) and semantic similarity ({semantic_score:.2f})",
                            risk_profile_match=0.95
                        )
                        recommendations.append(rec)
            
            except Exception as e:
                self.logger.debug(f"Error evaluating {candidate_symbol}: {e}")
        
        # Sort by correlation (descending)
        recommendations.sort(key=lambda x: x.correlation_score, reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    def _calculate_correlation(self, symbol1: str, symbol2: str) -> float:
        """
        Calculate price correlation between two symbols.
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
        
        Returns:
            Correlation score (0.0 to 1.0)
        """
        try:
            # Get mock price data
            prices1 = self.mock_price_data.get(symbol1.upper(), [])
            prices2 = self.mock_price_data.get(symbol2.upper(), [])
            
            if len(prices1) < 2 or len(prices2) < 2:
                return 0.0
            
            # Calculate correlation using Pearson coefficient
            correlation = self._pearson_correlation(prices1, prices2)
            
            return max(0.0, min(1.0, correlation))  # Clamp between 0 and 1
        
        except Exception as e:
            self.logger.debug(f"Correlation calculation error: {e}")
            return 0.0
    
    def _pearson_correlation(self, data1: List[float], data2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(data1) != len(data2) or len(data1) < 2:
            return 0.0
        
        n = len(data1)
        mean1 = sum(data1) / n
        mean2 = sum(data2) / n
        
        numerator = sum((data1[i] - mean1) * (data2[i] - mean2) for i in range(n))
        denom1 = math.sqrt(sum((x - mean1) ** 2 for x in data1))
        denom2 = math.sqrt(sum((x - mean2) ** 2 for x in data2))
        
        if denom1 == 0 or denom2 == 0:
            return 0.0
        
        return numerator / (denom1 * denom2)
    
    def _check_semantic_similarity(
        self,
        original_symbol: str,
        candidate_symbol: str,
        original_name: str
    ) -> float:
        """
        Use LLM to check semantic similarity between securities.
        
        Args:
            original_symbol: Original stock symbol
            candidate_symbol: Candidate replacement symbol
            original_name: Original stock name
        
        Returns:
            Semantic similarity score (0.0 to 1.0)
        """
        try:
            system_prompt = """You are an expert at evaluating investment similarity.
Compare two securities and rate their semantic and investment objective similarity on a scale of 0 to 1.
Consider: business model, market sector, customer base, investment objectives.

Return ONLY a JSON with: {"similarity_score": <number between 0 and 1>, "reason": "<brief reason>"}"""
            
            user_message = f"""Compare these two stocks:
1. {original_symbol} ({original_name}) - Original stock
2. {candidate_symbol} - Replacement candidate

Are they similar in business model and investment objectives?"""
            
            response = self.llm_client.json_chat(
                user_message,
                system_prompt,
                temperature=0.3,
                max_tokens=256
            )
            
            score = float(response.get("similarity_score", 0.0))
            return max(0.0, min(1.0, score))
        
        except Exception as e:
            self.logger.debug(f"Semantic similarity check failed: {e}")
            # Return a moderate default score
            return 0.7
    
    def _generate_candidates(self, symbol: str) -> List[str]:
        """
        Generate candidate replacement symbols.
        
        Args:
            symbol: Original symbol
        
        Returns:
            List of candidate symbols
        """
        # Mock candidates for Indian market
        sector_peers = {
            'TCS': ['INFY', 'WIPRO', 'HCLTECH', 'LTIM'],
            'INFY': ['TCS', 'WIPRO', 'HCLTECH', 'LTIM'],
            'RELIANCE': ['BHARTIARTL', 'JSWSTEEL', 'TATASTEEL'],
            'ITC': ['BRITANNIA', 'NESTLEIND', 'MARICO'],
            'HDFC': ['ICICIBANK', 'AXISBANK', 'KOTAK'],
            'MARUTI': ['HEROMOTOCO', 'TATAMOTOR', 'BAJAJFINSV'],
        }
        
        candidates = sector_peers.get(symbol.upper(), [
            'INFY', 'TCS', 'WIPRO', 'HCLTECH',  # Default IT stocks
            'HDFC', 'ICICIBANK', 'AXISBANK'     # Default finance stocks
        ])
        
        # Remove original symbol
        return [c for c in candidates if c != symbol.upper()]
    
    def _load_mock_price_data(self) -> Dict[str, List[float]]:
        """Load mock historical price data."""
        import random
        random.seed(42)
        
        symbols = [
            'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'LTIM',
            'RELIANCE', 'BHARTIARTL', 'JSWSTEEL', 'TATASTEEL',
            'ITC', 'BRITANNIA', 'NESTLEIND', 'MARICO',
            'HDFC', 'ICICIBANK', 'AXISBANK', 'KOTAK',
            'MARUTI', 'HEROMOTOCO', 'TATAMOTOR', 'BAJAJFINSV'
        ]
        
        data = {}
        for symbol in symbols:
            # Generate correlated random walk
            prices = [100]
            for _ in range(250):
                change = random.gauss(0.5, 3.0)
                prices.append(prices[-1] + change)
            data[symbol] = prices
        
        return data
    
    def evaluate_replacement(
        self,
        original: TaxLossOpportunity,
        replacement: ReplacementSecurity
    ) -> Dict[str, Any]:
        """
        Provide detailed evaluation of a replacement.
        
        Args:
            original: Original opportunity
            replacement: Replacement security
        
        Returns:
            Detailed evaluation
        """
        return {
            "original_symbol": original.holding.symbol,
            "replacement_symbol": replacement.recommended_symbol,
            "correlation_score": f"{replacement.correlation_score:.2f}",
            "semantic_similarity": f"{replacement.semantic_similarity:.2f}",
            "meets_correlation_threshold": replacement.correlation_score >= self.CORRELATION_THRESHOLD,
            "meets_semantic_threshold": replacement.semantic_similarity >= self.SEMANTIC_SIMILARITY_THRESHOLD,
            "overall_recommendation": "APPROVED" if (
                replacement.correlation_score >= self.CORRELATION_THRESHOLD and
                replacement.semantic_similarity >= self.SEMANTIC_SIMILARITY_THRESHOLD
            ) else "REVIEW_REQUIRED",
            "reason": replacement.reason
        }
    
    def batch_recommend(
        self,
        opportunities: List[TaxLossOpportunity]
    ) -> Dict[str, List[ReplacementSecurity]]:
        """
        Get recommendations for multiple opportunities.
        
        Args:
            opportunities: List of opportunities
        
        Returns:
            Dict mapping original symbols to replacement recommendations
        """
        recommendations = {}
        
        for opportunity in opportunities:
            recs = self.recommend_replacements(opportunity)
            recommendations[opportunity.holding.symbol] = recs
        
        return recommendations
