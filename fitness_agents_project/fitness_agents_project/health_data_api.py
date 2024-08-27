from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Initializes the Flask application
app = Flask(__name__)

# Configure the Postgres database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializes the SQLAlchemy extension with the Flask app.
db = SQLAlchemy(app)

# Defining the database model for health data
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    qty = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(255))
    units = db.Column(db.String(50))

# Create the database tables
with app.app_context():
    db.create_all()

# POST request for the Health Auto Export application 
@app.route('/health-data', methods=['POST'])
def receive_health_data():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"error": "Invalid data format. Expected JSON."}), 400

        if isinstance(data, dict):
            data = [data]

        for item in data:
            if not isinstance(item, dict):
                return jsonify({"error": "Each item in the data array must be a dictionary."}), 400

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

                    # Create a new HealthData object and add it to the database
                    health_data = HealthData(
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
        return jsonify({"error": str(e)}), 500

# GET request to get health data
@app.route('/health-data', methods=['GET'])
def get_health_data():
    # Query all health data entries from the database
    all_data = HealthData.query.all()
    results = [
        {
            "name": data.name,
            "date": data.date,
            "qty": data.qty,
            "source": data.source,
            "units": data.units
        } for data in all_data]
    
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True)