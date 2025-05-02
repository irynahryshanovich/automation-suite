import requests
import random
from datetime import datetime
from app.config import settings
from app.database import add_log

def fetch_sports_data():
    """
    Fetch sports data from an API
    Returns mock data if API key is not set
    """
    try:
        api_key = settings.SPORTS_API_KEY

        # Use a real API if key is provided
        if api_key != "demo_key":
            url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventslast.php?id=133602"  # NBA events
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        # Generate mock data for demo purposes
        teams = ["Lakers", "Celtics", "Bulls", "Warriors", "Heat", "Bucks", "Nets", "Suns"]
        home_team = random.choice(teams)
        away_team = random.choice([team for team in teams if team != home_team])
        home_score = random.randint(70, 120)
        away_score = random.randint(70, 120)

        sports_data = {
            "events": [
                {
                    "strEvent": f"{home_team} vs {away_team}",
                    "intHomeScore": str(home_score),
                    "intAwayScore": str(away_score),
                    "dateEvent": datetime.now().strftime("%Y-%m-%d"),
                    "strStatus": "Finished",
                    "strHomeTeam": home_team,
                    "strAwayTeam": away_team
                }
            ]
        }
        return sports_data
    except Exception as e:
        error_data = {"error": str(e), "message": "Failed to fetch sports data"}
        add_log("error", error_data)
        return error_data