import requests
import logging
from utils import normalize_city_name, get_region
from config import API_KEYS

# Using multiple API keys to balance requests
api_key_index = 0

def get_weather_data(city):
    """Gets weather for a city with API key balancing"""
    global api_key_index
    city = normalize_city_name(city)
    region = get_region(city)

    if region == "Unknown":
        logging.warning(f"The region of city {city} is not defined.")
        return None

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEYS[api_key_index], "units": "metric"}

    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Switch API key on next request
        api_key_index = (api_key_index + 1) % len(API_KEYS)

        # Filtering data
        temperature = data.get("main", {}).get("temp")
        if temperature is None or not (-50 <= temperature <= 50):
            logging.warning(f"Temperature in city {city} is invalid: {temperature}")
            return None

        return {
            "city": city,
            "region": region,
            "temperature": temperature,
            "description": data["weather"][0]["description"]
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Error while requesting weather for {city}: {e}")
        return None
