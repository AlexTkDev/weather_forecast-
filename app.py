import os
import logging
from typing import Dict, Any, List, Union

from flask import Flask, request, jsonify, Response
from celery.result import AsyncResult

from tasks import process_weather_task
from config import TASKS_DIR

app = Flask(__name__)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@app.route("/weather", methods=["POST"])
def start_weather_processing() -> Union[Response, tuple[Response, int]]:
    """
    Start weather data processing for provided cities.

    Expects JSON with "cities" list of city names.

    Returns:
        JSON response with task ID or error message
    """
    try:
        data = request.get_json()

        # Validate input data
        if not data:
            logger.error("No JSON data provided")
            return jsonify({"error": "No data provided"}), 400

        if "cities" not in data:
            logger.error("Missing 'cities' key in request data")
            return jsonify({"error": "Missing 'cities' key"}), 400

        if not isinstance(data["cities"], list):
            logger.error("'cities' is not a list")
            return jsonify({"error": "'cities' must be a list"}), 400

        if not all(isinstance(city, str) for city in data["cities"]):
            logger.error("Not all cities are strings")
            return jsonify({"error": "All cities must be strings"}), 400

        if not data["cities"]:
            logger.error("Empty cities list")
            return jsonify({"error": "Empty cities list"}), 400

        # Start async task
        task = process_weather_task.apply_async(args=[data["cities"]])
        return jsonify({"task_id": task.id}), 202

    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task_status(task_id: str) -> Union[Response, tuple[Response, int]]:
    """
    Get the status of a task by its ID.

    Args:
        task_id: The ID of the task to check

    Returns:
        JSON response with task status
    """
    try:
        task = AsyncResult(task_id)

        if task.state == "PENDING":
            return jsonify({"status": "pending"})
        elif task.state == "RUNNING":
            return jsonify({"status": "running"})
        elif task.state == "SUCCESS":
            regions = task.result.get("regions", [])
            return jsonify({
                "status": "completed",
                "processed_cities": task.result.get("processed_cities", 0),
                "total_cities": task.result.get("total_cities", 0),
                "regions": regions,
                "results_urls": [f"/results/{region}/{task_id}" for region in regions]
            })
        else:
            logger.error(f"Task {task_id} failed: {task.info}")
            return jsonify({
                "status": "failed",
                "error": str(task.info)
            }), 500

    except Exception as e:
        logger.exception(f"Error checking task {task_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/results/<region>", methods=["GET"])
def list_region_results(region: str) -> Union[Response, tuple[Response, int]]:
    """
    List all result files for a specific region.

    Args:
        region: Region name (Europe, Asia, etc.)

    Returns:
        JSON response with list of result files
    """
    region_path = os.path.join(TASKS_DIR, region)

    if not os.path.exists(region_path):
        logger.error(f"Region not found: {region}")
        return jsonify({"error": "Region not found"}), 404

    try:
        files = os.listdir(region_path)
        return jsonify({"files": files})
    except Exception as e:
        logger.exception(f"Error listing files for region {region}: {e}")
        return jsonify({"error": "Error accessing region files"}), 500


@app.route("/results/<region>/<task_id>", methods=["GET"])
def get_task_results(region: str, task_id: str) -> Union[Response, tuple[Response, int]]:
    """
    Get results for a specific task in a specific region.

    Args:
        region: Region name (Europe, Asia, etc.)
        task_id: Task ID

    Returns:
        JSON response with task results
    """
    file_path = os.path.join(TASKS_DIR, region, f"task_{task_id}.json")

    if not os.path.exists(file_path):
        logger.error(f"Results not found: {file_path}")
        return jsonify({"error": "Results not found"}), 404

    try:
        with open(file_path, 'r') as f:
            data = f.read()
        return Response(data, mimetype='application/json')
    except Exception as e:
        logger.exception(f"Error reading results file {file_path}: {e}")
        return jsonify({"error": "Error reading results"}), 500


@app.route("/health")
def health_check() -> Response:
    """Simple health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
