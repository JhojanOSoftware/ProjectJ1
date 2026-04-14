"""
Application Configuration
Environment-based configuration for different deployment stages.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment: development, staging, production
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "jhojan")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "J_Arrendatarios")

# CORS Configuration - Allow multiple origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
    # Default origins if not specified
    ALLOWED_ORIGINS = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

# API Configuration
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_VERSION = "2.0.0"

# Application
APP_NAME = "Actividad Microsite API"
APP_DESCRIPTION = "API for managing tenants and utility billing"

# Files
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")

# Pagination
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
