"""
Corpus loader: Loads and indexes all support documents for RAG
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class CorpusLoader:
    def __init__(self, data_dir: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize corpus loader with vector embeddings
        
        Args:
            data_dir: Path to data directory (containing claude/, hackerrank/, visa/)
            model_name: Sentence transformer model for embeddings
        """
        self.data_dir = Path(data_dir)
        self.model = SentenceTransformer(model_name)
        self.documents = []  # List of (text, metadata) tuples
        self.index = None
        self.metadata = []
        
    def load_corpus(self) -> None:
        """Load all markdown files from the corpus"""
        self._load_domain("claude")
        self._load_domain("hackerrank")
        self._load_domain("visa")
        
    def _load_domain(self, domain: str) -> None:
        """Load all markdown files from a domain"""
        domain_path = self.data_dir / domain
        if not domain_path.exists():
            return
            
        for md_file in domain_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip index files and empty files
                if not content.strip() or md_file.name == "index.md":
                    continue
                
                # Extract product area from path
                relative_path = md_file.relative_to(domain_path)
                product_area = str(relative_path.parent)
                
                # Create metadata
                metadata = {
                    "domain": domain,
                    "file": str(md_file),
                    "product_area": product_area,
                    "title": md_file.stem
                }
                
                self.documents.append(content)
                self.metadata.append(metadata)
                
            except Exception as e:
                print(f"Error loading {md_file}: {e}")
    
    def build_index(self) -> None:
        """Build FAISS index from documents"""
        if not self.documents:
            print("No documents loaded!")
            return
        
        print(f"Building index for {len(self.documents)} documents...")
        
        # Generate embeddings
        embeddings = self.model.encode(self.documents, convert_to_numpy=True)
        embeddings = embeddings.astype('float32')
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        print(f"Index built with {self.index.ntotal} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict, float]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of (document_text, metadata, score) tuples
        """
        if self.index is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                score = float(distances[0][i])
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    score
                ))
        
        return results
    
    def get_domain_documents(self, domain: str) -> List[str]:
        """Get all documents for a specific domain"""
        docs = []
        for doc, meta in zip(self.documents, self.metadata):
            if meta["domain"] == domain:
                docs.append(doc)
        return docs
