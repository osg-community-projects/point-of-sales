from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pos_system.db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API
    api_title: str = "POS System API"
    api_description: str = "A Point of Sale system API built with FastAPI"
    api_version: str = "1.0.0"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Tax
    default_tax_rate: float = 0.08  # 8%
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create a global settings instance
settings = Settings()
