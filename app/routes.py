from flask import Blueprint, request, jsonify
from app.models import fetch_pois_flexible
from app.utils import get_categories_and_options

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route('/api/pois', methods=['GET', 'POST'])
def fetch_pois():
    if request.method == 'POST':
        # Handle POST request
        data = request.get_json()  # Parse JSON payload
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        buffer_distance = data.get('buffer_distance')
        filters = data.get('filters')

        try:
            # Call the unified fetch_pois_flexible function
            results = fetch_pois_flexible(longitude, latitude, buffer_distance, filters)
            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Method Not Allowed"}), 405


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