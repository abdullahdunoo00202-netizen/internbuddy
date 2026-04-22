from extensions import mongo

DATE = "2026-02-01"

TIMES = [
    "09:00 - 10:45",
    "11:00 - 12:45",
    "13:00 - 14:45",
    "15:00 - 16:45"
]

for t in TIMES:
    mongo.db.assessment_slots.insert_one({
        "date": DATE,
        "time": t,
        "capacity": 3,
        "booked": 0
    })

print("Slots created")
