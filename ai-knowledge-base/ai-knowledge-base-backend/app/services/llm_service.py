"""LLM Service for RAG with Groq"""

import os
import json
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
from enum import Enum

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings
from app.services.knowledge_base import knowledge_base_service

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    OPENAI = "openai"
    OLLAMA = "ollama"


class LLMService:
    # Updated supported models
    GROQ_MODELS = {
        "llama-3.3-70b-versatile": {
            "name": "Llama 3.3 70B",
            "context_window": 32768,
            "description": "Latest and most capable model (recommended)"
        },
        "llama-3.1-70b-versatile": {
            "name": "Llama 3.1 70B",
            "context_window": 32768,
            "description": "Very capable, slightly older than 3.3"
        },
        "llama3-70b-8192": {
            "name": "Llama 3 70B",
            "context_window": 8192,
            "description": "High quality, smaller context window"
        },
        "llama-3.1-8b-instant": {
            "name": "Llama 3.1 8B",
            "context_window": 8192,
            "description": "Fastest responses, good for chat"
        },
        "llama3-8b-8192": {
            "name": "Llama 3 8B",
            "context_window": 8192,
            "description": "Good balance of speed and quality"
        },
        "gemma2-9b-it": {
            "name": "Gemma 2 9B",
            "context_window": 8192,
            "description": "Google's model, good for chat"
        },
    }
    
    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",  # Default model
        temperature: float = 0.7,
        max_tokens: int = 8192,
        top_p: float = 0.95,
    ):
        """
        Initialize the Groq LLM service.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        
        # Get API key from settings
        self.api_key = settings.GROQ_API_KEY
        
        if not self.api_key:
            logger.error("❌ GROQ_API_KEY not found in settings!")
            logger.error("Please set GROQ_API_KEY in your .env file")
            logger.error("Get your API key from: https://console.groq.com")
            raise ValueError("GROQ_API_KEY is required but not set")
        
        # Initialize the LLM
        self.llm = self._initialize_llm()
        
        # Get model info
        model_info = self.GROQ_MODELS.get(model, {})
        logger.info(f"✅ LLM Service initialized with Groq model: {model}")
        logger.info(f"  Model name: {model_info.get('name', 'Unknown')}")
        logger.info(f"  Context window: {model_info.get('context_window', 'Unknown')}")
    
    def _initialize_llm(self):
        """Initialize the Groq LLM"""
        try:
            # Pass API key explicitly
            return ChatGroq(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                api_key=self.api_key,  # Explicitly pass the API key
                # Don't set streaming=True here if you want to control it per call
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq LLM: {e}")
            logger.error(f"API Key provided: {'Yes' if self.api_key else 'No'}")
            if self.api_key:
                logger.error(f"API Key length: {len(self.api_key)}")
                logger.error(f"API Key preview: {self.api_key[:10]}...")
            raise
    
    async def generate_response(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a response with optional context.
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(query, context, system_prompt)
            
            # Generate response
            if stream:
                response = await self.llm.agenerate([messages])
                answer = response.generations[0][0].text
            else:
                response = await self.llm.agenerate([messages])
                answer = response.generations[0][0].text
            
            # Extract sources from context
            sources = []
            if context:
                for item in context:
                    sources.append({
                        "content": item.get("content", ""),
                        "score": item.get("score", 0),
                        "document_id": item.get("document_id", ""),
                    })
            
            return {
                "answer": answer,
                "sources": sources,
                "query": query,
                "model": self.model,
                "provider": "groq",
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate response: {e}")
            raise
    
    async def generate_response_stream(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response.
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(query, context, system_prompt)
            
            # Stream response from Groq
            # Note: The astream method requires the model to be initialized with streaming=True
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"❌ Failed to stream response: {e}")
            yield f"Error: {str(e)}"
    
    def _prepare_messages(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> List:
        """Prepare messages for the LLM"""
        
        default_system_prompt = """You are a knowledgeable AI assistant with access to a knowledge base. 
Your responses should be:
1. Accurate and based ONLY on the provided context
2. Clear, concise, and well-structured
3. Use bullet points and sections for readability
4. If the context doesn't contain the answer, say "I don't have enough information"
5. Always cite your sources

You are using Groq's ultra-fast inference to provide quick, helpful responses."""

        system_prompt = system_prompt or default_system_prompt
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add context if available
        if context:
            context_text = self._format_context(context)
            messages.append(SystemMessage(
                content=f"Relevant information from the knowledge base:\n\n{context_text}\n\nUse this information to answer the user's question."
            ))
        else:
            messages.append(SystemMessage(
                content="No relevant documents were found. Answer based on general knowledge, but be clear about what you know vs. what you're inferring."
            ))
        
        messages.append(HumanMessage(content=query))
        
        return messages
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context for the LLM"""
        formatted_parts = []
        
        for i, item in enumerate(context, 1):
            content = item.get("content", "")
            score = item.get("score", 0)
            
            if len(content) > 2000:
                content = content[:2000] + "..."
            
            part = f"[Source {i}] (relevance: {score:.2f})\n{content}\n"
            formatted_parts.append(part)
        
        return "\n---\n".join(formatted_parts)
    
    def health_check(self) -> Dict[str, Any]:
        """Check LLM service health"""
        model_info = self.GROQ_MODELS.get(self.model, {})
        
        return {
            "provider": "groq",
            "model": self.model,
            "model_name": model_info.get("name", "Unknown"),
            "context_window": model_info.get("context_window", "Unknown"),
            "temperature": self.temperature,
            "status": "healthy" if self.llm and self.api_key else "unhealthy",
            "api_key_set": bool(self.api_key),
            "available_models": list(self.GROQ_MODELS.keys()),
        }
    
    def list_models(self) -> List[Dict[str, str]]:
        """List all available Groq models"""
        return [
            {
                "id": model_id,
                "name": info["name"],
                "context_window": info["context_window"],
                "description": info["description"],
            }
            for model_id, info in self.GROQ_MODELS.items()
        ]


# Create a global instance
# IMPORTANT: This will fail if GROQ_API_KEY is not set in .env
# Create a global instance with a currently supported model
try:
    llm_service = LLMService(
        model="llama-3.3-70b-versatile",  # Latest model
        temperature=0.7,
        max_tokens=8192,
    )
except Exception as e:
    logger.error(f"Failed to create LLM service: {e}")
    llm_service = None