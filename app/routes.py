from flask import Blueprint, request, jsonify
from app.models import fetch_pois_flexible
from app.utils import get_categories_and_options

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/api/pois", methods=["GET"])
def get_pois():
    """
    API endpoint to fetch points of interest dynamically based on filters.
    """
    try:
        longitude = float(request.args.get("longitude"))
        latitude = float(request.args.get("latitude"))
        buffer_distance = float(request.args.get("buffer_distance", 2000))
        filters = request.args.getlist("filters[]")

        if not longitude or not latitude:
            return jsonify({"error": "Longitude and latitude are required"}), 400

        pois = fetch_pois_flexible(longitude, latitude, buffer_distance, filters)
        return jsonify(pois)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route("/api/categories", methods=["GET"])
def get_categories():
    """
    API endpoint to fetch categories and their options from the CSV file.
    """
    try:
        # Load categories and options
        categories = get_categories_and_options()
        return jsonify(categories)  # Send as JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500