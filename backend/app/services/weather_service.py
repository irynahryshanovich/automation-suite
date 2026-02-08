import random
from datetime import datetime

import requests
from requests import RequestException

from app.config import settings
from app.database import add_log


def convert_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius"""
    return round((fahrenheit - 32) * 5/9, 1)


def convert_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return round((celsius * 9/5) + 32, 1)


def build_mock_weather_data():
    celsius_temp = round(random.uniform(15.0, 35.0), 1)
    fahrenheit_temp = convert_to_fahrenheit(celsius_temp)

    return {
        "main": {
            "temp": celsius_temp,  # Main temp as Celsius
            "temp_c": celsius_temp,  # Explicit Celsius
            "temp_f": fahrenheit_temp,  # Explicit Fahrenheit
        },
        "weather": [
            {
                "main": random.choice(["Clear", "Clouds", "Rain", "Snow"]),
                "description": "Generated mock weather data"
            }
        ],
        "name": settings.DEFAULT_CITY,
        "dt": int(datetime.now().timestamp())
    }


def get_validated_city(city):
    if city and city in settings.CITY_COORDINATES:
        return city
    return settings.DEFAULT_CITY


def fetch_weather_data(city=None):
    """
    Fetch weather data from NOAA's National Weather Service API
    Returns mock data if API request fails
    """
    effective_city = get_validated_city(city)
    coordinates = settings.CITY_COORDINATES[effective_city]
    app_name, contact_email = settings.WEATHER_API_KEY

    try:
        headers = {
            'User-Agent': f'({app_name}, {contact_email})',
            'Accept': 'application/geo+json'
        }

        lat, lon = coordinates

        # Step 1: Get the grid endpoint for the location
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_response = requests.get(points_url, headers=headers, timeout=10)
        points_response.raise_for_status()

        points_data = points_response.json()
        forecast_url = points_data['properties']['forecast']

        # Step 2: Get the actual forecast
        forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()
        current_period = forecast_data['properties']['periods'][0]

        # NOAA provides temperature in Fahrenheit
        fahrenheit_temp = current_period['temperature']
        celsius_temp = convert_to_celsius(fahrenheit_temp)

        return {
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
            "name": effective_city,
            "dt": int(datetime.now().timestamp())
        }
    except RequestException as error:
        error_data = {"error": str(error), "message": "Failed to fetch NOAA weather data"}
        add_log("error", error_data)
        return build_mock_weather_data()
