from datetime import datetime
from extensions import mongo

def log_violation(session_id, event_type, severity):
    mongo.db.proctor_logs.insert_one({
        "session_id": session_id,
        "event": event_type,
        "severity": severity,
        "timestamp": datetime.utcnow()
    })
