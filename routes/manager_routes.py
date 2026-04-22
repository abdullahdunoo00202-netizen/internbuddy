from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt
from extensions import mongo
from flask import request
from bson import ObjectId



manager_bp = Blueprint("manager", __name__)

# ======================================================
# 🔹 MANAGER HTML PAGES (❌ NO JWT HERE)
# ======================================================

@manager_bp.route("/manager/dashboard")
def manager_dashboard_page():
    return render_template("manager/manager_dashboard.html")

@manager_bp.route("/manager/registered-students")
def registered_students_page():
    return render_template("manager/registered_students.html")

@manager_bp.route("/manager/applied-students")
def applied_students_page():
    return render_template("manager/applied_students.html")

# ======================================================
# 🔹 MANAGER APIs (✅ JWT REQUIRED HERE)
# ======================================================

@manager_bp.route("/manager/api/registered-students", methods=["GET"])
@jwt_required()
def registered_students_api():

    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    users = mongo.db.users.find({"role": "student"})

    students = []
    for u in users:
        students.append({
            "id": str(u["_id"]),
            "name": u.get("name"),
            "email": u.get("email")
        })

    return jsonify(students), 200


# ======================================================
# 🔹 APPLIED STUDENTS API
# ======================================================

@manager_bp.route("/manager/api/applied-students", methods=["GET"])
@jwt_required()
def applied_students_api():

    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    applications = mongo.db.applications.find()

    data = []
    for app in applications:
        data.append({
            "id": str(app["_id"]),
            "name": app.get("student_name"),
            "email": app.get("email"),
            "cgpa": app.get("education", {}).get("cgpa"),
            "domain": app.get("domain"),
            "resume_match": app.get("resume_match", 0),
            "status": app.get("status"),
            "resume": app.get("resume")
        })

    return jsonify(data), 200


@manager_bp.route("/api/manager/requests", methods=["GET"])
@jwt_required()
def manager_requests_api():
    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    requests = mongo.db.applications.find({"status": "pending"})

    data = []
    for r in requests:
        data.append({
            "id": str(r["_id"]),
            "name": r.get("student_name"),
            "email": r.get("email"),
            "domain": r.get("domain"),
            "resume": r.get("resume"),
            "resume_match": r.get("resume_match", 0)
        })

    return jsonify(data), 200

@manager_bp.route("/api/manager/assigned", methods=["GET"])
@jwt_required()
def manager_assigned_api():
    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    assigned = mongo.db.applications.find({"status": "assigned"})

    data = []
    for a in assigned:
        data.append({
            "name": a.get("student_name"),
            "email": a.get("email"),
            "domain": a.get("domain")
        })

    return jsonify(data), 200

@manager_bp.route("/api/manager/accepted", methods=["GET"])
@jwt_required()
def manager_accepted_api():
    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    accepted = mongo.db.applications.find({"status": "accepted"})

    data = []
    for a in accepted:
        data.append({
            "name": a.get("student_name"),
            "email": a.get("email"),
            "domain": a.get("domain")
        })

    return jsonify(data), 200


@manager_bp.route("/api/manager/stats", methods=["GET"])
@jwt_required()
def manager_stats():
    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    total = mongo.db.applications.count_documents({})
    pending = mongo.db.applications.count_documents({"status": "pending"})
    accepted = mongo.db.applications.count_documents({"status": "accepted"})

    return jsonify({
        "total": total,
        "pending": pending,
        "accepted": accepted
    }), 200


@manager_bp.route("/manager/api/update-status/<app_id>", methods=["POST"])
@jwt_required()
def update_application_status(app_id):

    claims = get_jwt()
    if claims.get("role") != "manager":
        return jsonify({"error": "Unauthorized"}), 403

    new_status = request.json.get("status")

    application = mongo.db.applications.find_one(
        {"_id": ObjectId(app_id)}
    )

    if not application:
        return jsonify({"error": "Application not found"}), 404

    mongo.db.applications.update_one(
        {"_id": ObjectId(app_id)},
        {"$set": {"status": new_status}}
    )

    # 🔥 HARD DEBUG (THIS MUST PRINT)
    print("🚀 UPDATE STATUS HIT")
    print("➡ STATUS:", new_status)
    print("➡ EMAIL:", application.get("email"))

    from utils.email_service import send_application_status_email

    send_application_status_email(
        student_name=application.get("student_name"),
        student_email=application.get("email"),
        internship_domain=application.get("domain"),
        status=new_status
    )

    print("📧 EMAIL FUNCTION CALLED")

    return jsonify({"message": "Status updated & email triggered"}), 200

