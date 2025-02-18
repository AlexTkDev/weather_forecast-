import os
from flask import Flask, request, jsonify
from celery.result import AsyncResult
from tasks import process_weather_task
from config import TASKS_DIR
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/weather", methods=["POST"])
def start_weather_processing():
    data = request.get_json()
    if not data or "cities" not in data or not isinstance(data["cities"], list) or not all(
            isinstance(city, str) for city in data["cities"]):
        logger.error("Invalid request data: %s", data)
        return jsonify({"error": "Invalid request format"}), 400

    task = process_weather_task.apply_async(args=[data["cities"]])
    return jsonify({"task_id": task.id}), 202


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task_status(task_id):
    task = AsyncResult(task_id)
    if task.state == "PENDING":
        return jsonify({"status": "pending"})
    elif task.state == "RUNNING":
        return jsonify({"status": "running"})
    elif task.state == "SUCCESS":
        return jsonify({"status": "completed", "results": f"/results/task_{task_id}.json"})
    else:
        return jsonify({"status": "failed"}), 500


@app.route("/results/<region>", methods=["GET"])
def get_results(region):
    region_path = os.path.join(TASKS_DIR, region)
    if not os.path.exists(region_path):
        logger.error("Region not found: %s", region)
        return jsonify({"error": "Region not found"}), 404

    files = os.listdir(region_path)
    return jsonify({"files": files})


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(debug=True)
