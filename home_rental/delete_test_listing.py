#!/usr/bin/env python
"""Delete test listing"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')
django.setup()

from apps.listings.models import Listing

# Delete the test listing
test_listing_id = '6a01f709e5a6eca2dc1d57eb'

try:
    listing = Listing.objects.get(id=test_listing_id)
    title = listing.title
    owner = listing.owner.username if listing.owner else 'Unknown'
    listing.delete()
    print(f'✅ Deleted test listing: "{title}" by {owner}')
except Exception as e:
    print(f'❌ Error: {str(e)}')
