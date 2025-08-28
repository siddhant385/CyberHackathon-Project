# app/core/config.py
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application configuration with validation and type safety.
    Supports environment variables and .env files.
    """
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./data/data.db",
        description="Database connection URL"
    )
    
    # Application Configuration
    APP_NAME: str = Field(default="IPDR Analysis System", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    
    # Data Processing Configuration
    MAX_BATCH_SIZE: int = Field(default=1000, description="Maximum batch size for data processing")
    MAX_FILE_SIZE_MB: int = Field(default=100, description="Maximum file size in MB")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="your-secret-key-here", description="Secret key for security")
    
    # Investigation Configuration
    DEFAULT_SUSPICIOUS_THRESHOLD_MB: int = Field(default=100, description="Default threshold for suspicious data usage in MB")
    MAX_QUERY_RESULTS: int = Field(default=10000, description="Maximum results returned by queries")
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validate database URL and create directory for SQLite"""
        if v.startswith('sqlite:///'):
            # Extract file path and create directory
            file_path = v.replace('sqlite:///', '')
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        return v
    
    @validator('MAX_BATCH_SIZE')
    def validate_batch_size(cls, v):
        """Validate batch size"""
        if v <= 0 or v > 10000:
            raise ValueError('Batch size must be between 1 and 10000')
        return v

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings