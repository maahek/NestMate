#!/usr/bin/env python
"""
Cleanup script to:
1. List all listings and their status
2. Remove test/incomplete listings
3. Ensure valid data for display
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')
django.setup()

from apps.listings.models import Listing

def main():
    all_listings = list(Listing.objects.all())
    print(f'\n{"="*80}')
    print(f'Total Listings in DB: {len(all_listings)}')
    print(f'{"="*80}\n')
    
    # Categorize listings
    valid_listings = []
    invalid_listings = []
    
    for l in all_listings:
        has_location = l.location is not None
        has_city = l.location and l.location.city if has_location else False
        has_photos = len(l.photos) > 0 if l.photos else False
        is_available = l.is_available
        not_scam = not l.is_scam_flagged
        
        status = {
            'id': str(l.id),
            'title': l.title,
            'location': f"{l.location.city if has_location and l.location.city else 'MISSING'} / {l.location.locality if has_location and l.location.locality else 'MISSING'}",
            'rent': l.rent,
            'has_location': has_location,
            'has_city': has_city,
            'has_photos': has_photos,
            'is_available': is_available,
            'not_scam': not_scam,
            'created_at': l.created_at.strftime('%Y-%m-%d') if l.created_at else 'N/A',
            'owner': l.owner.username if l.owner else 'UNKNOWN'
        }
        
        # Valid = has location + city + photos + available + not flagged
        if has_location and has_city and has_photos and is_available and not_scam:
            valid_listings.append(status)
        else:
            invalid_listings.append(status)
    
    # Show valid listings
    print(f'\n✅ VALID LISTINGS ({len(valid_listings)} total):')
    print(f'{"-"*80}')
    for l in valid_listings:
        print(f"  Title: {l['title']}")
        print(f"    ID: {l['id']}")
        print(f"    Location: {l['location']}")
        print(f"    Rent: ₹{l['rent']}/mo | Owner: {l['owner']}")
        print()
    
    # Show invalid listings
    print(f'\n❌ INVALID LISTINGS ({len(invalid_listings)} total):')
    print(f'{"-"*80}')
    for l in invalid_listings:
        issues = []
        if not l['has_location']: issues.append('NO_LOCATION')
        if not l['has_city']: issues.append('NO_CITY')
        if not l['has_photos']: issues.append('NO_PHOTOS')
        if not l['is_available']: issues.append('NOT_AVAILABLE')
        if not l['not_scam']: issues.append('FLAGGED_SCAM')
        
        print(f"  Title: {l['title']}")
        print(f"    ID: {l['id']}")
        print(f"    Issues: {', '.join(issues)}")
        print(f"    Location: {l['location']} | Rent: ₹{l['rent']}/mo")
        print()
    
    # Options for cleanup
    print(f'\n{"="*80}')
    print('CLEANUP OPTIONS:')
    print(f'{"="*80}')
    print('\n1. Delete ALL invalid listings')
    print('   Command: python cleanup_listings.py --delete-invalid')
    print('\n2. Delete listings without location')
    print('   Command: python cleanup_listings.py --delete-no-location')
    print('\n3. Delete listings without photos')
    print('   Command: python cleanup_listings.py --delete-no-photos')
    print('\n4. Delete specific listing by ID')
    print('   Command: python cleanup_listings.py --delete-id <LISTING_ID>')
    print('\n5. Show this info again')
    print('   Command: python cleanup_listings.py')
    print()

def delete_invalid():
    """Delete all invalid listings"""
    all_listings = list(Listing.objects.all())
    deleted_count = 0
    
    for l in all_listings:
        has_location = l.location is not None
        has_city = l.location and l.location.city if has_location else False
        has_photos = len(l.photos) > 0 if l.photos else False
        is_available = l.is_available
        not_scam = not l.is_scam_flagged
        
        # Delete if invalid
        if not (has_location and has_city and has_photos and is_available and not_scam):
            print(f'🗑️  Deleting: {l.title} (ID: {str(l.id)[:8]}...)')
            l.delete()
            deleted_count += 1
    
    print(f'\n✅ Deleted {deleted_count} invalid listings')

def delete_no_location():
    """Delete listings without location"""
    listings = Listing.objects(location=None)
    count = listings.count()
    print(f'🗑️  Deleting {count} listings without location...')
    for l in listings:
        print(f'   - {l.title}')
        l.delete()
    print(f'✅ Deleted {count} listings')

def delete_no_photos():
    """Delete listings without photos"""
    all_listings = list(Listing.objects.all())
    deleted_count = 0
    for l in all_listings:
        if not l.photos or len(l.photos) == 0:
            print(f'🗑️  Deleting: {l.title}')
            l.delete()
            deleted_count += 1
    print(f'✅ Deleted {deleted_count} listings without photos')

def delete_by_id(listing_id):
    """Delete specific listing"""
    try:
        listing = Listing.objects.get(id=listing_id)
        title = listing.title
        listing.delete()
        print(f'✅ Deleted: {title}')
    except Exception as e:
        print(f'❌ Error: Listing not found or already deleted')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == '--delete-invalid':
            confirm = input('⚠️  Delete ALL invalid listings? Type "yes" to confirm: ')
            if confirm.lower() == 'yes':
                delete_invalid()
            else:
                print('Cancelled.')
        elif cmd == '--delete-no-location':
            confirm = input('⚠️  Delete all listings WITHOUT location? Type "yes" to confirm: ')
            if confirm.lower() == 'yes':
                delete_no_location()
            else:
                print('Cancelled.')
        elif cmd == '--delete-no-photos':
            confirm = input('⚠️  Delete all listings WITHOUT photos? Type "yes" to confirm: ')
            if confirm.lower() == 'yes':
                delete_no_photos()
            else:
                print('Cancelled.')
        elif cmd == '--delete-id' and len(sys.argv) > 2:
            listing_id = sys.argv[2]
            confirm = input(f'⚠️  Delete listing {listing_id[:8]}...? Type "yes" to confirm: ')
            if confirm.lower() == 'yes':
                delete_by_id(listing_id)
            else:
                print('Cancelled.')
        else:
            print('Unknown command')
            main()
    else:
        main()
