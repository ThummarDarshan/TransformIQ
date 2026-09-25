from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env") if (BASE_DIR / ".env").exists() else ".env",
        extra="allow"
    )

    PROJECT_NAME: str = "TransformIQ — Business Transformation AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENVIRONMENT: str = "production"
    DATABASE_URL: str = "sqlite+aiosqlite:///./transformiq.db"
    
    # JWT Auth
    SECRET_KEY: str = "transformiq-super-secret-jwt-key-for-chaos2commit-2026-production"
    JWT_SECRET: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    def model_post_init(self, __context):
        if self.JWT_SECRET:
            self.SECRET_KEY = self.JWT_SECRET
    
    # AI Provider settings
    AI_PROVIDER: str = "auto"  # options: auto, gemini, openai, azure_openai, deterministic_smart
    
    # Google Gemini (Free tier with generous quota at https://aistudio.google.com)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    
    # OpenAI Configuration (Optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_BASE: Optional[str] = None
    
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25



settings = Settings()

