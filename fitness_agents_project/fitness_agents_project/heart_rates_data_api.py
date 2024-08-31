from flask import Blueprint, request, jsonify
import logging

# Create a blueprint for the heart rates data API.
heart_rates_data_bp = Blueprint('heart_rates_data_api', __name__)
# Temporary storage for heart rates data
heart_rates_data_storage = []

# POST request to receive heart rates data
@heart_rates_data_bp.route('/', methods=["POST"])
def receive_heart_rates_data():
    try:
        data = request.json
        logging.info(f"Received heart rates data: {data}")
        heart_rates_data_storage.append(data)
        return jsonify({"message": "Heart rates data received successfully"}), 201
    except Exception as e:
        logging.error(f"Error occurred while receiving heart rates data: {str(e)}")
        return jsonify({"error": str(e)}), 500

# GET request to retrieve heart rates data
@heart_rates_data_bp.route('/', methods=["GET"])
def get_heart_rates_data():
    try:
        if not heart_rates_data_storage:
            return jsonify({"message": "No heart rates data available"}), 404
        return jsonify(heart_rates_data_storage), 200
    except Exception as e:
        logging.error(f"Error occurred while retrieving heart rates data: {str(e)}")
        return jsonify({"error": str(e)}), 500
