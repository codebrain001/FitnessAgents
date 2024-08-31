from flask import Blueprint, request, jsonify
import logging

# Create a blueprint for the workout data API.
workout_data_bp = Blueprint('workout_data_api', __name__)
# Temporary storage for workout data
workout_data_storage = []

# POST request to receive workout data
@workout_data_bp.route('/', methods=["POST"])
def receive_workout_data():
    try:
        data = request.json
        print(data)
        logging.info(f"Received workout data: {data}")
        workout_data_storage.append(data)
        return jsonify({"message": "Workout data received successfully"}), 201
    except Exception as e:
        logging.error(f"Error occurred while receiving workout data: {str(e)}")
        return jsonify({"error": str(e)}), 500

# GET request to retrieve workout data
@workout_data_bp.route('/', methods=["GET"])
def get_workout_data():
    try:
        if not workout_data_storage:
            return jsonify({"message": "No workout data available"}), 404
        return jsonify(workout_data_storage), 200
    except Exception as e:
        logging.error(f"Error occurred while retrieving workout data: {str(e)}")
        return jsonify({"error": str(e)}), 500
