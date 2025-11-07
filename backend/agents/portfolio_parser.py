"""
Portfolio Parser Agent - Parses uploaded portfolio files.
"""

import logging
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
import csv

from backend.utils.data_models import PortfolioHolding
from backend.utils.groq_client import GroqLLMClient

logger = logging.getLogger(__name__)


class PortfolioParserAgent:
    """
    Parses uploaded portfolio files (CSV, PDF, or Excel).
    Extracts portfolio holdings with stock details.
    """
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize Portfolio Parser Agent.
        
        Args:
            llm_client: GroqLLMClient instance for LLM operations
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
    
    def parse_portfolio(self, file_data: bytes, file_type: str) -> Dict[str, Any]:
        """
        Parse portfolio file and extract holdings.
        
        Args:
            file_data: Binary file data
            file_type: Type of file ('csv', 'pdf', 'excel')
        
        Returns:
            Dict with parsed portfolio data
        """
        self.logger.info(f"Parsing portfolio file of type: {file_type}")
        
        try:
            if file_type.lower() == "csv":
                return self._parse_csv(file_data)
            elif file_type.lower() == "pdf":
                return self._parse_pdf(file_data)
            elif file_type.lower() in ["excel", "xlsx"]:
                return self._parse_excel(file_data)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported file type: {file_type}",
                    "holdings": []
                }
        except Exception as e:
            self.logger.error(f"Portfolio parsing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "holdings": [],
                "error_type": type(e).__name__
            }
    
    def _parse_csv(self, file_data: bytes) -> Dict[str, Any]:
        """Parse CSV file using heuristics."""
        try:
            text = file_data.decode('utf-8')
            file_obj = io.StringIO(text)
            
            reader = csv.DictReader(file_obj)
            holdings = []
            
            # Expected columns (case-insensitive)
            expected_cols = {
                'stock_name': ['stock name', 'symbol', 'ticker', 'stock'],
                'quantity': ['quantity', 'qty', 'shares', 'units'],
                'purchase_date': ['purchase date', 'buy date', 'acquired date'],
                'purchase_price': ['purchase price', 'buy price', 'cost per share'],
                'current_price': ['current price', 'market price', 'price']
            }
            
            # Find columns (case-insensitive)
            header = {k.lower(): k for k in reader.fieldnames or []}
            col_map = {}
            
            for expected_key, aliases in expected_cols.items():
                for alias in aliases:
                    if alias in header:
                        col_map[expected_key] = header[alias]
                        break
            
            if not col_map.get('stock_name'):
                return {
                    "status": "error",
                    "message": "Could not find stock name column",
                    "holdings": []
                }
            
            for row_idx, row in enumerate(reader, start=2):
                try:
                    holding = self._parse_csv_row(row, col_map)
                    if holding:
                        holdings.append(holding)
                except Exception as e:
                    self.logger.warning(f"Skipping row {row_idx}: {e}")
            
            return {
                "status": "success",
                "message": f"Parsed {len(holdings)} holdings from CSV",
                "holdings": holdings,
                "total_holdings": len(holdings)
            }
        
        except Exception as e:
            logger.error(f"CSV parsing error: {e}")
            return {
                "status": "error",
                "message": f"CSV parsing failed: {e}",
                "holdings": []
            }
    
    def _parse_csv_row(self, row: Dict[str, str], col_map: Dict[str, str]) -> Optional[PortfolioHolding]:
        """Parse a single CSV row into PortfolioHolding."""
        try:
            stock_name = row.get(col_map.get('stock_name', ''), '').strip()
            
            if not stock_name:
                return None
            
            # Extract symbol (first part before space if not available)
            symbol = stock_name.split()[0].upper()
            
            quantity = float(row.get(col_map.get('quantity', ''), 0))
            purchase_price = float(row.get(col_map.get('purchase_price', ''), 0))
            current_price = float(row.get(col_map.get('current_price', ''), 0))
            
            # Parse purchase date
            purchase_date_str = row.get(col_map.get('purchase_date', ''), '')
            purchase_date = self._parse_date(purchase_date_str)
            
            if quantity > 0 and purchase_price >= 0 and current_price >= 0:
                return PortfolioHolding(
                    stock_name=stock_name,
                    symbol=symbol,
                    quantity=quantity,
                    purchase_date=purchase_date,
                    purchase_price=purchase_price,
                    current_price=current_price
                )
        
        except (ValueError, KeyError) as e:
            self.logger.debug(f"Row parsing error: {e}")
        
        return None
    
    def _parse_pdf(self, file_data: bytes) -> Dict[str, Any]:
        """Parse PDF file using LLM reasoning."""
        try:
            # Try to extract text from PDF
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            except ImportError:
                logger.warning("PyPDF2 not installed. Attempting basic parsing.")
                text = file_data.decode('utf-8', errors='ignore')
            
            if not text.strip():
                return {
                    "status": "error",
                    "message": "Could not extract text from PDF",
                    "holdings": []
                }
            
            # Use LLM to extract portfolio data
            system_prompt = """You are an expert at parsing financial documents.
Extract portfolio holdings from the provided text. Return a JSON array with objects containing:
- stock_name: Name of the stock
- symbol: Stock ticker symbol
- quantity: Number of shares
- purchase_price: Price paid per share
- current_price: Current market price
- purchase_date: Date of purchase (YYYY-MM-DD format)

Return ONLY valid JSON array, no markdown or explanation."""
            
            user_message = f"Extract portfolio holdings from this document:\n\n{text[:2000]}"
            
            try:
                holdings_json = self.llm_client.json_chat(
                    user_message,
                    system_prompt,
                    temperature=0.3
                )
                
                holdings = []
                if isinstance(holdings_json, list):
                    for item in holdings_json:
                        holding = self._json_to_holding(item)
                        if holding:
                            holdings.append(holding)
                
                return {
                    "status": "success",
                    "message": f"Parsed {len(holdings)} holdings from PDF using LLM",
                    "holdings": holdings,
                    "total_holdings": len(holdings)
                }
            except Exception as e:
                logger.error(f"LLM parsing error: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to parse PDF with LLM: {e}",
                    "holdings": []
                }
        
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            return {
                "status": "error",
                "message": f"PDF parsing failed: {e}",
                "holdings": []
            }
    
    def _parse_excel(self, file_data: bytes) -> Dict[str, Any]:
        """Parse Excel file."""
        try:
            try:
                import openpyxl
                workbook = openpyxl.load_workbook(io.BytesIO(file_data))
                sheet = workbook.active
                
                rows = list(sheet.iter_rows(values_only=True))
                
                if not rows:
                    return {
                        "status": "error",
                        "message": "Excel file is empty",
                        "holdings": []
                    }
                
                # Treat first row as header
                header = [str(cell).lower() if cell else '' for cell in rows[0]]
                
                # Find column indices
                col_indices = self._find_column_indices(header)
                
                if not col_indices.get('stock_name'):
                    return {
                        "status": "error",
                        "message": "Could not find stock name column",
                        "holdings": []
                    }
                
                holdings = []
                for row_idx, row in enumerate(rows[1:], start=2):
                    try:
                        holding = self._parse_excel_row(row, col_indices)
                        if holding:
                            holdings.append(holding)
                    except Exception as e:
                        self.logger.warning(f"Skipping row {row_idx}: {e}")
                
                return {
                    "status": "success",
                    "message": f"Parsed {len(holdings)} holdings from Excel",
                    "holdings": holdings,
                    "total_holdings": len(holdings)
                }
            
            except ImportError:
                logger.error("openpyxl not installed")
                return {
                    "status": "error",
                    "message": "openpyxl not installed. Install with: pip install openpyxl",
                    "holdings": []
                }
        
        except Exception as e:
            logger.error(f"Excel parsing error: {e}")
            return {
                "status": "error",
                "message": f"Excel parsing failed: {e}",
                "holdings": []
            }
    
    def _find_column_indices(self, header: List[str]) -> Dict[str, int]:
        """Find column indices from header."""
        expected_cols = {
            'stock_name': ['stock name', 'symbol', 'ticker', 'stock'],
            'quantity': ['quantity', 'qty', 'shares', 'units'],
            'purchase_date': ['purchase date', 'buy date', 'acquired date'],
            'purchase_price': ['purchase price', 'buy price', 'cost per share'],
            'current_price': ['current price', 'market price', 'price']
        }
        
        col_indices = {}
        for expected_key, aliases in expected_cols.items():
            for alias in aliases:
                for idx, col in enumerate(header):
                    if alias in col:
                        col_indices[expected_key] = idx
                        break
                if expected_key in col_indices:
                    break
        
        return col_indices
    
    def _parse_excel_row(self, row: tuple, col_indices: Dict[str, int]) -> Optional[PortfolioHolding]:
        """Parse Excel row into PortfolioHolding."""
        try:
            stock_name_idx = col_indices.get('stock_name')
            if stock_name_idx is None or stock_name_idx >= len(row):
                return None
            
            stock_name = str(row[stock_name_idx]).strip()
            if not stock_name:
                return None
            
            symbol = stock_name.split()[0].upper()
            
            quantity = float(row[col_indices.get('quantity', -1)] or 0)
            purchase_price = float(row[col_indices.get('purchase_price', -1)] or 0)
            current_price = float(row[col_indices.get('current_price', -1)] or 0)
            
            purchase_date_idx = col_indices.get('purchase_date')
            purchase_date_val = row[purchase_date_idx] if purchase_date_idx and purchase_date_idx < len(row) else None
            purchase_date = self._parse_date(str(purchase_date_val) if purchase_date_val else '')
            
            if quantity > 0 and purchase_price >= 0 and current_price >= 0:
                return PortfolioHolding(
                    stock_name=stock_name,
                    symbol=symbol,
                    quantity=quantity,
                    purchase_date=purchase_date,
                    purchase_price=purchase_price,
                    current_price=current_price
                )
        
        except (ValueError, IndexError) as e:
            self.logger.debug(f"Excel row parsing error: {e}")
        
        return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime."""
        if not date_str:
            return datetime.now()
        
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # If all formats fail, return today
        logger.debug(f"Could not parse date: {date_str}")
        return datetime.now()
    
    def _json_to_holding(self, data: Dict[str, Any]) -> Optional[PortfolioHolding]:
        """Convert JSON dict to PortfolioHolding."""
        try:
            return PortfolioHolding(
                stock_name=data.get('stock_name', 'Unknown'),
                symbol=data.get('symbol', 'UNKNOWN').upper(),
                quantity=float(data.get('quantity', 0)),
                purchase_date=self._parse_date(data.get('purchase_date', '')),
                purchase_price=float(data.get('purchase_price', 0)),
                current_price=float(data.get('current_price', 0))
            )
        except (ValueError, KeyError, TypeError):
            return None
