import json
from flask import Blueprint, request, jsonify
from app.models import fetch_pois_flexible
from flask_cors import CORS

api_blueprint = Blueprint("api", __name__)
CORS(api_blueprint)

@api_blueprint.route('/api/pois', methods=['POST'])
def fetch_pois():
    try:
        data = request.get_json()

        # Extracting options
        options = data.get("options", {})
        start_location = options.get("startLocation", {}).get("coords", {})
        buffer_distance = int(options.get("range", 0)) * 1000  # Convert km to meters
        barrier_free = options.get("barrierFree", False)
        vegan = options.get("vegan", False)
        date = options.get("date", None)

        if not start_location or not date:
            return jsonify({"error": "Missing required location or date information."}), 400

        # Extracting location preferences
        locations = data.get("locations", [])
        if not locations:
            return jsonify({"error": "Locations array is required."}), 400

        # Building filter options
        filters = {
            "BarrierFree": barrier_free,
            "Vegan": vegan,
        }

        # Call processing function
        all_results, closest_results = fetch_pois_flexible(
            start_location.get('lon'),
            start_location.get('lat'),
            buffer_distance,
            locations,
            filters,
            date
        )

        return jsonify({
            "all_results": all_results,
            "closest_results": closest_results
        })

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
    except KeyError as e:
        return jsonify({"error": f"Missing key in request: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500