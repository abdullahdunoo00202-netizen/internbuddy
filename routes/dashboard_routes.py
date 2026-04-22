from flask import Blueprint, jsonify, request
from extensions import mongo
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity


dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/student-dashboard", methods=["GET"])
@jwt_required()
def student_dashboard():
    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] != "student":
        return jsonify({"error": "Access denied"}), 403

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    return jsonify({
        "message": "Welcome to Student Dashboard",
        "name": user["name"]
    }), 200


@dashboard_bp.route("/manager-dashboard", methods=["GET"])
@jwt_required()
def manager_dashboard():
    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] != "manager":
        return jsonify({"error": "Access denied"}), 403

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    return jsonify({
        "message": "Welcome to Manager Dashboard",
        "name": user["name"]
    }), 200
