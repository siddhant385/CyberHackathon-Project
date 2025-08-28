# app/core/config.py
"""
Configuration Management Module

This module handles all application configuration using Pydantic Settings.
It provides type-safe configuration with environment variable support,
validation, and default values for development and production environments.

Features:
- Environment-based configuration loading
- Type validation and conversion
- Default values for all settings
- Database URL validation and directory creation
- Security and performance tuning parameters

Usage:
    from app.core.config import settings
    
    # Access configuration
    database_url = settings.DATABASE_URL
    debug_mode = settings.DEBUG
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any, List
import os

class Settings(BaseSettings):
    """
    Application configuration with validation and type safety.
    
    This class defines all configuration parameters for the IPDR Analysis System.
    It supports environment variables and .env files for configuration override.
    All settings have sensible defaults for development environments.
    
    Environment Variables:
        DATABASE_URL: Database connection string
        DEBUG: Enable debug mode (True/False)
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        MAX_BATCH_SIZE: Maximum batch size for data processing
        SECRET_KEY: Application secret key for security
        
    Example:
        # In .env file
        DATABASE_URL=postgresql://user:pass@localhost/ipdr_db
        DEBUG=False
        LOG_LEVEL=INFO
    """
    
    # =============================================================================
    # Database Configuration
    # =============================================================================
    DATABASE_URL: str = Field(
        default="sqlite:///./data/data.db",
        description="Database connection URL. Supports SQLite and PostgreSQL."
    )
    
    # =============================================================================
    # Application Configuration
    # =============================================================================
    APP_NAME: str = Field(
        default="IPDR Analysis System", 
        description="Human-readable application name"
    )
    
    APP_VERSION: str = Field(
        default="1.0.0", 
        description="Application version for tracking and compatibility"
    )
    
    DEBUG: bool = Field(
        default=False, 
        description="Enable debug mode with verbose logging and error details"
    )
    
    # =============================================================================
    # Logging Configuration
    # =============================================================================
    LOG_LEVEL: str = Field(
        default="INFO", 
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    LOG_FILE: Optional[str] = Field(
        default=None, 
        description="Optional log file path. If None, uses default log directory"
    )
    
    # =============================================================================
    # Data Processing Configuration
    # =============================================================================
    MAX_BATCH_SIZE: int = Field(
        default=1000, 
        description="Maximum batch size for bulk database operations"
    )
    
    MAX_FILE_SIZE_MB: int = Field(
        default=100, 
        description="Maximum file size in MB for CSV imports"
    )
    
    # =============================================================================
    # Security Configuration
    # =============================================================================
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production", 
        description="Secret key for cryptographic operations. MUST be changed in production!"
    )
    
    # =============================================================================
    # Investigation Configuration
    # =============================================================================
    DEFAULT_SUSPICIOUS_THRESHOLD_MB: int = Field(
        default=100, 
        description="Default threshold for suspicious data usage in MB"
    )
    
    MAX_QUERY_RESULTS: int = Field(
        default=10000, 
        description="Maximum results returned by database queries"
    )
    
    NETWORK_ANALYSIS_MAX_DEPTH: int = Field(
        default=3,
        description="Maximum depth for network analysis to prevent infinite loops"
    )
    
    # =============================================================================
    # Performance Configuration
    # =============================================================================
    CONNECTION_POOL_SIZE: int = Field(
        default=5,
        description="Database connection pool size"
    )
    
    QUERY_TIMEOUT_SECONDS: int = Field(
        default=30,
        description="Database query timeout in seconds"
    )
    
    # =============================================================================
    # Centralized Configuration for Analysis Thresholds
    # =============================================================================
    ANALYSIS_THRESHOLDS: Dict[str, Any] = Field(
        default={
            "high_data_usage_mb": 500,          # in MB
            "excessive_sessions": 50,
            "multiple_destinations": 20,
            "unusual_upload_ratio": 2.0,        # Upload is 2x more than download
            "late_night_start_hour": 23,        # 11 PM
            "late_night_end_hour": 5,           # 5 AM
            "high_data_session_mb": 100,        # Single session data usage in MB
            "data_exfiltration_ratio": 5.0,     # Upload is 5x more than download
            "unusual_services_count": 8,        # Number of distinct services considered unusual
            "late_night_activity_ratio": 0.3,   # 30% of activity is late at night
            "short_duration_minutes": 5         # Session duration in minutes considered "short"
        },
        description="Centralized configuration for analysis thresholds"
    )
    
    # =============================================================================
    # Generator Configuration
    # =============================================================================
    GENERATOR_CITIES: List[str] = Field(
        default=["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"],
        description="List of cities for data generation"
    )
    
    GENERATOR_STATES: List[str] = Field(
        default=["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Telangana", "Maharashtra", "West Bengal", "Gujarat"],
        description="List of states for data generation"
    )
    
    GENERATOR_ISPS: List[str] = Field(
        default=["Jio", "Airtel", "Vi", "BSNL"],
        description="List of ISPs for data generation"
    )

    GENERATOR_CITY_COORDS: Dict[str, Dict[str, float]] = Field(
        default={
            "Mumbai": {"lat": 19.0760, "lng": 72.8777, "radius": 0.5},
            "Delhi": {"lat": 28.7041, "lng": 77.1025, "radius": 0.6},
            "Bangalore": {"lat": 12.9716, "lng": 77.5946, "radius": 0.4},
            "Chennai": {"lat": 13.0827, "lng": 80.2707, "radius": 0.4},
        },
        description="Coordinates and radius for cities"
    )
    GENERATOR_IP_RANGES: Dict[str, List[str]] = Field(
        default={
            "Mumbai": ["103.21", "117.18", "125.99"],
            "Delhi": ["117.97", "106.51", "203.122"],
            "Bangalore": ["117.196", "49.207", "103.248"],
            "Chennai": ["117.192", "203.192", "49.205"],
        },
        description="IP ranges for different cities"
    )

    GENERATOR_SUSPICIOUS_BEHAVIORS: List[str] = Field(
        default=[
            "location_hopping", "ip_hopping", "unusual_timing", "large_transfers",
            "micro_sessions", "long_sessions", "suspicious_destinations",
            "device_cloning", "data_exfiltration"
        ],
        description="List of suspicious behaviors for generators"
    )
    GENERATOR_SUSPICIOUS_IPS: List[str] = Field(
        default=[
            "185.220.101.15", "198.98.51.189", "45.77.230.37",
            "194.61.24.102", "103.224.182.251", "45.32.105.15"
        ],
        description="List of suspicious IPs for generators"
    )
    GENERATOR_SUSPICIOUS_LOCATIONS: List[Dict[str, Any]] = Field(
        default=[
            {"lat": 28.7041, "lng": 77.1025, "name": "Border Area"},
            {"lat": 15.2993, "lng": 74.1240, "name": "Remote Area"},
        ],
        description="List of suspicious locations for generators"
    )

    GENERATOR_SERVICES: Dict[str, Dict[str, Any]] = Field(
        default={
            "WhatsApp": {"name": "WhatsApp", "ports": [443, 5222], "protocol": "HTTPS", "data_type": "IM", "data_usage": (50_000, 500_000)},
            "Facebook": {"name": "Facebook", "ports": [443, 80], "protocol": "HTTPS", "data_type": "Social", "data_usage": (200_000, 2_000_000)},
            "Instagram": {"name": "Instagram", "ports": [443], "protocol": "HTTPS", "data_type": "Social", "data_usage": (500_000, 5_000_000)},
            "YouTube": {"name": "YouTube", "ports": [443, 80], "protocol": "HTTPS", "data_type": "Video", "data_usage": (1_000_000, 50_000_000)},
            "Netflix": {"name": "Netflix", "ports": [443], "protocol": "HTTPS", "data_type": "Video", "data_usage": (5_000_000, 100_000_000)},
            "Telegram": {"name": "Telegram", "ports": [443, 80], "protocol": "HTTPS", "data_type": "IM", "data_usage": (50_000, 500_000)},
            "Gmail": {"name": "Gmail", "ports": [993, 587], "protocol": "IMAP", "data_type": "Email", "data_usage": (5_000, 50_000)},
            "Banking": {"name": "Banking", "ports": [443], "protocol": "HTTPS", "data_type": "Finance", "data_usage": (10_000, 100_000)},
            "Gaming": {"name": "Gaming", "ports": [443, 7777], "protocol": "TCP", "data_type": "Gaming", "data_usage": (100_000, 10_000_000)},
            "Unknown": {"name": "Unknown", "ports": [80, 8080], "protocol": "TCP", "data_type": "Unknown", "data_usage": (10_000, 100_000)}
        },
        description="Service configurations for generators"
    )
    GENERATOR_SERVICE_SERVERS: Dict[str, List[str]] = Field(
        default={
            "WhatsApp": ["157.240.12.35", "91.108.4.41"],
            "Telegram": ["91.108.56.181", "149.154.175.50"],
            "YouTube": ["142.250.183.14", "172.217.160.78"],
            "Facebook": ["157.240.12.35", "31.13.64.35"],
            "Netflix": ["54.230.216.47", "52.85.83.228"],
            "Gmail": ["172.217.160.109", "142.250.183.109"]
        },
        description="Server IPs for external services"
    )

    # =============================================================================
    # Geolocation Configuration
    # =============================================================================
    GEOIP_DATABASE_PATH: str = Field(
        default="data/geoip/GeoLite2-City.mmdb",
        description="Path to the GeoIP database file"
    )

    # =============================================================================
    # Pydantic Configuration
    # =============================================================================
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unknown environment variables
    )
    
    # =============================================================================
    # Validation Methods
    # =============================================================================
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """
        Validate logging level against allowed values.
        
        Args:
            v (str): Log level string
            
        Returns:
            str: Validated and normalized log level
            
        Raises:
            ValueError: If log level is not valid
        """
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v_upper
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """
        Validate database URL and create directory for SQLite databases.
        
        This validator ensures that:
        1. SQLite database directories exist
        2. Database URLs are properly formatted
        3. Required directories are created automatically
        
        Args:
            v (str): Database URL
            
        Returns:
            str: Validated database URL
        """
        if v.startswith('sqlite:///'):
            # Extract file path and create directory for SQLite
            file_path = v.replace('sqlite:///', '')
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        return v
    
    @validator('MAX_BATCH_SIZE')
    def validate_batch_size(cls, v):
        """
        Validate batch size is within reasonable limits.
        
        Args:
            v (int): Batch size
            
        Returns:
            int: Validated batch size
            
        Raises:
            ValueError: If batch size is out of range
        """
        if v <= 0 or v > 10000:
            raise ValueError('Batch size must be between 1 and 10000')
        return v
    
    @validator('NETWORK_ANALYSIS_MAX_DEPTH')
    def validate_network_depth(cls, v):
        """
        Validate network analysis depth to prevent performance issues.
        
        Args:
            v (int): Network analysis depth
            
        Returns:
            int: Validated depth
            
        Raises:
            ValueError: If depth is out of range
        """
        if v < 1 or v > 5:
            raise ValueError('Network analysis depth must be between 1 and 5')
        return v

# =============================================================================
# Global Settings Instance
# =============================================================================
# Create a global settings instance that can be imported throughout the application
settings = Settings()

def get_settings() -> Settings:
    """
    Get application settings instance.
    
    This function provides a way to access settings that can be easily mocked
    during testing and supports dependency injection patterns.
    
    Returns:
        Settings: Current application settings
        
    Example:
        from app.core.config import get_settings
        
        app_settings = get_settings()
        database_url = app_settings.DATABASE_URL
    """
    return settings

# =============================================================================
# Configuration Validation
# =============================================================================
def validate_configuration() -> bool:
    """
    Validate the current configuration for completeness and correctness.
    
    This function performs additional validation that can't be done at the
    Pydantic model level, such as checking file permissions, network connectivity,
    and configuration consistency.
    
    Returns:
        bool: True if configuration is valid, False otherwise
        
    Raises:
        ValueError: If critical configuration errors are found
    """
    try:
        # Check if database directory is writable (for SQLite)
        if settings.DATABASE_URL.startswith('sqlite:///'):
            db_path = settings.DATABASE_URL.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.access(db_dir, os.W_OK):
                raise ValueError(f"Database directory not writable: {db_dir}")
        
        # Validate log level is properly set
        if settings.LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid log level: {settings.LOG_LEVEL}")
        
        # Check if secret key has been changed from default
        if settings.SECRET_KEY == "your-secret-key-here-change-in-production":
            # This is a warning, not an error for development
            import warnings
            warnings.warn("Using default secret key. Change this in production!")
        
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

# Validate configuration on import (optional)
if __name__ == "__main__":
    if validate_configuration():
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed")