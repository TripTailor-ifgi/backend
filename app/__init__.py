from flask import Flask
from flask_cors import CORS
from app.routes import api_blueprint  # Import the blueprint

def create_app():
    """
    Application factory pattern for creating Flask app.
    """
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Register the blueprint
    app.register_blueprint(api_blueprint)

    return app