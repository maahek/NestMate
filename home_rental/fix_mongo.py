import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_rental.settings")
django.setup()

from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["nestmate"]

result = db.roommate_matches.update_many(
    {"status": {"$exists": False}},
    {"$set": {"status": "pending"}}
)

print(f"Fixed {result.modified_count} roommate_match documents")

result2 = db.roommate_profiles.update_many(
    {"is_looking": {"$exists": False}},
    {"$set": {"is_looking": True}}
)

print(f"Fixed {result2.modified_count} roommate_profile documents")

print("Done!")