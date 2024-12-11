from flask import Blueprint, request, jsonify
from app.models import fetch_museums_by_city

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/api/museums", methods=["GET"])
def get_museums():
    try:
        data = fetch_museums_by_city()  # No city parameter needed
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500