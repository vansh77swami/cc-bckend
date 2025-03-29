from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Basic settings
    PROJECT_NAME: str = "Image Processing API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Replace with your frontend URL
    API_KEY: str = ""  # Set this in production
    
    # Database
    SQLITE_DB: str = "data/image_processing.db"
    
    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: set = {"image/jpeg", "image/png", "image/gif"}
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_DB}"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 