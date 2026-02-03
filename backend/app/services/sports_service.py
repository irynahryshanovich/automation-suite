from datetime import datetime
import random

import requests
from requests import RequestException

from app.config import settings
from app.database import add_log

def build_mock_sports_data():
    teams = ["Lakers", "Celtics", "Bulls", "Warriors", "Heat", "Bucks", "Nets", "Suns"]
    home_team = random.choice(teams)
    away_team = random.choice([team for team in teams if team != home_team])
    home_score = random.randint(70, 120)
    away_score = random.randint(70, 120)

    return {
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

def fetch_sports_data():
    """
    Fetch sports data from an API
    Returns mock data if API key is not set
    """
    api_key = settings.SPORTS_API_KEY

    if api_key == "demo_key":
        return build_mock_sports_data()

    try:
        url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventslast.php?id=133602"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if "events" in data and data["events"]:
            return data

        if "results" in data and data["results"]:
            return {"events": data["results"]}

        error_data = {"error": "Empty sports data response", "message": "Falling back to mock data"}
        add_log("error", error_data)
        return build_mock_sports_data()
    except RequestException as error:
        error_data = {"error": str(error), "message": "Failed to fetch sports data"}
        add_log("error", error_data)
        return build_mock_sports_data()
