"""Application settings and configuration management."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation and environment variable support."""
    
    # Telegram Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(300, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(0.8, env="OPENAI_TEMPERATURE")
    
    # Bot Configuration
    bot_name: str = Field("AI Bot", env="BOT_NAME")
    bot_username: str = Field("@ai_bot", env="BOT_USERNAME")
    bot_description: str = Field("AI-powered Telegram bot", env="BOT_DESCRIPTION")
    
    # Application Configuration
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    environment: str = Field("production", env="ENVIRONMENT")
    
    # Database Configuration (for future use)
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # Web Management Configuration
    web_host: str = Field("0.0.0.0", env="WEB_HOST")
    web_port: int = Field(8080, env="WEB_PORT")
    web_enabled: bool = Field(True, env="WEB_ENABLED")
    
    # Session Configuration
    session_timeout: int = Field(3600, env="SESSION_TIMEOUT")  # 1 hour
    max_conversation_history: int = Field(20, env="MAX_CONVERSATION_HISTORY")
    
    # Assistant API Configuration
    assistant_timeout: int = Field(30, env="ASSISTANT_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

