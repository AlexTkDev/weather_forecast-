from celery import Celery
from typing import List, Dict, Any

from city_utils import normalize_city_name
from weather_utils import fetch_weather, save_results
from config import REDIS_URL

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(bind=True, max_retries=3)
def process_weather_task(self, cities: List[str]) -> Dict[str, Any]:
    """
    Process weather data for a list of cities.

    Args:
        cities: List of city names to process

    Returns:
        Dictionary with task status and ID
    """
    self.update_state(state="RUNNING")

    # Normalize city names
    cleaned_cities = []
    for city in cities:
        normalized = normalize_city_name(city)
        if normalized:
            cleaned_cities.append(normalized)

    # Fetch weather data for each city
    results = []
    for city in cleaned_cities:
        weather_data = fetch_weather(city)
        if weather_data:
            results.append(weather_data)

    # Save results organized by region
    regions = save_results(self.request.id, results)

    return {
        "status": "completed",
        "task_id": self.request.id,
        "processed_cities": len(results),
        "total_cities": len(cities),
        "regions": list(regions.keys())
    }
