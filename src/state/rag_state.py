"""RAG state definition for LangGraph"""

from typing import List, Annotated, Sequence
from pydantic import BaseModel, ConfigDict
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

class RAGState(BaseModel):
    """
    State object for RAG workflow.
    Using ConfigDict to allow LangChain's Document type.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    question: str
    # If you use LangGraph's MessagesState later, 
    # you might want to store the conversation here:
    # messages: Annotated[Sequence[BaseMessage], operator.add] = []
    
    retrieved_docs: List[Document] = []
    answer: str = ""