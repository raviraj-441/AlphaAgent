"""
Sample configuration and test data for tax-loss harvesting system.
"""

# Tax Brackets (2023-24, India)
TAX_BRACKETS = {
    "individual_resident": {
        "0_to_300k": 0.00,
        "300k_to_700k": 0.05,
        "700k_to_1m": 0.20,
        "above_1m": 0.30
    },
    "senior_citizen": {
        "0_to_500k": 0.00,
        "500k_to_1m": 0.20,
        "above_1m": 0.30
    }
}

# Sample Portfolio for Testing
SAMPLE_PORTFOLIO = [
    {
        "stock_name": "Tata Consultancy Services",
        "symbol": "TCS",
        "quantity": 100,
        "purchase_date": "2023-01-15",
        "purchase_price": 3500,
        "current_price": 3200
    },
    {
        "stock_name": "Infosys",
        "symbol": "INFY",
        "quantity": 50,
        "purchase_date": "2023-03-20",
        "purchase_price": 1800,
        "current_price": 1600
    },
    {
        "stock_name": "Reliance Industries",
        "symbol": "RELIANCE",
        "quantity": 75,
        "purchase_date": "2022-12-01",
        "purchase_price": 2600,
        "current_price": 2750
    },
    {
        "stock_name": "HDFC Bank",
        "symbol": "HDFC",
        "quantity": 25,
        "purchase_date": "2023-06-10",
        "purchase_price": 1500,
        "current_price": 1400
    },
    {
        "stock_name": "ITC Limited",
        "symbol": "ITC",
        "quantity": 200,
        "purchase_date": "2023-02-14",
        "purchase_price": 300,
        "current_price": 280
    }
]

# Sample Income Tax Law Text for ChromaDB
SAMPLE_TAX_DOCUMENTS = [
    {
        "title": "Income Tax Act - Capital Gains",
        "content": """
        Section 45: Capital Gains
        (1) Any gain arising from the transfer of a capital asset effected in the previous year 
        shall, save as otherwise provided in this Act, be chargeable to income-tax under the head 
        'Capital gains'.
        (2) The period for which a capital asset is held shall be determined as follows:—
        (a) where the capital asset is an equity share in a company or a unit of an equity oriented 
        fund or a unit of a business trust, and it is held for a period of less than twelve months, 
        it shall be treated as a short-term capital asset; otherwise it shall be treated as a 
        long-term capital asset.
        """
    },
    {
        "title": "Income Tax Act - Capital Loss",
        "content": """
        Section 71: Capital Loss
        (1) Any loss arising from the transfer of a capital asset shall be allowed as a deduction 
        under this section.
        (2) The loss shall be calculated as the difference between the cost of acquisition and 
        sale price.
        (3) Capital loss can be set off against capital gains of the same year.
        (4) If capital losses exceed capital gains, the excess loss can be carried forward for 
        up to 8 years.
        """
    },
    {
        "title": "Wash Sale Rule (Amended)",
        "content": """
        The wash-sale rule applies to securities transactions. If a taxpayer sells a security at 
        a loss and purchases a substantially identical security within 30 days before or after the 
        sale, the loss is disallowed.
        
        Substantially identical securities include:
        - Same stock
        - Rights to purchase the same stock
        - Stock options on the same stock
        - Substantially similar securities (bonds, debentures with same characteristics)
        """
    },
    {
        "title": "Tax Loss Harvesting - Compliance",
        "content": """
        Tax loss harvesting is a strategy to offset capital gains through strategic sale of 
        securities at a loss. For compliance:
        
        1. Ensure sufficient holding period (no wash sale violations)
        2. Maintain proper documentation (cost basis, purchase/sale dates)
        3. Comply with section 47 exemptions
        4. Report on ITR schedule
        5. Monitor carryforward of unused losses
        """
    }
]

# Monte Carlo Simulation Defaults
MONTE_CARLO_DEFAULTS = {
    "runs": 1000,
    "annual_return_mean": 0.08,
    "annual_return_std": 0.03,
    "inflation_rate": 0.04,
    "projection_years": 10
}

# Correlation Thresholds
CORRELATION_THRESHOLDS = {
    "high_correlation": 0.85,
    "medium_correlation": 0.70,
    "low_correlation": 0.50
}

# Tax Loss Constraints
TAX_LOSS_CONSTRAINTS = {
    "minimum_loss_amount": 100,  # USD
    "minimum_loss_percentage": 5,  # Percent
    "wash_sale_period": 30,  # Days
    "holding_period_warning": 30,  # Days
    "carryforward_years": 8
}

# Sector Peers (for Replacement Recommendations)
SECTOR_PEERS = {
    "IT": {
        "TCS": ["INFY", "WIPRO", "HCLTECH", "LTIM", "MPHASIS"],
        "INFY": ["TCS", "WIPRO", "HCLTECH", "LTIM", "MPHASIS"],
        "WIPRO": ["TCS", "INFY", "HCLTECH", "LTIM", "TECHM"],
    },
    "FINANCE": {
        "HDFC": ["ICICIBANK", "AXISBANK", "KOTAK", "INDUSIND"],
        "ICICIBANK": ["HDFC", "AXISBANK", "KOTAK", "INDUSIND"],
        "AXISBANK": ["HDFC", "ICICIBANK", "KOTAK", "INDUSIND"],
    },
    "ENERGY": {
        "RELIANCE": ["BHARTIARTL", "JSWSTEEL", "TATASTEEL"],
    },
    "CONSUMER": {
        "ITC": ["BRITANNIA", "NESTLEIND", "MARICO"],
        "BRITANNIA": ["ITC", "NESTLEIND", "MARICO"],
    }
}

# API Response Codes
API_RESPONSE_CODES = {
    "success": 200,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "internal_error": 500,
    "service_unavailable": 503
}

# Agent Configuration
AGENT_CONFIG = {
    "portfolio_parser": {
        "timeout": 30,
        "max_file_size_mb": 50,
        "supported_formats": ["csv", "pdf", "excel"]
    },
    "tax_loss_identifier": {
        "min_loss_threshold": 100,
        "min_loss_percentage": 5,
        "batch_size": 100
    },
    "compliance_checker": {
        "timeout": 20,
        "vector_search_results": 5,
        "llm_temperature": 0.3
    },
    "replacement_recommender": {
        "correlation_threshold": 0.85,
        "semantic_threshold": 0.75,
        "max_recommendations": 5
    },
    "tax_savings_calculator": {
        "monte_carlo_runs": 1000,
        "projection_years": 10,
        "annual_return_mean": 0.08,
        "annual_return_std": 0.03
    },
    "orchestrator": {
        "max_iterations": 3,
        "negotiation_timeout": 60
    }
}


# Utility function to create sample CSV
def create_sample_csv():
    """Create sample CSV for testing."""
    csv_content = """Stock Name,Symbol,Quantity,Purchase Date,Purchase Price,Current Price
Tata Consultancy Services,TCS,100,2023-01-15,3500,3200
Infosys,INFY,50,2023-03-20,1800,1600
Reliance Industries,RELIANCE,75,2022-12-01,2600,2750
HDFC Bank,HDFC,25,2023-06-10,1500,1400
ITC Limited,ITC,200,2023-02-14,300,280
"""
    return csv_content


if __name__ == "__main__":
    # Print sample portfolio
    print("Sample Portfolio:")
    for holding in SAMPLE_PORTFOLIO:
        print(f"  {holding['symbol']}: {holding['quantity']} @ ${holding['purchase_price']}")
    
    print("\nTax Loss Constraints:")
    for constraint, value in TAX_LOSS_CONSTRAINTS.items():
        print(f"  {constraint}: {value}")
    
    print("\nSample CSV:")
    print(create_sample_csv())
