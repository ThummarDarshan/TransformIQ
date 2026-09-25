import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env") if (BASE_DIR / ".env").exists() else ".env",
        extra="allow"
    )

    PROJECT_NAME: str = "TransformIQ — Business Transformation AI Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./transformiq.db"
    DEBUG: bool = True
    
    # JWT Auth & Security
    SECRET_KEY: str = "transformiq-super-secret-jwt-key-for-chaos2commit-2026-production"
    JWT_SECRET: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    def model_post_init(self, __context):
        if self.JWT_SECRET:
            self.SECRET_KEY = self.JWT_SECRET
    
    # AI Routing & Provider Management
    AI_PROVIDER: str = "auto"  # auto, gemini, groq, openrouter, openai, azure
    AI_PROVIDER_ORDER: str = "gemini,groq,openrouter,openai,azure"
    AI_ROUTING_STRATEGY: str = "health_round_robin"  # health_round_robin, priority_fallback
    AI_MAX_RETRIES: int = 2
    AI_REQUEST_TIMEOUT: int = 60
    AI_COOLDOWN_SECONDS: int = 60
    AI_MAX_MESSAGE_LENGTH: int = 12000
    AI_MAX_OUTPUT_TOKENS: int = 4096
    AI_TEST_FORCE_PROVIDER_ERROR: Optional[str] = None
    
    # 1. Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # 2. Groq (Ultra-fast low-cost inference)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    
    # 3. OpenRouter (Multi-model free tier hub)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    
    # 4. OpenAI (Optional fallback)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    # 5. Azure OpenAI (Optional enterprise fallback)
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Security & CORS
    FRONTEND_URL: Optional[str] = None
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000,https://transformiq.vercel.app"
    CORS_ALLOW_CREDENTIALS: bool = True
    ENABLE_SECURITY_HEADERS: bool = True
    STRICT_TRANSPORT_SECURITY: bool = True
    
    # Storage & Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    MAX_URL_RESPONSE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2 MB limit for SSRF protection
    
    # RAG Configuration
    CHAT_RAG_ENABLED: bool = True
    VECTOR_SEARCH_ENABLED: bool = True
    RAG_TOP_K: int = 4
    RAG_CHUNK_SIZE: int = 600
    RAG_CHUNK_OVERLAP: int = 120
    
    # Chat & Memory
    CHAT_HISTORY_ENABLED: bool = True
    CHAT_AUTO_TITLE_ENABLED: bool = True
    CHAT_PROJECT_CONTEXT_ENABLED: bool = True
    
    # Multilingual
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: str = "en,hi,gu"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    CHAT_RATE_LIMIT_ENABLED: bool = True
    AUTH_RATE_LIMIT_PER_MINUTE: int = 15
    CHAT_RATE_LIMIT_PER_MINUTE: int = 20
    AI_RATE_LIMIT_PER_MINUTE: int = 20
    UPLOAD_RATE_LIMIT_PER_MINUTE: int = 10
    WEBSITE_INGEST_RATE_LIMIT_PER_MINUTE: int = 5
    EXPORT_RATE_LIMIT_PER_MINUTE: int = 10
    ADMIN_RATE_LIMIT_PER_MINUTE: int = 60

settings = Settings()

