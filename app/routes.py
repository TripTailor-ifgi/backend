from flask import Blueprint, request, jsonify
from app.models import fetch_pois_within_buffer

# Define the blueprint
api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/api/pois", methods=["GET"])
def get_pois_within_buffer():
    """
    API endpoint to fetch amenities within a buffer.
    """
    try:
        # Extract query parameters
        longitude = float(request.args.get("longitude"))
        latitude = float(request.args.get("latitude"))
        buffer_distance = float(request.args.get("buffer_distance", 2000))  # Default: 2000 meters

        # Validate required parameters
        if not longitude or not latitude:
            return jsonify({"error": "Longitude and latitude are required"}), 400

        # Fetch data from the database
        data = fetch_pois_within_buffer(longitude, latitude, buffer_distance)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500