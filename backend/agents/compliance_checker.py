"""
Regulatory Compliance Checker Agent - Validates tax-loss harvesting compliance.
"""

import logging
from typing import Dict, Any, List

from backend.utils.data_models import (
    ComplianceCheckResult, ComplianceStatus, TaxLossOpportunity
)
from backend.utils.groq_client import GroqLLMClient
from backend.utils.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RegulatoryComplianceAgent:
    """
    Validates tax-loss harvesting transactions against Indian tax regulations.
    Uses RAG (Retrieval-Augmented Generation) with ChromaDB for tax law reasoning.
    """
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize Compliance Agent.
        
        Args:
            llm_client: GroqLLMClient instance for LLM operations
        """
        self.llm_client = llm_client
        self.vector_store = get_vector_store()
        self.logger = logging.getLogger(__name__)
    
    def check_compliance(
        self,
        opportunity: TaxLossOpportunity
    ) -> ComplianceCheckResult:
        """
        Check if a tax-loss harvesting opportunity complies with Indian tax regulations.
        
        Args:
            opportunity: TaxLossOpportunity to validate
        
        Returns:
            ComplianceCheckResult with compliance status and reasoning
        """
        self.logger.info(f"Checking compliance for {opportunity.holding.symbol}")
        
        # Retrieve relevant regulations
        query = f"tax-loss harvesting wash sale exemption {opportunity.holding.symbol}"
        relevant_docs = self._retrieve_relevant_regulations(query)
        
        # Use LLM for RAG-based reasoning
        compliance_check = self._perform_rag_check(opportunity, relevant_docs)
        
        return compliance_check
    
    def check_batch_compliance(
        self,
        opportunities: List[TaxLossOpportunity]
    ) -> List[ComplianceCheckResult]:
        """
        Check compliance for multiple opportunities.
        
        Args:
            opportunities: List of opportunities to check
        
        Returns:
            List of ComplianceCheckResult objects
        """
        results = []
        for opportunity in opportunities:
            result = self.check_compliance(opportunity)
            results.append(result)
        
        return results
    
    def _retrieve_relevant_regulations(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant tax regulations using vector store.
        
        Args:
            query: Search query
        
        Returns:
            Retrieved documents and metadata
        """
        try:
            results = self.vector_store.search(query, n_results=5)
            
            if results.get("documents"):
                self.logger.debug(f"Retrieved {len(results['documents'][0])} relevant documents")
            
            return results
        
        except Exception as e:
            self.logger.warning(f"Failed to retrieve regulations: {e}")
            return {"documents": [[], []], "metadatas": [[]]}
    
    def _perform_rag_check(
        self,
        opportunity: TaxLossOpportunity,
        retrieved_docs: Dict[str, Any]
    ) -> ComplianceCheckResult:
        """
        Use LLM with RAG to perform compliance check.
        
        Args:
            opportunity: Opportunity to check
            retrieved_docs: Retrieved regulatory documents
        
        Returns:
            ComplianceCheckResult
        """
        try:
            # Build context from retrieved documents
            doc_context = ""
            regulation_refs = []
            
            if retrieved_docs.get("documents") and retrieved_docs["documents"][0]:
                for idx, doc in enumerate(retrieved_docs["documents"][0][:3]):
                    doc_context += f"\n\nRegulation {idx + 1}:\n{doc[:500]}"
                    
                    if retrieved_docs.get("metadatas") and retrieved_docs["metadatas"][0]:
                        meta = retrieved_docs["metadatas"][0][idx]
                        if meta.get("source"):
                            regulation_refs.append(meta["source"])
            
            # Create prompt
            system_prompt = """You are an expert on Indian tax law and regulations.
Analyze the tax-loss harvesting transaction for compliance with Indian Income Tax Act.
Consider wash-sale rules, exemption limits, and other relevant regulations.

Return a JSON response with:
- is_compliant: boolean
- status: "compliant", "non_compliant", or "needs_review"
- risk_level: "low", "medium", or "high"
- explanation: detailed explanation
- suggested_fix: optional suggestion if non-compliant"""
            
            transaction_info = f"""
Transaction Details:
- Symbol: {opportunity.holding.symbol}
- Stock Name: {opportunity.holding.stock_name}
- Quantity: {opportunity.holding.quantity}
- Purchase Price: ${opportunity.holding.purchase_price}
- Current Price: ${opportunity.holding.current_price}
- Unrealized Loss: ${opportunity.unrealized_loss}
- Loss Percentage: {opportunity.loss_percentage}%
- Holding Period: {(datetime.now() - opportunity.holding.purchase_date).days} days

Relevant Regulations:
{doc_context}

Analyze if this transaction complies with Indian tax regulations."""
            
            # Get LLM response
            result_json = self.llm_client.json_chat(
                transaction_info,
                system_prompt,
                temperature=0.3,
                max_tokens=1024
            )
            
            # Build result
            return ComplianceCheckResult(
                is_compliant=result_json.get("is_compliant", False),
                status=ComplianceStatus(result_json.get("status", "needs_review")),
                regulation_references=regulation_refs,
                explanation=result_json.get("explanation", ""),
                risk_level=result_json.get("risk_level", "medium"),
                suggested_fix=result_json.get("suggested_fix")
            )
        
        except Exception as e:
            self.logger.error(f"RAG check failed: {e}")
            return ComplianceCheckResult(
                is_compliant=False,
                status=ComplianceStatus.NEEDS_REVIEW,
                explanation=f"Error during compliance check: {e}",
                risk_level="high"
            )
    
    def check_wash_sale_rule(
        self,
        sold_symbol: str,
        purchase_date: Any,
        replacement_symbol: str
    ) -> Dict[str, Any]:
        """
        Check wash-sale rule compliance.
        
        Args:
            sold_symbol: Symbol being sold
            purchase_date: When the loss is being harvested
            replacement_symbol: Replacement security symbol
        
        Returns:
            Dict with wash-sale analysis
        """
        # Wash-sale rule: Cannot repurchase substantially identical security
        # within 30 days before or after
        
        substantially_identical = sold_symbol.upper() == replacement_symbol.upper()
        
        return {
            "rule": "Wash-Sale Rule",
            "violated": substantially_identical,
            "details": {
                "original_security": sold_symbol,
                "replacement_security": replacement_symbol,
                "substantially_identical": substantially_identical,
                "wash_sale_window_days": 30
            },
            "explanation": (
                "The replacement security is substantially identical to the sold security. "
                "This triggers the wash-sale rule, and the loss cannot be claimed."
            ) if substantially_identical else (
                "The replacement security is not substantially identical. "
                "Wash-sale rule does not apply."
            )
        }
    
    def check_exemption_limits(
        self,
        total_harvested_loss: float,
        applicable_period: str = "financial_year"
    ) -> Dict[str, Any]:
        """
        Check if harvested loss exceeds exemption/deduction limits.
        
        Args:
            total_harvested_loss: Total harvested loss amount
            applicable_period: Period for limit check
        
        Returns:
            Dict with limit analysis
        """
        # Indian tax law: Capital loss can be set off against capital gains
        # Excess can be carried forward for 8 years
        
        limits = {
            "financial_year": float('inf'),  # No limit in current FY
            "carryforward_years": 8
        }
        
        return {
            "rule": "Exemption/Deduction Limits",
            "total_harvested_loss": total_harvested_loss,
            "limit_type": applicable_period,
            "within_limit": True,
            "explanation": (
                "Capital losses can be set off against capital gains. "
                "Excess losses can be carried forward for up to 8 years."
            )
        }
    
    def generate_compliance_report(
        self,
        opportunities: List[TaxLossOpportunity],
        compliance_results: List[ComplianceCheckResult]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.
        
        Args:
            opportunities: List of opportunities
            compliance_results: Corresponding compliance results
        
        Returns:
            Comprehensive compliance report
        """
        compliant_count = sum(1 for r in compliance_results if r.is_compliant)
        non_compliant_count = sum(1 for r in compliance_results if not r.is_compliant)
        needs_review = sum(1 for r in compliance_results if r.status == ComplianceStatus.NEEDS_REVIEW)
        
        high_risk = sum(1 for r in compliance_results if r.risk_level == "high")
        
        return {
            "total_opportunities_checked": len(compliance_results),
            "compliant": compliant_count,
            "non_compliant": non_compliant_count,
            "needs_review": needs_review,
            "high_risk_count": high_risk,
            "compliance_rate": f"{compliant_count / len(compliance_results) * 100:.1f}%" if compliance_results else "0%",
            "recommendations": self._generate_recommendations(compliance_results)
        }
    
    def _generate_recommendations(
        self,
        compliance_results: List[ComplianceCheckResult]
    ) -> List[str]:
        """Generate recommendations based on compliance results."""
        recommendations = []
        
        non_compliant = [r for r in compliance_results if not r.is_compliant]
        if non_compliant:
            recommendations.append(
                f"Review {len(non_compliant)} non-compliant transactions before execution"
            )
        
        high_risk = [r for r in compliance_results if r.risk_level == "high"]
        if high_risk:
            recommendations.append(
                f"Consult tax professional for {len(high_risk)} high-risk transactions"
            )
        
        if not recommendations:
            recommendations.append("All transactions are compliant. Safe to proceed.")
        
        return recommendations


from datetime import datetime
