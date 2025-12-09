from abc import ABC, abstractmethod
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents using Groq (ultra-fast, free!)
    """
    def __init__(self, name, system_prompt=""):
        self.name = name
        self.system_prompt = system_prompt
        
        # Initialize Groq 
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(f"{self.name}: GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",  # Ultra fast, free model
            groq_api_key=api_key,
            temperature=0,  # Zero for maximum speed and determinism
            max_tokens=300,  # Minimal tokens for speed
            timeout=2,  # Ultra short timeout
            max_retries=1  # Single retry only
        )
    
    def _call_llm(self, user_message):
        """
        Internal method to call Groq AI via LangChain
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    @abstractmethod
    def handle_request(self, input_data):
        """
        Process input data and return agent-specific response.
        Must be implemented by subclasses.
        """
        pass
    
    def format_response(self, data):
        """
        Format response in a consistent structure
        """
        return {
            "agent": self.name,
            "response": data
        }
