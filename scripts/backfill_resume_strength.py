from extensions import mongo
from ai.resume_parser import extract_resume_text
from ai.resume_strength import calculate_resume_strength
import os

UPLOAD_FOLDER = "uploads"

apps = mongo.db.applications.find({
    "resume": {"$exists": True}
})

for app in apps:
    resume_file = app.get("resume")
    if not resume_file:
        continue

    path = os.path.join(UPLOAD_FOLDER, resume_file)
    if not os.path.exists(path):
        continue

    text = extract_resume_text(path)
    print("TEXT LENGTH:", len(text))

    score = calculate_resume_strength(text)["score"]

    mongo.db.applications.update_one(
        {"_id": app["_id"]},
        {"$set": {"resume_match": score}}
    )

    print(f"UPDATED → {score}%")

print("✅ DONE")
