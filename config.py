import os
from typing import List

# API configuration
API_KEYS: List[str] = os.getenv('API_KEYS', '').split(',')
if API_KEYS == ['']:
    API_KEYS = []  # Prevent empty string becoming an API key

REDIS_URL: str = os.getenv('REDIS_URL', "redis://localhost:6379/0")
WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"  # Updated to correct endpoint
TASKS_DIR: str = "weather_data"

# Timeout configuration
REQUEST_TIMEOUT: int = 5  # seconds

# Validation parameters
VALID_TEMP_RANGE: tuple = (-50, 50)  # Valid temperature range in Celsius
CITY_MATCH_THRESHOLD: int = 80  # Threshold for fuzzy matching city names