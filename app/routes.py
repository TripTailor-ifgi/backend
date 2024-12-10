from flask import Blueprint, request, jsonify
from app.models import fetch_museums_by_city

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/api/museums", methods=["GET"])
def get_museums():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    try:
        data = fetch_museums_by_city(city)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
