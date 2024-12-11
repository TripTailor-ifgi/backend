from flask import Flask
from flask_cors import CORS
from app.routes import api_blueprint


def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes
    CORS(app)

    app.register_blueprint(api_blueprint)
    return app
