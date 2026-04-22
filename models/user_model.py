from datetime import datetime

def user_schema(name, email, password, role):
    return {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "is_verified": False,
        "created_at": datetime.now()
    }
