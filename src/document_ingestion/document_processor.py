"""Document processing module for loading and splitting documents using Local HuggingFace Embeddings"""

import os
from typing import List, Union
from pathlib import Path
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFDirectoryLoader,
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# NEW: Local Embedding Import
from langchain_huggingface import HuggingFaceEmbeddings

class DocumentProcessor:
    """Handles document loading and processing with free local embeddings"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Optimized separators for better semantic retrieval
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""] 
        )

    def get_embeddings(self):
        """
        Returns a high-performance, FREE HuggingFace embedding model.
        This runs locally on your machine's CPU.
        """
        # BGE-Small is the 2026 'Gold Standard' for local RAG
        model_name = "BAAI/bge-small-en-v1.5"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True} 
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

    def load_from_url(self, url: str) -> List[Document]:
        """Load content from a web URL"""
        loader = WebBaseLoader(url)
        return loader.load()

    def load_from_pdf_dir(self, directory: Union[str, Path]) -> List[Document]:
        """Load all PDFs from a directory"""
        loader = PyPDFDirectoryLoader(str(directory))
        return loader.load()

    def load_from_txt(self, file_path: Union[str, Path]) -> List[Document]:
        """Load a single text file"""
        loader = TextLoader(str(file_path), encoding="utf-8")
        return loader.load()

    def load_documents(self, sources: List[str]) -> List[Document]:
        """
        Smart loader that identifies source types
        """
        docs: List[Document] = []
        for src in sources:
            if src.startswith("http://") or src.startswith("https://"):
                docs.extend(self.load_from_url(src))
            else:
                path = Path(src)
                if path.is_dir():
                    docs.extend(self.load_from_pdf_dir(path))
                elif path.suffix.lower() == ".txt":
                    docs.extend(self.load_from_txt(path))
                elif path.suffix.lower() == ".pdf":
                    # Single PDF logic
                    docs.extend(self.load_from_pdf_dir(path.parent))
        return docs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split loaded documents into chunks"""
        return self.splitter.split_documents(documents)
    
    def process_sources(self, sources: List[str]) -> List[Document]:
        """General pipeline to load and split documents"""
        docs = self.load_documents(sources)
        return self.split_documents(docs)

    def process_urls(self, urls: List[str]) -> List[Document]:
        """
        Alias for process_sources to maintain compatibility with main.py
        """
        return self.process_sources(urls)