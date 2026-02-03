from datetime import datetime
from typing import Dict, Any, List

from app.services.weather_service import fetch_weather_data
from app.services.sports_service import fetch_sports_data
from app.config import settings
from app.database import add_log, update_state, get_states


def perform_automation(city=None, source="automation"):
    """
    Perform the main automation routine:
    1. Fetch weather and sports data
    2. Log the data
    3. Perform actions based on the data
    4. Return the results
    
    Args:
        city: City name for weather data (optional)
        source: Source of the automation trigger ("manual" or "automation")
    """
    effective_city = city or settings.DEFAULT_CITY
    weather_data = fetch_weather_data(effective_city)
    sports_data = fetch_sports_data()

    # Log raw data
    add_log("weather", weather_data)
    add_log("sports", sports_data)

    # Perform actions based on data
    actions = perform_actions(weather_data, sports_data)

    # Log actions
    for action in actions:
        add_log(source, {"message": action}, action)

    return {
        "timestamp": datetime.now().isoformat(),
        "weather": weather_data,
        "sports": sports_data,
        "actions": actions,
        "states": get_states()
    }

def perform_actions(weather_data: Dict[str, Any], sports_data: Dict[str, Any]) -> List[str]:
    """Perform actions based on input data"""
    actions_taken = []

    # Action based on weather temperature - using Fahrenheit
    if "main" in weather_data and "temp_f" in weather_data["main"]:
        temp_f = weather_data["main"]["temp_f"]
        if temp_f > 86:  # 30°C is approximately 86°F
            update_state("Twitter", "paused")
            actions_taken.append(f"Paused Twitter ads due to high temperature ({temp_f}°F)")
        else:
            update_state("Twitter", "active")
            actions_taken.append(f"Activated Twitter ads due to moderate temperature ({temp_f}°F)")

    # Action based on sports scores
    if "events" in sports_data and sports_data["events"]:
        event = sports_data["events"][0]
        # 0 if API returns incomplete/in-progress game data
        home_score = int(event.get("intHomeScore") or 0)
        away_score = int(event.get("intAwayScore") or 0)

        if home_score > away_score:
            update_state("Facebook", "active")
            actions_taken.append(f"Activated Facebook ads - home team won ({home_score}-{away_score})")
        else:
            update_state("Facebook", "paused")
            actions_taken.append(f"Paused Facebook ads - away team won or tied ({away_score}-{home_score})")

    # Time-based action (Instagram)
    current_hour = datetime.now().hour
    if 8 <= current_hour <= 20:  # Between 8 AM and 8 PM
        update_state("Instagram", "active")
        actions_taken.append("Activated Instagram ads during prime hours")
    else:
        update_state("Instagram", "paused")
        actions_taken.append("Paused Instagram ads during off hours")

    return actions_taken
