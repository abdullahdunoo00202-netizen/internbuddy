from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.proctor_log import log_violation

proctor_bp = Blueprint("proctor", __name__)

@proctor_bp.route("/proctor/api/log", methods=["POST"])
@jwt_required()
def log_event():
    data = request.json

    log_violation(
        session_id=data.get("session_id"),
        event_type=data.get("event"),
        severity=data.get("severity")
    )

    return jsonify({"message": "Violation logged"})
