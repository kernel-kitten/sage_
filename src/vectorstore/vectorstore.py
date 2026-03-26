"""Vector store module for document embedding and retrieval using Local HuggingFace Models"""

import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
# NEW: Import local HuggingFace embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config.config import Config 

class VectorStore:
    """Manages vector store operations using FREE local HuggingFace embeddings"""
    
    def __init__(self):
        """Initialize vector store with BGE-Small (Local CPU)"""
        # BGE models are top-tier for local RAG. 
        # They run on your CPU/RAM with 0 API costs.
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore: Optional[FAISS] = None
        self.retriever = None
        # Path to save the index locally
        self.index_path = "faiss_index"
    
    def create_vectorstore(self, documents: List[Document]):
        """
        Create and save a local vector store from documents
        """
        if not documents:
            raise ValueError("No documents provided to create vector store.")
            
        # This will download the ~130MB model on the FIRST run only
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # PRO TIP: Save the index locally so you don't have to re-process 
        # the same documents every time you refresh the Streamlit app.
        self.vectorstore.save_local(self.index_path)
        
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
    
    def load_local_vectorstore(self):
        """
        Load an existing vector store from disk if it exists
        """
        if os.path.exists(self.index_path):
            self.vectorstore = FAISS.load_local(
                self.index_path, 
                self.embeddings,
                allow_dangerous_deserialization=True # Required for FAISS files
            )
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
            return True
        return False

    def get_retriever(self):
        """Get the retriever instance"""
        if self.retriever is None:
            # Try to load from disk before giving up
            if not self.load_local_vectorstore():
                raise ValueError("Vector store not initialized. Process documents first.")
        return self.retriever

    def retrieve(self, query: str) -> List[Document]:
        """Retrieve relevant documents for a query"""
        if self.vectorstore is None:
            if not self.load_local_vectorstore():
                raise ValueError("Vector store not initialized.")
        
        return self.vectorstore.similarity_search(query, k=4)