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
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de la configuración.
    """
    env_path = Path(__file__).parent.parent.parent / '.env'
    logger.debug(f"Buscando archivo .env en: {env_path}")
    logger.debug(f"Archivo .env existe: {env_path.exists()}")
    
    if env_path.exists():
        logger.debug("Contenido del archivo .env:")
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key = line.split('=')[0]
                    logger.debug(f"Variable encontrada: {key}")
    
    settings = Settings()
    logger.debug(f"GitHub Token configurado: {'Sí' if settings.GITHUB_TOKEN else 'No'}")
    logger.debug(f"Longitud del GitHub Token: {len(settings.GITHUB_TOKEN) if settings.GITHUB_TOKEN else 0}")
    return settings

settings = get_settings() 