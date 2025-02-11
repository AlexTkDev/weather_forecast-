import requests
import logging
from utils import normalize_city_name, get_region
from config import API_KEYS

# Используем несколько API-ключей для балансировки запросов
api_key_index = 0

def get_weather_data(city):
    """Получает погоду для города с балансировкой API-ключей"""
    global api_key_index
    city = normalize_city_name(city)
    region = get_region(city)

    if region == "Unknown":
        logging.warning(f"Регион города {city} не определен.")
        return None

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEYS[api_key_index], "units": "metric"}

    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Переключаем API-ключ при следующем запросе
        api_key_index = (api_key_index + 1) % len(API_KEYS)

        # Фильтруем данные
        temperature = data.get("main", {}).get("temp")
        if temperature is None or not (-50 <= temperature <= 50):
            logging.warning(f"Температура в городе {city} невалидна: {temperature}")
            return None

        return {
            "city": city,
            "region": region,
            "temperature": temperature,
            "description": data["weather"][0]["description"]
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе погоды для {city}: {e}")
        return None
