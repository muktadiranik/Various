"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Knowledge Base"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///data/documents.db"
    
    # Embeddings - using a lightweight, open-source model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector Store
    VECTOR_STORE_PATH: str = "data/vector_store"
    
    # Document chunking settings
    CHUNK_SIZE: int = 500  # Characters per chunk
    CHUNK_OVERLAP: int = 50  # Overlap between chunks for context preservation

    # Embeddings device
    EMBEDDING_DEVICE: str = "gpu"

    # Groq API Settings
    GROQ_API_KEY: Optional[str] = None  
    GROQ_MODEL: str = "mixtral-8x7b-32768"  # Optional: default model
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global settings instance for easy import
settings = Settings()