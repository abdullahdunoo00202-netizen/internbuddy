import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "internbuddy_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "internbuddy_jwt_secret")

    # ===============================
    # MongoDB
    # ===============================
    MONGO_URI = os.getenv("MONGO_URI")

    # ===============================
    # Mail Configuration (Gmail SMTP)
    # ===============================
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv("EMAIL")
    MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    # 🔥 IMPORTANT: Sender Name + Email
    MAIL_DEFAULT_SENDER = (
        "InternBuddy | Smart Internship Partner",
        os.getenv("EMAIL")
    )

    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True
    MAIL_USE_SSL = False