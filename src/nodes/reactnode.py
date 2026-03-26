"""LangGraph nodes for RAG workflow + ReAct Agent using Groq-compatible Tool Schemas"""

import uuid
import pydantic
from typing import List, Optional, Any

# Absolute imports for sage project structure
from src.state.rag_state import RAGState 

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool # Updated: Use the @tool decorator
# LangGraph prebuilt agent - 2026 compatibility
from langgraph.prebuilt import create_react_agent

# Wikipedia tool imports
from langchain_community.utilities import WikipediaAPIWrapper

class RAGNodes:
    """Contains node functions for RAG workflow using Groq LLM"""

    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        self._agent = None 

    def retrieve_docs(self, state: RAGState) -> RAGState:
        """Populates state with context chunks from vector store"""
        docs = self.retriever.invoke(state.question)
        state.retrieved_docs = docs
        return state

    def _build_tools(self) -> List[Any]:
        """Builds the toolset with explicit schemas to satisfy Groq validation"""
        
        # 1. Internal Search Tool with EXPLICIT naming
        @tool
        def internal_search(query: str) -> str:
            """Search the internal technical documentation. Use this FIRST for any specific or private info."""
            # Accessing self via closure
            docs: List[Document] = self.retriever.invoke(query)
            if not docs:
                return "No relevant internal documents found."
            
            formatted_docs = []
            for i, d in enumerate(docs[:5], start=1):
                source = d.metadata.get("source", "Unknown Source")
                formatted_docs.append(f"Source [{i}] ({source}):\n{d.page_content}")
            return "\n\n".join(formatted_docs)

        # 2. Wikipedia Tool with EXPLICIT naming
        wiki_wrapper = WikipediaAPIWrapper(top_k_results=3, lang="en")
        
        @tool
        def wikipedia_search(query: str) -> str:
            """Search Wikipedia for general knowledge. Use this ONLY if internal_search has no information."""
            return wiki_wrapper.run(query)

        return [internal_search, wikipedia_search]

    def _init_agent(self):
        """Initializes the agent and ensures namespace safety for Groq/Llama"""
        globals()['uuid'] = uuid
        globals()['pydantic'] = pydantic

        tools = self._build_tools()
        
        # Groq models like Llama 3.1 work best with very clear, structured instructions
        system_msg = (
    "### ROLE\n"
    "You are a helpful assistant replying to casual questions."
    "You are an expert student tutor. Your goal is to provide simple high-signal, "
    "fact-based answers based on retrieved documentation.\n\n"
    
    "### OPERATIONAL RULES\n"
    "1. **Search First**: Always call 'internal_search' to check private docs before answering.\n"
    "2. **Gap Filling**: If internal docs are insufficient, use 'wikipedia_search' for general context.\n"
    "3. **Zero Hallucination**: If the information is not in the search results, state that you don't know.\n\n"
    
    "### OUTPUT FORMAT (CRITICAL)\n"
    "- **Structure**: Start with a 1-sentence summary, explain the answer, followed by a concise explanation.\n"
    "- **Tone**: Technical, objective, and professional. No 'I found' or 'Based on the docs'.\n"
    "- **Formatting**: Use bolding for key terms and bullet points for lists of features or steps.\n"
    
)

        self._agent = create_react_agent(
            self.llm, 
            tools=tools,
            prompt=system_msg
        )

    def generate_answer(self, state: RAGState) -> RAGState:
        """Executes the ReAct loop and updates state"""
        if self._agent is None:
            self._init_agent()

        # Re-using the question from state
        inputs = {"messages": [HumanMessage(content=state.question)]}
        
        try:
            # Groq is fast, so we can comfortably set a high recursion limit
            result = self._agent.invoke(inputs, config={"recursion_limit": 10})
            final_response = result["messages"][-1]
            state.answer = final_response.content
        except Exception as e:
            # Provides clearer debugging for the 400 errors
            state.answer = f"Agent Error: {str(e)}"

        return state