#!/usr/bin/env python
"""Fix and cleanup listings"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')
django.setup()

from apps.listings.models import Listing

# Find and fix the "Modern Fully Furnished 2BHK Flat" listing
listing = Listing.objects(title__icontains='Modern Fully Furnished').first()

if listing:
    print(f'Found: {listing.title}')
    print(f'Current Status:')
    print(f'  is_scam_flagged: {listing.is_scam_flagged}')
    print(f'  scam_risk_score: {listing.scam_risk_score}')
    print(f'  scam_reasons: {listing.scam_reasons}')
    print()
    
    # Remove scam flag
    listing.update(
        is_scam_flagged=False,
        scam_risk_score=0,
        scam_reasons=[]
    )
    print('✅ Fixed! Scam flag removed')
    print()
    
    # Reload and verify
    listing.reload()
    print(f'Updated Status:')
    print(f'  is_scam_flagged: {listing.is_scam_flagged}')
    print(f'  scam_risk_score: {listing.scam_risk_score}')
    print(f'  scam_reasons: {listing.scam_reasons}')
else:
    print('❌ Listing not found')
