from celery import Celery
from city_utils import normalize_city_name
from weather_utils import fetch_weather, save_results
from config import REDIS_URL

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(bind=True)
def process_weather_task(self, cities):
    self.update_state(state="RUNNING")

    cleaned_cities = [normalize_city_name(city) for city in cities if city]
    results = [fetch_weather(city) for city in cleaned_cities if city]
    save_results(self.request.id, [r for r in results if r])

    return {"status": "completed", "task_id": self.request.id}
