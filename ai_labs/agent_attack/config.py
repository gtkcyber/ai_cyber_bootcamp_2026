import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./crm.db"

    # Email Configuration
    EMAIL_HOST: str = "imap.gmail.com"
    EMAIL_PORT: int = 993
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # AI Provider Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "openai"  # "openai", "anthropic", or "ollama"
    AI_MODEL: str = "gpt-3.5-turbo"
    OLLAMA_HOST: str = "http://localhost:11434"

    # Difficulty and Security Settings
    DIFFICULTY_LEVEL: str = "medium"  # "easy", "medium", "hard"
    ENABLE_GUARDRAILS: bool = True
    ENABLE_CONTENT_FILTERING: bool = True
    ENABLE_RESPONSE_VALIDATION: bool = True

    # Application Settings
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # Red Team Testing Features
    ENABLE_PROMPT_INJECTION_DETECTION: bool = True
    ENABLE_DATA_EXTRACTION_LOGGING: bool = True
    ENABLE_CONVERSATION_LOGGING: bool = True

    class Config:
        env_file = ".env"

settings = Settings()