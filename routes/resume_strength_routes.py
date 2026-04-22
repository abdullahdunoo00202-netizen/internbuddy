from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os

from ai.resume_parser import extract_resume_text
from ai.resume_strength import calculate_resume_strength

resume_strength_bp = Blueprint("resume_strength", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_strength_bp.route("/resume-strength", methods=["POST"])
@jwt_required()
def resume_strength():
    resume = request.files.get("resume")

    if not resume or resume.filename == "":
        return jsonify({"error": "Resume file required"}), 400

    if not allowed_file(resume.filename):
        return jsonify({"error": "Invalid file type"}), 400

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(resume.filename)
    path = os.path.join(upload_folder, filename)
    resume.save(path)

    # 🔥 AI MAGIC
    text = extract_resume_text(path)
    result = calculate_resume_strength(text)

    return jsonify({
        "resume_strength": result["score"],
        "skills_found": result["skills_found"]
    }), 200
