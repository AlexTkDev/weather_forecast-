from typing import Optional
from fuzzywuzzy import process
from config import CITY_MATCH_THRESHOLD

# Expanded list of known cities
KNOWN_CITIES = [
    "Kyiv", "London", "New York", "Tokyo", "Paris", "Berlin",
    "Moscow", "Beijing", "Sydney", "Cairo", "Rio de Janeiro",
    "Toronto", "Mexico City", "Rome", "Madrid", "Amsterdam"
]


def normalize_city_name(city: str) -> Optional[str]:
    """
    Normalize city name using fuzzy matching against known cities.

    Args:
        city: Input city name that might contain errors

    Returns:
        Normalized city name or None if no match found
    """
    if not city or not isinstance(city, str):
        return None

    city = city.strip()
    if not city:
        return None

    match, score = process.extractOne(city, KNOWN_CITIES)
    return match if score > CITY_MATCH_THRESHOLD else city
