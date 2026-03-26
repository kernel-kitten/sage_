"""Configuration module for Agentic RAG system using Groq and local Embeddings"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for RAG system using Groq"""
    
    # --- Identification ---
    USER_AGENT = "SageAgenticRAG/1.0"
    os.environ["USER_AGENT"] = USER_AGENT

    # --- API Keys ---
    # REPLACED: Now uses Groq API Key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # --- Model Configuration ---
    # Llama 3.1 8B is the 2026 sweet spot for speed and tool-calling accuracy on Groq
    LLM_MODEL = "llama-3.1-8b-instant"
    
    # --- Local Embedding Configuration (FREE & LOCAL) ---
    # We keep this local so you don't need a token for embeddings
    EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
    
    # --- Document Processing ---
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100  # Increased to 20% for better context retention
    
    # --- Default Sources ---
    DEFAULT_URLS = [
        "https://lilianweng.github.io/posts/2023-06-23-agent/",
        "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/"
    ]
    
    @classmethod
    def get_llm(cls):
        """Initialize and return the Groq LLM model"""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file."
            )
        
        # init_chat_model handles the provider mapping automatically
        # Requires: pip install langchain-groq
        return init_chat_model(
            model=cls.LLM_MODEL,
            model_provider="groq",
            api_key=cls.GROQ_API_KEY,
            temperature=0,  # Zero is best for factual RAG and Tool Calling
            max_tokens=1024
        )