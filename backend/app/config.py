import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillPath AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/skillpath.db")
    
    # Synthetic generator
    RANDOM_SEED: int = int(os.getenv("RANDOM_SEED", 20261022))
    DATASET_MODE: str = os.getenv("DATASET_MODE", "STARTER")  # STARTER or FULL
    
    # Server
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
