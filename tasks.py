from celery import Celery
from utils import normalize_city_name, fetch_weather, save_results
from config import REDIS_URL

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(bind=True)
def process_weather_task(self, cities):
    self.update_state(state="RUNNING")

    cleaned_cities = [normalize_city_name(city) for city in cities]
    cleaned_cities = [c for c in cleaned_cities if c]

    results = [fetch_weather(city) for city in cleaned_cities]
    results = [r for r in results if r]

    save_results(self.request.id, results)

    return {"status": "completed", "task_id": self.request.id}
