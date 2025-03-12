import os
import json
import logging
import random
from typing import Optional, Dict, List, Any

import requests
from geopy.geocoders import Nominatim
from requests.exceptions import RequestException, Timeout

from config import (
    API_KEYS,
    WEATHER_API_URL,
    TASKS_DIR,
    REQUEST_TIMEOUT,
    VALID_TEMP_RANGE
)

logger = logging.getLogger(__name__)

# Initialize geocoder with more specific user-agent
geolocator = Nominatim(user_agent="weather_data_processing_app")


def fetch_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch weather data for a given city from the weather API.

    Args:
        city: City name to get weather data for

    Returns:
        Dictionary with weather data or None if request failed
    """
    if not API_KEYS:
        logger.error("No API keys configured")
        return None

    api_key = random.choice(API_KEYS)
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(
            WEATHER_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        data = response.json()

        if "main" not in data:
            logger.error(f"Unexpected API response format for {city}: {data}")
            return None

        temperature = data["main"].get("temp")
        if temperature is None or not (VALID_TEMP_RANGE[0] <= temperature <= VALID_TEMP_RANGE[1]):
            logger.warning(f"Invalid temperature for {city}: {temperature}")
            return None

        return {
            "city": city,
            "temperature": temperature,
            "description": data["weather"][0]["description"],
            "humidity": data["main"].get("humidity"),
            "wind_speed": data.get("wind", {}).get("speed")
        }
    except Timeout:
        logger.error(f"Request timeout for {city}")
        return None
    except RequestException as e:
        logger.error(f"Request failed for {city}: {e}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Error parsing data for {city}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {city}: {e}")
        return None


def get_region(city: str) -> str:
    """
    Determine geographic region for a city.

    Args:
        city: City name

    Returns:
        Region name (Europe, Asia, America, etc.) or "Unknown"
    """
    try:
        location = geolocator.geocode(city, timeout=REQUEST_TIMEOUT)
        if location:
            display_name = location.raw.get("display_name", "")

            # Check for continents in the display name
            if "Europe" in display_name:
                return "Europe"
            if any(region in display_name for region in ["Asia", "Middle East"]):
                return "Asia"
            if any(region in display_name for region in
                   ["North America", "South America", "America"]):
                return "America"
            if "Africa" in display_name:
                return "Africa"
            if any(region in display_name for region in ["Australia", "Oceania"]):
                return "Oceania"
    except Exception as e:
        logger.warning(f"Error getting region for {city}: {e}")

    return "Unknown"


def save_results(task_id: str, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Save weather results to files organized by region.

    Args:
        task_id: ID of the current task
        data: List of weather data dictionaries

    Returns:
        Dictionary mapping regions to their respective weather data
    """
    if not data:
        logger.warning(f"No data to save for task {task_id}")
        return {}

    os.makedirs(TASKS_DIR, exist_ok=True)

    # Group data by region
    region_data = {}
    for entry in data:
        if not entry or "city" not in entry:
            continue

        region = get_region(entry["city"])
        region_data.setdefault(region, []).append(entry)

    # Save each region's data to a separate file
    for region, cities in region_data.items():
        region_path = os.path.join(TASKS_DIR, region)
        os.makedirs(region_path, exist_ok=True)
        file_path = os.path.join(region_path, f"task_{task_id}.json")

        try:
            with open(file_path, "w") as f:
                json.dump(cities, f, indent=2)
        except (IOError, OSError) as e:
            logger.error(f"Error saving results for {region}: {e}")

    return region_data
