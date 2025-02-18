import os
API_KEYS = os.getenv('API_KEYS', '').split(',')
REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379/0")
WEATHER_API_URL = "https://api.openweathermap.org/data/3.0/onecall"
TASKS_DIR = "weather_data"