import json
import logging
from flask import Blueprint, request, jsonify
from app.models import fetch_pois_flexible
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

api_blueprint = Blueprint("api", __name__)
CORS(api_blueprint)

@api_blueprint.route('/api/pois', methods=['POST'])
def fetch_pois():
    try:
        logging.info("Received a request at /api/pois")

        # Log the raw request data for debugging
        raw_data = request.get_data(as_text=True)
        logging.debug(f"Raw request data: {raw_data}")

        # Attempt to parse JSON
        data = request.get_json()

        # Log parsed JSON data
        logging.debug(f"Parsed JSON data: {json.dumps(data, indent=2)}")

        # Extracting options
        options = data.get("options", {})
        start_location = options.get("startLocation", {}).get("coords", {})
        buffer_distance = int(options.get("range", 0)) * 1000  # Convert km to meters
        barrier_free = options.get("barrierFree", False)
        vegan = options.get("vegan", False)
        date = options.get("date", None)

        if not start_location or not date:
            logging.warning("Missing required location or date information.")
            return jsonify({"error": "Missing required location or date information."}), 400

        # Extracting location preferences
        locations = data.get("locations", [])
        if not locations:
            logging.warning("Locations array is required.")
            return jsonify({"error": "Locations array is required."}), 400

        # Building filter options
        filters = {
            "BarrierFree": barrier_free,
            "Vegan": vegan,
        }

        # Log filters and locations
        logging.info(f"Filters applied: {filters}")
        logging.info(f"Processing locations: {locations}")

        # Call processing function
        all_results, closest_results = fetch_pois_flexible(
            start_location.get('lon'),
            start_location.get('lat'),
            buffer_distance,
            locations,
            filters,
            date
        )

        logging.info("Successfully processed the request.")
        return jsonify({
            "all_results": all_results,
            "closest_results": closest_results
        })

    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error: {str(e)}")
        return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
    except KeyError as e:
        logging.error(f"Missing key in request: {str(e)}")
        return jsonify({"error": f"Missing key in request: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")
        return jsonify({"error": str(e)}), 500