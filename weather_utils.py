import os
import json
import requests
import random
import logging
from geopy.geocoders import Nominatim
from config import API_KEYS, WEATHER_API_URL, TASKS_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

geolocator = Nominatim(user_agent="geoapiExercises")


def fetch_weather(city: str) -> dict:
    api_key = random.choice(API_KEYS)
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            logger.error(f"API error for {city}: {data}")
            return None

        temperature = data["main"].get("temp")
        if temperature is None or not (-50 <= temperature <= 50):
            logger.warning(f"Invalid temperature for {city}: {temperature}")
            return None

        return {
            "city": city,
            "temperature": temperature,
            "description": data["weather"][0]["description"]
        }
    except requests.RequestException as e:
        logger.error(f"Request failed for {city}: {e}")
        return None


def get_region(city: str) -> str:
    try:
        location = geolocator.geocode(city)
        if location:
            display_name = location.raw.get("display_name", "")
            if "Europe" in display_name:
                return "Europe"
            if "Asia" in display_name:
                return "Asia"
            if "America" in display_name:
                return "America"
    except Exception:
        pass
    return "Unknown"


def save_results(task_id: str, data: list) -> dict:
    os.makedirs(TASKS_DIR, exist_ok=True)

    region_data = {}
    for entry in data:
        region = get_region(entry["city"])
        region_data.setdefault(region, []).append(entry)

    for region, cities in region_data.items():
        region_path = os.path.join(TASKS_DIR, region)
        os.makedirs(region_path, exist_ok=True)
        file_path = os.path.join(region_path, f"task_{task_id}.json")

        with open(file_path, "w") as f:
            json.dump(cities, f, indent=2)

    return region_data
