#!/usr/bin/env python
"""
Fix RoommateMatch documents directly at MongoDB level.
This removes stale fields using PyMongo.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

def fix_roommate_matches_direct():
    """Remove stale fields from RoommateMatch collection using PyMongo."""
    
    # Get MongoDB connection from settings
    mongo_settings = settings.MONGODB_SETTINGS
    host = mongo_settings.get('host', 'localhost')
    port = mongo_settings.get('port', 27017)
    db_name = mongo_settings.get('db', 'nestmate')
    
    client = MongoClient(host, port)
    db = client[db_name]
    collection = db['roommate_matches']
    
    # Remove the stale fields from all documents
    result = collection.update_many(
        {},  # match all documents
        {
            '$unset': {
                'is_rejected': 1,
                'breakdown': 1,
                'is_accepted': 1
            }
        }
    )
    
    print(f"✓ Updated {result.modified_count} documents")
    print(f"✓ Matched {result.matched_count} documents")
    
    # Verify the fix
    sample = collection.find_one({})
    if sample:
        print(f"\nSample document after cleanup:")
        print(f"  ID: {sample.get('_id')}")
        print(f"  Fields: {list(sample.keys())}")
    
    client.close()

if __name__ == '__main__':
    fix_roommate_matches_direct()
    print("\nDone! Stale fields have been removed from MongoDB.")
