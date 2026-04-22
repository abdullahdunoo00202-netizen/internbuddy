from flask_mail import Message
from flask import current_app
from extensions import mail

print("🔥 email_service.py LOADED")



# =========================================
# 🔹 GENERIC EMAIL FUNCTION (BASE)
# =========================================
def send_email(subject, recipient, body=None, html=None):
    """
    Generic InternBuddy branded email sender
    Supports BOTH plain text and HTML emails
    """

    print("📧 EMAIL FUNCTION CALLED →", recipient)

    sender = current_app.config.get("MAIL_DEFAULT_SENDER")

    msg = Message(
        subject=subject,
        sender=sender,
        recipients=[recipient]
    )

    # ✅ Support both types
    if html:
        msg.html = html
    else:
        msg.body = body

    try:
        mail.send(msg)
        print("✅ EMAIL SENT SUCCESSFULLY")
    except Exception as e:
        print("❌ EMAIL ERROR:", str(e))


# =========================================
# 🔹 APPLICATION STATUS EMAIL (APPROVE/REJECT)
# =========================================
def send_application_status_email(student_name, student_email, internship_domain, status):

    print("📧 send_application_status_email CALLED")

    internship_domain = internship_domain.upper()

    if status == "approved":
        subject = "🎉 Internship Application Approved | InternBuddy"

        body = f"""
Dear {student_name},

Congratulations! 🎉

We are pleased to inform you that your application for the
{internship_domain} Internship has been successfully approved.

🔹 NEXT STEP:
Please log in and select your assessment slot.

👉 Dashboard:
http://localhost:5000/student/dashboard

Warm regards,
InternBuddy Team
"""

    else:
        subject = "Internship Application Update | InternBuddy"

        body = f"""
Dear {student_name},

Thank you for applying to the {internship_domain} Internship.

We regret to inform you that your application was not selected.

We encourage you to apply again in the future.

Warm regards,
InternBuddy Team
"""

    send_email(subject, student_email, body=body)


# =========================================
# 🔹 ASSESSMENT EMAIL (SLOT SELECT)
# =========================================
def send_assessment_email(to_email, student_name, date, time):

    print("📧 send_assessment_email CALLED →", to_email)

    subject = "Your Internship Assessment Has Been Scheduled – InternBuddy"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; max-width:600px; margin:auto;">

        <h2 style="color:#4A90E2;">InternBuddy Smart Internship Partner</h2>

        <p>Dear {student_name},</p>

        <p>Your internship assessment has been successfully scheduled.</p>

        <hr>

        <h3>📅 Assessment Details:</h3>
        <p><b>Date:</b> {date}</p>
        <p><b>Time:</b> {time}</p>

        <h3>🧪 Start Your Test:</h3>
        <p>
            <a href="https://internbuddy-proctor.onrender.com/start-test"
               style="background:#4A90E2; color:white; padding:12px 18px; text-decoration:none; border-radius:6px; display:inline-block;">
               ▶ Start Assessment
            </a>
        </p>

        <h3>🔐 Login Details:</h3>
        <ul>
            <li><b>Passkey:</b> internbuddy</li>
            <li>Use your <b>CNIC number</b> for verification</li>
        </ul>

        <h3>⚠️ Important Instructions:</h3>
        <ul>
            <li>Ensure camera & microphone are working</li>
            <li>Stable internet connection required</li>
            <li>Do not switch tabs during test</li>
            <li>Fullscreen mode is mandatory</li>
            <li>AI-based proctoring will monitor your activity</li>
        </ul>

        <h3>▶️ Steps to Start:</h3>
        <ol>
            <li>Click "Start Assessment"</li>
            <li>Complete system check</li>
            <li>Verify CNIC + face</li>
            <li>Enter passkey</li>
            <li>Begin test</li>
        </ol>

        <p>Best of luck!</p>

        <br>
        <p><b>InternBuddy Team</b><br>Smart Internship Partner</p>

    </div>
    """

    # ✅ USE GENERIC FUNCTION
    send_email(
        subject=subject,
        recipient=to_email,
        html=html_content
    )

def send_offer_email(to_email, student_name, domain, duration, manager, lms_email, lms_password):
    subject = "InternBuddy Internship Offer 🎉"

    html = f"""
    <h2>Congratulations {student_name} 🎉</h2>
    <p>You have been selected for <b>{domain.upper()} Internship</b></p>

    <h3>Internship Details</h3>
    <ul>
        <li>Duration: {duration}</li>
        <li>Manager: {manager}</li>
    </ul>

    <h3>LMS Credentials</h3>
    <ul>
        <li>Email: {lms_email}</li>
        <li>Password: {lms_password}</li>
    </ul>

    <p>Welcome to InternBuddy 🚀</p>
    """

    send_email(subject, to_email, html)