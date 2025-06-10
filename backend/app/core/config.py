import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI DocGen API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # GitHub
    GITHUB_TOKEN: str
    GITHUB_API_URL: str = "https://api.github.com"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hora
    
    # File Analysis
    MAX_FILE_SIZE: int = 1024 * 1024  # 1MB
    SUPPORTED_LANGUAGES: set = {
        "python", "javascript", "typescript", "java", "go",
        "ruby", "php", "csharp", "cpp", "rust"
    }
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de la configuración.
    """
    return Settings()

settings = get_settings() 