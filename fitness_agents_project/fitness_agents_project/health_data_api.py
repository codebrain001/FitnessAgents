from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging

# Create a blueprint for the health data API.
health_data_bp = Blueprint('health_data_api', __name__)
# Initialize SQLAlchemy without configuration
db = SQLAlchemy()

# Defining the database model for the health data table
class HealthDataTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    qty = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(255))
    units = db.Column(db.String(50))

# POST request to receive health data
@health_data_bp.route('/', methods=['POST'])
def receive_health_data():
    try:
        data = request.get_json(force=True)
        logging.info(f"Received health data: {data}")

        if isinstance(data, dict):
            data = [data]

        for item in data:
            metrics = item.get("data", {}).get("metrics", [])
            for metric in metrics:
                name = metric.get("name")
                units = metric.get("units")
                for entry in metric.get("data", []):
                    date = entry.get("date")
                    qty = entry.get("qty")
                    source = entry.get("source")

                    # Skip the record if qty is None
                    if qty is None:
                        continue

                    # Create a new HealthDataTable object and add it to the database
                    health_data = HealthDataTable(
                        name=name,
                        date=date,
                        qty=qty,
                        source=source,
                        units=units
                    )
                    db.session.add(health_data)

        db.session.commit()
        return jsonify({"message": "Data received successfully"}), 201

    except Exception as e:
        logging.error(f"Error occurred while receiving health data: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET request to retrieve health data
@health_data_bp.route('/', methods=['GET'])
def get_health_data():
    try:
        all_data = HealthDataTable.query.all()
        results = [
            {
                "name": data.name,
                "date": data.date,
                "qty": data.qty,
                "source": data.source,
                "units": data.units
            } for data in all_data]

        return jsonify(results), 200
    except Exception as e:
        logging.error(f"Error occurred while retrieving health data: {str(e)}")
        return jsonify({"error": str(e)}), 500
