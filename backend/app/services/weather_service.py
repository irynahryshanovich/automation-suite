import requests
import random
from datetime import datetime
from app.database import add_log


def fetch_weather_data(city=None):
    """
    Fetch weather data from NOAA's National Weather Service API
    Falls back to mock data if API request fails
    """
    # Always use Seattle, ignore any city parameter
    city = "Seattle"

    try:
        # NOAA API doesn't use API keys but requires a user-agent with contact info
        headers = {
            'User-Agent': '(Automation Suite, contact@example.com)',
            'Accept': 'application/geo+json'
        }

        # Hard-coded coordinates for Seattle
        lat = 47.6062
        lon = -122.3321

        # Step 1: Get the grid endpoint for the location
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_response = requests.get(points_url, headers=headers)
        points_response.raise_for_status()

        points_data = points_response.json()
        forecast_url = points_data['properties']['forecast']

        # Step 2: Get the actual forecast
        forecast_response = requests.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()
        current_period = forecast_data['properties']['periods'][0]

        # NOAA provides temperature in Fahrenheit
        fahrenheit_temp = current_period['temperature']
        celsius_temp = convert_to_celsius(fahrenheit_temp)

        # Create a response with both temperature units
        weather_data = {
            "main": {
                "temp": celsius_temp,  # Keep the main temp as Celsius for compatibility
                "temp_c": celsius_temp,  # Explicit Celsius
                "temp_f": fahrenheit_temp,  # Explicit Fahrenheit
            },
            "weather": [
                {
                    "main": current_period['shortForecast'],
                    "description": current_period['detailedForecast']
                }
            ],
            "name": city,
            "dt": int(datetime.now().timestamp())
        }

        return weather_data
    except Exception as e:
        # Log the error and fall back to mock data
        error_data = {"error": str(e), "message": "Failed to fetch NOAA weather data, falling back to mock data"}
        add_log("error", error_data)

        # Generate mock data as fallback
        celsius_temp = round(random.uniform(15.0, 35.0), 1)
        fahrenheit_temp = convert_to_fahrenheit(celsius_temp)

        weather_data = {
            "main": {
                "temp": celsius_temp,  # Main temp as Celsius
                "temp_c": celsius_temp,  # Explicit Celsius
                "temp_f": fahrenheit_temp,  # Explicit Fahrenheit
            },
            "weather": [
                {
                    "main": random.choice(["Clear", "Clouds", "Rain", "Snow"]),
                    "description": "Generated mock weather data (NOAA API failed)"
                }
            ],
            "name": city,
            "dt": int(datetime.now().timestamp())
        }
        return weather_data

def convert_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius"""
    return round((fahrenheit - 32) * 5/9, 1)

def convert_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return round((celsius * 9/5) + 32, 1)
