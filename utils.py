import os
import json
import requests
import random
import logging
from fuzzywuzzy import process
from geopy.geocoders import Nominatim
from config import API_KEYS, WEATHER_API_URL, TASKS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

geolocator = Nominatim(user_agent="geoapiExercises")

# Исправление ошибок в названии городов
KNOWN_CITIES = ["Kyiv", "London", "New York", "Tokyo", "Paris", "Berlin"]


def normalize_city_name(city):
    match, score = process.extractOne(city, KNOWN_CITIES)
    return match if score > 80 else None


# Получение данных о погоде
def fetch_weather(city):
    api_key = random.choice(API_KEYS)  # Выбираем случайный ключ API
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            logging.error(f"API error for {city}: {data}")
            return None

        temperature = data["main"].get("temp")
        if temperature is None or not (-50 <= temperature <= 50):
            logging.warning(f"Invalid temperature for {city}: {temperature}")
            return None

        return {
            "city": city,
            "temperature": temperature,
            "description": data["weather"][0]["description"]
        }
    except requests.RequestException as e:
        logging.error(f"Request failed for {city}: {e}")
        return None


# Определение региона
def get_region(city):
    try:
        location = geolocator.geocode(city)
        if location:
            if "Europe" in location.raw.get("display_name", ""):
                return "Europe"
            if "Asia" in location.raw.get("display_name", ""):
                return "Asia"
            if "America" in location.raw.get("display_name", ""):
                return "America"
    except BaseException:
        pass
    return "Unknown"


# Сохранение результатов
def save_results(task_id, data):
    os.makedirs(f"{TASKS_DIR}", exist_ok=True)

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
