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

    # API keys and NOAA contact info,SPORTS_API_KEY='123'
    WEATHER_API_KEY: list = os.getenv("WEATHER_API_KEY", ["Automation Suite", "contact@example.com"])
    SPORTS_API_KEY: str = os.getenv("SPORTS_API_KEY", "demo_key")

    # Automation settings
    AUTOMATION_CADENCE: int = 30  # minutes
    DEFAULT_CITY: str = "Seattle"

    # City coordinates mapping (latitude, longitude)
    CITY_COORDINATES: dict = {
        "Seattle": (47.6062, -122.3321),
        "New York": (40.7128, -74.0060),
        "Los Angeles": (34.0522, -118.2437),
        "Chicago": (41.8781, -87.6298),
        "Houston": (29.7604, -95.3698),
        "Phoenix": (33.4484, -112.0740),
        "Miami": (25.7617, -80.1918),
        "Denver": (39.7392, -104.9903),
        "Boston": (42.3601, -71.0589),
        "San Francisco": (37.7749, -122.4194)
    }

    # Available US cities for weather selection (derived from CITY_COORDINATES keys)
    @property
    def AVAILABLE_CITIES(self) -> list:
        return list(self.CITY_COORDINATES.keys())

    # Social targets
    SOCIAL_TARGETS: list = ["Twitter", "Facebook", "Instagram"]

    class Config:
        env_file = ".env"

settings = Settings()
