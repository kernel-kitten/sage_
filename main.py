"""Main application entry point for Agentic RAG system using Google Gemini and Local Embeddings"""

import sys
import os
from pathlib import Path

# 1. Path Setup: Ensures 'import src' works from the root
root_path = Path(__file__).resolve().parent.parent # Adjusted to find 'src' from 'src/main.py'
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path)) 

from src.config.config import Config
from src.document_ingestion.document_processor import DocumentProcessor
from src.vectorstore.vectorstore import VectorStore 
from src.graph_builder.graph_builder import GraphBuilder

class AgenticRAG:
    """Main Agentic RAG application"""
    
    def __init__(self, urls=None):
        """
        Initialize Agentic RAG system with local embeddings and Gemini brain
        """
        print("🚀 Initializing Agentic RAG (Gemini + Local BGE Embeddings)...")
        
        self.urls = urls or getattr(Config, 'DEFAULT_URLS', [])
        
        # Initialize components
        self.llm = Config.get_llm()
        self.doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.vector_store = VectorStore()
        
        # Process logic: Try to load existing index first to save time/CPU
        if not self.vector_store.load_local_vectorstore():
            if self.urls:
                self._setup_vectorstore()
            else:
                print("⚠️ Warning: No URLs and no local index found.")
        else:
            print("📁 Loaded existing FAISS index from disk.")
        
        # Build LangGraph
        self.graph_builder = GraphBuilder(
            retriever=self.vector_store.get_retriever(),
            llm=self.llm
        )
        self.graph_builder.build()
        
        print("✅ System ready!\n")
    
    def _setup_vectorstore(self):
        """Setup vector store with processed documents"""
        print(f"📄 Processing {len(self.urls)} source(s)...")
        documents = self.doc_processor.process_urls(self.urls)
        
        print(f"📊 Created {len(documents)} chunks. Embedding locally (this may take a minute)...")
        self.vector_store.create_vectorstore(documents)
    
    def ask(self, question: str) -> str:
        """Invoke the RAG Graph"""
        print(f"❓ Question: {question}")
        print("🤔 Agent is thinking and searching tools...")
        
        result = self.graph_builder.run(question)
        answer = result.get('answer', "No answer generated.")
        
        print(f"✅ Answer: {answer}\n")
        return answer

    def interactive_mode(self):
        print("\n💬 Interactive Mode - Type 'exit' to quit")
        while True:
            try:
                q = input("User: ").strip()
                if q.lower() in ['quit', 'exit', 'q']: break
                if q: self.ask(q)
            except KeyboardInterrupt:
                break

def main():
    # Attempt to load URLs from local data folder
    urls_file = Path("data/urls.txt")
    urls = None
    if urls_file.exists():
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

    try:
        rag = AgenticRAG(urls=urls)
        
        # Run a test question
        rag.ask("What are the core components of an LLM agent?")
        
        user_input = input("Enter interactive mode? (y/n): ")
        if user_input.lower() == 'y':
            rag.interactive_mode()
    except Exception as e:
        print(f"❌ Initialization Error: {e}")

if __name__ == "__main__":
    main()