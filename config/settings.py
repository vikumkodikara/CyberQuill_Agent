"""
CyberQuill Configuration Module
================================

Purpose:
    Loads all configuration from environment variables (.env file) into
    a single, validated Python object. Any module in the project can
    import `settings` and access configuration values.

Why pydantic-settings?
    - Automatically reads from .env files
    - Validates types (e.g., ensures LOG_LEVEL is a string, not a number)
    - Provides defaults so the app doesn't crash if a variable is missing
    - Makes configuration self-documenting via type hints

Inputs:
    - .env file in the project root (or system environment variables)

Outputs:
    - A `settings` object with typed attributes

Dependencies:
    - pydantic-settings

Testing strategy:
    - Test with valid .env file → all fields should populate
    - Test without .env file → defaults should apply
    - Test with invalid values → should raise validation error

Possible improvements:
    - Add per-environment configs (dev, staging, production)
    - Add validation for API key format
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    How it works:
    1. Reads the .env file from the project root
    2. Maps each variable name to a class attribute
    3. Uses the type hint to validate the value
    4. Falls back to the default if the variable is not set
    """

    # ---- API Keys ----
    # These have no defaults — they MUST be provided in .env
    # We use empty string as default so the app starts even without keys,
    # but agents will check and raise clear errors when they try to use them.
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # ---- Model Names ----
    # These have sensible defaults that can be overridden
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_MODEL: str = "meta-llama/llama-4-maverick"

    # ---- ChromaDB ----
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"

    # ---- RSS Feed URLs ----
    # These are hardcoded here because they rarely change.
    # If you need to change them, override via environment variables.
    RSS_FEEDS: list[str] = [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.bleepingcomputer.com/feed/",
        "https://krebsonsecurity.com/feed/",
        "https://www.securityweek.com/feed/",
        "https://www.darkreading.com/rss.xml",
        "https://www.cisa.gov/news.xml",
    ]

    # ---- Article Classification Categories ----
    CATEGORIES: list[str] = [
        "Malware",
        "Data Breach",
        "AI Security",
        "Cloud Security",
        "Zero-Day",
        "Threat Intelligence",
        "Vulnerability Management",
    ]

    # ---- Pydantic Settings Configuration ----
    # This tells pydantic-settings WHERE to find the .env file
    # and how to handle extra variables it doesn't recognize.
    model_config = SettingsConfigDict(
        env_file=".env",            # Look for .env in the current directory
        env_file_encoding="utf-8",  # Read the file as UTF-8
        extra="ignore",             # Ignore any variables not defined above
    )


# Create a single instance that the whole app shares.
# Usage: from config.settings import settings
settings = Settings()
