from fuzzywuzzy import process

KNOWN_CITIES = ["Kyiv", "London", "New York", "Tokyo", "Paris", "Berlin"]


def normalize_city_name(city: str) -> str:
    match, score = process.extractOne(city, KNOWN_CITIES)
    return match if score > 80 else city
