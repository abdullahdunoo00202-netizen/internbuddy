from flask import Blueprint, request, jsonify, current_app, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
import time
import uuid
import random
import string
from utils.email_service import send_email


from extensions import mongo
from ai.resume_parser import extract_resume_text
from ai.resume_strength import calculate_resume_strength
from utils.email_service import send_assessment_email

application_bp = Blueprint("application", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}




# ==================================
# HELPERS
# ==================================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================================
# APPLY INTERNSHIP
# ==================================
@application_bp.route("/apply", methods=["POST"])
@jwt_required()
def apply_internship():
    data = request.form
    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 403

    internship_id = data.get("internship_id")
    domain = data.get("domain")

    if not internship_id or not domain:
        return jsonify({"error": "Internship ID or domain missing"}), 400

    applied_count = mongo.db.applications.count_documents({
        "student_id": ObjectId(user_id)
    })

    if applied_count >= 2:
        return jsonify({"error": "Max 2 applications allowed"}), 400

    resume = request.files.get("resume")
    profile_pic = request.files.get("profilePicture")

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    resume_filename = None
    profile_pic_filename = None
    resume_match = 0.0

    if resume and resume.filename:
        resume_filename = secure_filename(f"{user_id}_resume_{resume.filename}")
        resume_path = os.path.join(upload_folder, resume_filename)
        resume.save(resume_path)

        resume_text = extract_resume_text(resume_path)
        result = calculate_resume_strength(resume_text)
        resume_match = result["score"]

    if profile_pic and profile_pic.filename:
        profile_pic_filename = secure_filename(f"{user_id}_photo_{profile_pic.filename}")
        profile_pic.save(os.path.join(upload_folder, profile_pic_filename))

    application = {
        "student_id": ObjectId(user_id),
        "internship_id": ObjectId(internship_id),
        "domain": domain,
        "student_name": data.get("fullName"),
        "email": data.get("email"),
        "education": {
            "degree": data.get("degree"),
            "major": data.get("major"),
            "graduation_year": data.get("graduationYear"),
            "cgpa": data.get("cgpa")
        },
        "resume": resume_filename,
        "profile_picture": profile_pic_filename,
        "resume_match": resume_match,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    mongo.db.applications.insert_one(application)

    return jsonify({
        "message": "Application submitted successfully",
        "resume_match": resume_match
    }), 201


# ==================================
# MY APPLICATIONS
# ==================================
@application_bp.route("/api/my-applications", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = get_jwt_identity()

    applications = list(mongo.db.applications.find({
        "student_id": ObjectId(user_id)
    }))

    if not applications:
        return jsonify({"student": {}, "applications": []}), 200

    first_app = applications[0]

    for app in applications:
        app["_id"] = str(app["_id"])
        app["internship_id"] = str(app["internship_id"])
        app["resume_match"] = app.get("resume_match", 0)

    return jsonify({
        "student": {
            "name": first_app.get("student_name"),
            "email": first_app.get("email"),
            "cgpa": first_app.get("education", {}).get("cgpa"),
            "profile_picture": first_app.get("profile_picture")
        },
        "applications": applications
    })


@application_bp.route("/api/select-slot/<application_id>", methods=["POST"])
@jwt_required()
def select_slot(application_id):
    data = request.json
    slot_id = data.get("slot_id")

    if not slot_id:
        return jsonify({"error": "Slot ID missing"}), 400

    slot = mongo.db.assessment_slots.find_one({"_id": ObjectId(slot_id)})

    if not slot:
        return jsonify({"error": "Slot not found"}), 404

    if slot["booked"] >= slot["capacity"]:
        return jsonify({"error": "Slot full"}), 400

    # ✅ Increase booked count
    mongo.db.assessment_slots.update_one(
        {"_id": ObjectId(slot_id)},
        {"$inc": {"booked": 1}}
    )

    session_id = f"session_{int(time.time()*1000)}"

    # ✅ Update application
    mongo.db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {
            "assessment_slot": {
                "date": slot["date"],
                "time": slot["time"]
            },
            "status": "slot_selected",
            "session_id": session_id,
            "test_status": "not_started"
        }}
    )

    # ✅ Send email
    app = mongo.db.applications.find_one({"_id": ObjectId(application_id)})
    send_assessment_email(app["email"], app["student_name"], slot["date"], slot["time"])

    return jsonify({"message": "Slot booked successfully"})

@application_bp.route("/api/slots/<date>")
@jwt_required()
def get_slots_by_date(date):

    # 🔍 check existing
    slots = list(mongo.db.assessment_slots.find({"date": date}))

    # ✅ auto create if empty
    if not slots:
        times = [
            "09:00 AM", "11:00 AM", "01:00 PM",
            "03:00 PM", "05:00 PM", "07:00 PM"
        ]

        created_slots = []

        for t in times:
            slot = {
                "date": date,
                "time": t,
                "capacity": 3,
                "booked": 0
            }

            inserted = mongo.db.assessment_slots.insert_one(slot)

            created_slots.append({
                "_id": str(inserted.inserted_id),
                "time": t,
                "available": True
            })

        return jsonify(created_slots)

    # ✅ return existing
    result = []
    for s in slots:
        result.append({
            "_id": str(s["_id"]),
            "time": s["time"],
            "available": s["booked"] < s["capacity"]
        })

    return jsonify(result)

@application_bp.route('/start-test/<application_id>', methods=['POST'])
@jwt_required()
def start_test(application_id):

    application = mongo.db.applications.find_one({
        "_id": ObjectId(application_id)
    })

    if not application:
        return jsonify({"error": "Application not found"}), 404

    # ✅ mark complete
    mongo.db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"test_status": "completed"}}
    )

    # ✅ create offer if not exists
    existing_offer = mongo.db.offers.find_one({
        "application_id": ObjectId(application_id)
    })

    if not existing_offer:
        mongo.db.offers.insert_one({
            "student_id": application["student_id"],
            "application_id": application["_id"],
            "domain": application.get("domain", "general"),
            "duration": "3 Months",
            "manager_name": "Ali Khan",
            "status": "pending",
            "created_at": datetime.utcnow()
        })

    return jsonify({
        "message": "Test completed & offer generated",
        "proctor_url": "https://internbuddy-proctor.onrender.com"
    })

@application_bp.route("/api/requests", methods=["POST"])
@jwt_required()
def submit_request():
    try:
        data = request.json
        user_id = get_jwt_identity()

        subject = data.get("subject")
        message = data.get("message")

        if not subject or not message:
            return jsonify({"error": "Subject and message required"}), 400

        # Optional: student info (for display later)
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        request_doc = {
            "student_id": ObjectId(user_id),
            "student_name": user.get("name") if user else None,
            "email": user.get("email") if user else None,
            "subject": subject,
            "message": message,
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        mongo.db.requests.insert_one(request_doc)

        return jsonify({"message": "Request submitted successfully"}), 201

    except Exception as e:
        print("REQUEST ERROR:", e)
        return jsonify({"error": "Server error"}), 500
    

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@application_bp.route("/api/student-offers", methods=["GET"])
@jwt_required()
def get_student_offers():
    try:
        user_id = get_jwt_identity()

        offers = list(mongo.db.offers.find({
            "student_id": ObjectId(user_id)
        }))

        result = []

        for o in offers:
            result.append({
                "_id": str(o["_id"]),
                "domain": o.get("domain"),
                "duration": o.get("duration"),
                "manager_name": o.get("manager_name"),
                "status": o.get("status")
            })

        return jsonify({"offers": result})

    except Exception as e:
        print("OFFERS ERROR:", e)
        return jsonify({"offers": []}), 500
    
@application_bp.route("/api/offer-action/<offer_id>", methods=["POST"])
@jwt_required()
def handle_offer(offer_id):
    try:
        data = request.json
        action = data.get("action")  # accepted / rejected

        offer = mongo.db.offers.find_one({"_id": ObjectId(offer_id)})
        if not offer:
            return jsonify({"error": "Offer not found"}), 404

        # ================= ACCEPT =================
        if action == "accepted":

            # 🔐 Generate LMS credentials
            lms_email = f"internbuddy_{str(offer['student_id'])[-4:]}@internbuddy.com"
            lms_password = generate_password()

            # 💾 Save in DB
            mongo.db.offers.update_one(
                {"_id": ObjectId(offer_id)},
                {"$set": {
                    "status": "accepted",
                    "lms_email": lms_email,
                    "lms_password": lms_password,
                    "accepted_at": datetime.utcnow()
                }}
            )

            # 📄 Get student + application data
            application = mongo.db.applications.find_one({
                "_id": offer["application_id"]
            })

            student_name = application.get("student_name", "Student")
            student_email = application.get("email")

            # ================= EMAIL CONTENT =================
            subject = "🎉 Internship Offer - InternBuddy"

            message = f"""
Hello {student_name},

Congratulations! 🎉

You have been selected for the {offer['domain'].upper()} Internship at InternBuddy.

📌 Internship Details:
- Duration: {offer['duration']}
- Manager: {offer['manager_name']}

🔐 LMS Credentials:
- Email: {lms_email}
- Password: {lms_password}

Please use these credentials to log into your InternBuddy LMS.

We are excited to have you onboard 🚀

Best Regards,
InternBuddy Team
"""

            # 📧 SEND EMAIL
            send_email(subject, student_email, message)

            return jsonify({"message": "Offer accepted & email sent"})

        # ================= REJECT =================
        elif action == "rejected":

            mongo.db.offers.update_one(
                {"_id": ObjectId(offer_id)},
                {"$set": {"status": "rejected"}}
            )

            return jsonify({"message": "Offer rejected"})

        else:
            return jsonify({"error": "Invalid action"}), 400

    except Exception as e:
        print("OFFER ACTION ERROR:", e)
        return jsonify({"error": "Server error"}), 500
    

@application_bp.route("/manager/requests", methods=["GET"])
@jwt_required()
def get_requests():
    try:
        requests = list(mongo.db.requests.find())

        result = []
        for r in requests:
            result.append({
                "_id": str(r["_id"]),
                "name": r.get("student_name"),
                "email": r.get("email"),
                "subject": r.get("subject"),
                "message": r.get("message"),
                "status": r.get("status")
            })

        return jsonify(result)

    except Exception as e:
        print("REQUEST ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500

@application_bp.route("/manager/assigned", methods=["GET"])
@jwt_required()
def assigned_students_api():
    try:
        offers = list(mongo.db.offers.find())

        result = []
        for o in offers:
            result.append({
                "_id": str(o["_id"]),
                "domain": o.get("domain"),
                "manager": o.get("manager_name"),
                "status": o.get("status")
            })

        return jsonify(result)

    except Exception as e:
        print("ASSIGNED ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500

@application_bp.route("/manager/accepted", methods=["GET"])
@jwt_required()
def accepted_students_api():
    try:
        offers = list(mongo.db.offers.find({"status": "accepted"}))

        result = []
        for o in offers:
            result.append({
                "_id": str(o["_id"]),
                "domain": o.get("domain"),
                "manager": o.get("manager_name")
            })

        return jsonify(result)

    except Exception as e:
        print("ACCEPTED ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500