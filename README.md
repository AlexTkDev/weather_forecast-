# ⛅️ Weather Data Processing System Documentation

## ⚠️ Overview

This system provides an asynchronous weather data processing API using Flask, Celery, and Redis.
Users submit a list of city names, and the system fetches and processes weather data, classifying
results by geographic regions.

## Features

- Normalizes city names (handling typos and multiple languages)
- Fetches weather data asynchronously
- Validates and filters invalid data
- Stores results in structured files by region
- Provides API endpoints to check task status and retrieve results

## System Components

- **Flask API** for handling requests
- **Celery Workers** for background task processing
- **Redis** for task queuing
- **Weather API** (OpenWeatherMap) for data retrieval

## Project Structure

```
weather_app/
│── app.py                # Main Flask application
│── tasks.py              # Celery tasks
│── city_utils.py         # Utilities for city handling
│── weather_utils.py      # Utilities for weather data handling
│── config.py             # Configuration settings
│── weather_data/         # Storage directory for results
│── requirements.txt      # Project dependencies
│── celery_worker.sh      # Celery worker startup script
│── Dockerfile            # Docker configuration
│── docker-compose.yml    # Docker Compose configuration
```

## API Endpoints

### `POST /weather`

- **Request:**
  ```json
  { "cities": ["Kyiv", "New York", "Tokyo", "Londn"] }
  ```
- **Response:**
  ```json
  { "task_id": "12345" }
  ```

### `GET /tasks/<task_id>`

- **Response:**
  ```json
  { "status": "completed", "results": "link_to_results" }
  ```

### `GET /results/<region>`

- **Response:**
  ```json
  { "files": ["task_12345.json"] }
  ```

## Setup & Deployment

### 1. Install Dependencies

```sh
pip install -r requirements.txt
```

### 2. Run Redis

```sh
docker-compose up -d redis
```

### 3. Start Flask API

```sh
flask run
```

### 4. Start Celery Worker

```sh
./celery_worker.sh
```

### 5. Run Using Docker Compose

```sh
docker-compose up --build
```

## Configuration

Modify `config.py` for API keys and Redis settings:

```python
API_KEYS = os.getenv('API_KEYS', '').split(',')
REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379/0")
WEATHER_API_URL = "https://api.openweathermap.org/data/3.0/onecall"
TASKS_DIR = "weather_data"
```

## 🚨 Error Handling

- Logs errors from external API requests
- Handles missing or incorrect data
- Retries failed requests

## Future Enhancements

- Implement support for multiple weather APIs
- Improve region classification accuracy
- Add a database for historical weather data storage