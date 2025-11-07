"""
Vector store for managing tax law and compliance documents using ChromaDB.
"""

import os
import logging
from typing import List, Dict, Optional
import hashlib

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages ChromaDB vector store for tax law and compliance documents."""
    
    def __init__(self, persist_dir: str = "./data/chroma_db"):
        """
        Initialize vector store.
        
        Args:
            persist_dir: Directory to persist ChromaDB data
        """
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
        
        if CHROMA_AVAILABLE:
            self._initialize_chroma()
        else:
            logger.warning("ChromaDB not available. Install with: pip install chromadb")
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            os.makedirs(self.persist_dir, exist_ok=True)
            
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_dir,
                anonymized_telemetry=False
            )
            
            self.client = chromadb.Client(settings)
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="tax_law_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Vector store initialized at {self.persist_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_documents(self, documents: List[str], metadata: Optional[List[Dict]] = None):
        """
        Add documents to vector store.
        
        Args:
            documents: List of text documents
            metadata: List of metadata dicts corresponding to documents
        """
        if not self.collection:
            logger.warning("Vector store not initialized")
            return
        
        try:
            ids = []
            for i, doc in enumerate(documents):
                doc_id = hashlib.md5(doc.encode()).hexdigest()[:12]
                ids.append(doc_id)
            
            meta = metadata or [{"source": f"doc_{i}"} for i in range(len(documents))]
            
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=meta
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """
        Search vector store for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            Dict with ids, distances, documents, and metadata
        """
        if not self.collection:
            logger.warning("Vector store not initialized")
            return {"documents": [], "metadatas": [], "distances": []}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"documents": [], "metadatas": [], "distances": []}
    
    def load_income_tax_documents(self, data_dir: str = "./data/income_tax_law_texts/"):
        """
        Load income tax documents from directory.
        
        Args:
            data_dir: Directory containing tax law text files
        """
        if not os.path.exists(data_dir):
            logger.warning(f"Data directory not found: {data_dir}")
            return
        
        documents = []
        metadata = []
        
        for filename in os.listdir(data_dir):
            if filename.endswith(('.txt', '.md')):
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(content)
                        metadata.append({
                            "source": filename,
                            "type": "income_tax_act"
                        })
                except Exception as e:
                    logger.error(f"Failed to read {filepath}: {e}")
        
        if documents:
            self.add_documents(documents, metadata)
            logger.info(f"Loaded {len(documents)} tax documents from {data_dir}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about the vector store."""
        if not self.collection:
            return {"status": "not_initialized"}
        
        try:
            count = self.collection.count()
            return {
                "status": "initialized",
                "document_count": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"status": "error", "error": str(e)}


# Global instance
_vector_store = None


def get_vector_store(persist_dir: str = "./data/chroma_db") -> VectorStore:
    """Get or create global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(persist_dir)
    return _vector_store
