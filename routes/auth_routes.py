from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import mongo, bcrypt
from models.user_model import user_schema
from utils.token import generate_token, verify_token
from utils.email_service import send_email

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ================= REGISTER =================
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 400

    if len(data["password"]) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    hashed_pw = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    user = user_schema(
        data["name"],
        data["email"],
        hashed_pw,
        data["role"]
    )

    mongo.db.users.insert_one(user)

    token = generate_token(data["email"])
    link = f"http://127.0.0.1:5000/api/auth/verify/{token}"

    send_email(
        "Verify your InternBuddy account",
        data["email"],
        f"Click to verify your account:\n{link}"
    )

    return jsonify({"message": "Registered successfully! Check email."}), 201


# ================= VERIFY =================
@auth_bp.route("/verify/<token>")
def verify_email(token):
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid token"}), 400

    mongo.db.users.update_one(
        {"email": email},
        {"$set": {"is_verified": True}}
    )

    return jsonify({"message": "Email verified. You can login."}), 200


# ================= LOGIN =================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user = mongo.db.users.find_one({"email": data["email"]})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.get("is_verified"):
        return jsonify({"error": "Verify email first"}), 401

    if not bcrypt.check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid password"}), 401

    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={"role": user["role"]}
    )

    return jsonify({
        "access_token": token,
        "user_id": str(user["_id"]),   # 🔥 MUST ADD
        "role": user["role"]
    }), 200


# ================= FORGOT PASSWORD =================
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True)
    email = data.get("email")

    if not mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "User not found"}), 404

    token = generate_token(email)
    link = f"http://127.0.0.1:5000/reset-password-page/{token}"

    send_email(
        "Reset Password",
        email,
        f"Reset link:\n{link}"
    )

    return jsonify({"message": "Reset link sent"}), 200


# ================= RESET PASSWORD =================
@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    data = request.get_json(silent=True)
    password = data.get("password")

    if not password or len(password) < 8:
        return jsonify({"error": "Invalid password"}), 400

    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid token"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    mongo.db.users.update_one(
        {"email": email},
        {"$set": {"password": hashed_pw}}
    )

    return jsonify({"message": "Password reset successful"}), 200
