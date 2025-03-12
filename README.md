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
- Implements robust error handling and logging
- Includes container health checks for reliable deployment

## System Components

- **Flask API** for handling requests
- **Celery Workers** for background task processing
- **Redis** for task queuing and result storage
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
│── docker-compose.yaml   # Docker Compose configuration
```

## API Endpoints

### `POST /weather`

Submit a list of cities for weather data processing.

- **Request:**
  ```json
  { "cities": ["Kyiv", "New York", "Tokyo", "Londn"] }
  ```
- **Response:**
  ```json
  { "task_id": "12345" }
  ```

### `GET /tasks/<task_id>`

Check the status of a processing task.

- **Response:**
  ```json
  {
    "status": "completed",
    "processed_cities": 3,
    "total_cities": 4,
    "regions": ["Europe", "America", "Asia"],
    "results_urls": [
      "/results/Europe/12345",
      "/results/America/12345",
      "/results/Asia/12345"
    ]
  }
  ```

### `GET /results/<region>`

List all result files for a specific region.

- **Response:**
  ```json
  { "files": ["task_12345.json", "task_67890.json"] }
  ```

### `GET /results/<region>/<task_id>`

Get detailed results for a specific task in a specific region.

- **Response:**
  ```json
  [
    {
      "city": "Kyiv",
      "temperature": 15.2,
      "description": "partly cloudy",
      "humidity": 65,
      "wind_speed": 4.5
    }
  ]
  ```

### `GET /health`

Health check endpoint for monitoring system status.

- **Response:**
  ```json
  { "status": "healthy" }
  ```

## Setup & Deployment

### 1. Install Dependencies

```sh
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file based on `.env.example`:

```
API_KEYS=your_api_key_1,your_api_key_2
REDIS_URL=redis://localhost:6379
```

### 3. Run Redis

```sh
docker-compose up -d redis
```

### 4. Start Flask API

```sh
flask run
```

### 5. Start Celery Worker

```sh
./celery_worker.sh
```

### 6. Run Using Docker Compose

```sh
docker-compose up --build
```

## Configuration

Modify `config.py` for API keys and other settings:

```python
API_KEYS = os.getenv('API_KEYS', '').split(',')
REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379/0")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
TASKS_DIR = "weather_data"
REQUEST_TIMEOUT = 5  # seconds
VALID_TEMP_RANGE = (-50, 50)  # Valid temperature range in Celsius
CITY_MATCH_THRESHOLD = 80  # Threshold for fuzzy matching city names
```

## 🚨 Error Handling

- Comprehensive logging with detailed error messages
- Robust exception handling throughout the application
- Request retries for transient failures
- Input validation at all API endpoints
- Proper error responses with meaningful status codes

## Future Enhancements

- Implement support for multiple weather APIs
- Improve region classification accuracy
- Add a database for historical weather data storage
- Implement rate limiting and API key rotation
- Add user authentication and personalized weather alerts
- Create a web UI for easier interaction with the API