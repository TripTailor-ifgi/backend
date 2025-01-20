from flask import Blueprint, request, jsonify
from app.models import fetch_pois_flexible

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route('/api/pois', methods=['POST'])
def fetch_pois():
    if request.method == 'POST':
        data = request.get_json()

        # Extract necessary fields from the request JSON
        start_location = data["options"]["startLocation"]["coords"]
        buffer_distance = int(data["options"]["range"]) * 1000  # Convert km to meters
        locations = data["locations"]
        filters = {
            "barrierFree": data["options"].get("barrierFree", False),
            "vegan": data["options"].get("vegan", False),
        }
        date = data["options"]["date"]

        try:
            # Call function with extracted values
            all_results, closest_results = fetch_pois_flexible(
                start_location['lon'],
                start_location['lat'],
                buffer_distance,
                locations,
                filters,
                date
            )

            return jsonify({
                "all_results": all_results,
                "closest_results": closest_results
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500