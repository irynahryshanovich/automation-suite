import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Automation Suite"

    # Go up two levels from current 'app' directory
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Define the path to the database folder and file
    DB_DIR = os.path.join(PROJECT_ROOT, "database")
    DB_PATH = os.path.join(DB_DIR, "automation.db")

    # Ensure the directory exists
    os.makedirs(DB_DIR, exist_ok=True)

    # Create the SQLite connection URL
    DATABASE_URL = f"sqlite:///{DB_PATH}"

    print(f"Database URL: {DATABASE_URL}")

    # API keys
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "demo_key")
    SPORTS_API_KEY: str = os.getenv("SPORTS_API_KEY", "demo_key")

    # Automation settings
    AUTOMATION_CADENCE: int = 30  # minutes
    DEFAULT_CITY: str = "Seattle"

    # Social targets
    SOCIAL_TARGETS: list = ["Twitter", "Facebook", "Instagram"]

    class Config:
        env_file = ".env"

settings = Settings()
