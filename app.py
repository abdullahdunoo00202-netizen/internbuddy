import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, jsonify
from flask_jwt_extended import jwt_required
from config.config import Config
from extensions import mongo, bcrypt, mail, jwt
from flask import send_from_directory

app = Flask(__name__)
app.config.from_object(Config)

# ---------------- FILE UPLOAD CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

# ---------------- INIT EXTENSIONS ----------------
mongo.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)
jwt.init_app(app)

# ---------------- HTML ROUTES ----------------

@app.route("/")
def splash():
    return render_template("splash.html")

@app.route("/auth")
def auth_page():
    return render_template("auth.html")

@app.route("/login")
def login_page():
    return render_template("auth.html")

@app.route("/student-dashboard-page")
def student_dash_page():
    return render_template("student_dashboard.html")

@app.route("/student/dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/student/my-applications")
def my_applications_page():
    return render_template("my_applications.html")

@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ===============================
# APPLY FORM (🔥 FIXED ROUTE 🔥)
# ===============================
@app.route("/apply/<domain>")
def application_form(domain):
    internship = mongo.db.internships.find_one({"domain": domain})

    if not internship:
        return "Internship information missing. Please go back to dashboard.", 400

    return render_template(
        "application_form.html",
        domain=domain,
        internship_id=str(internship["_id"])
    )

@app.route("/test-email")
def test_email():
    from utils.email_service import send_email
    send_email(
        "Test InternBuddy Email",
        "abdullahdunoo00202@gmail.com",
        "This is a direct test email from InternBuddy."
    )
    return "Email trigger called"

@app.route("/student/request")
def student_request_page():
    return render_template("student_request.html")

@app.route("/student/offers")
def offers_page():
    return render_template("student_offers.html")

# ================= MANAGER PAGES =================

@app.route("/manager/requests")
def manager_requests():
    return render_template("manager_requests.html")

@app.route("/manager/assigned-students")
def manager_assigned():
    return render_template("manager_assigned.html")

@app.route("/manager/accepted-students")
def manager_accepted():
    return render_template("manager_accepted.html")

@app.route("/manager/interns")
def manager_interns():
    return render_template("manager_interns.html")

@app.route("/manager/rules")
def manager_rules():
    return render_template("manager_rules.html")

@app.route("/manager/privacy")
def manager_privacy():
    return render_template("manager_privacy.html")

@app.route("/manager/completed-interns")
def manager_completed():
    return render_template("manager_completed.html")
# ---------------- API BLUEPRINTS ----------------
# ---------------- API BLUEPRINTS ----------------
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.application_routes import application_bp
from routes.resume_strength_routes import resume_strength_bp
from routes.manager_routes import manager_bp
#from routes.proctor_routes import proctor_bp




#app.register_blueprint(proctor_bp)
app.register_blueprint(manager_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(application_bp)
app.register_blueprint(resume_strength_bp, url_prefix="/api")


# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

print("MONGO_URI:", os.getenv("MONGO_URI"))
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 🔥 IMPORTANT FOR RENDER
    app.run(host="0.0.0.0", port=port)
