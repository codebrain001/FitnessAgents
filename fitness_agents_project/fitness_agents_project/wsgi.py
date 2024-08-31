from flask import Flask
from health_data_api import health_data_bp, db
from heart_rates_data_api import heart_rates_data_bp
from workout_data_api import workout_data_bp
import logging
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Configuration for SQLAlchemy using Heroku's DATABASE_URL
database_uri = os.environ.get('DATABASE_URL')
if database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Register blueprints
app.register_blueprint(health_data_bp, url_prefix='/health-data')
app.register_blueprint(heart_rates_data_bp, url_prefix='/heart-rates-data')
app.register_blueprint(workout_data_bp, url_prefix='/workout-data')

if __name__ == "__main__":
    app.run()
