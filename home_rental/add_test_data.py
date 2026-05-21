"""
Run this to add sample listings to MongoDB for testing.
Command: python add_test_data.py
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')
django.setup()

from apps.listings.models import (
    Listing, GeoLocation, TrustInfo, EnvironmentScore, NearbyAmenity
)
from apps.accounts.models import User
from django.contrib.auth.models import User as DjangoUser
import bcrypt

print("=" * 50)
print("   NestMate — Adding Test Data")
print("=" * 50)

# ── Create test owner ──────────────────────────────────────────────────────────
django_user, created = DjangoUser.objects.get_or_create(
    username='testowner',
    defaults={'email': 'testowner@nestmate.com'}
)
if created:
    django_user.set_password('test123456')
    django_user.save()
    print("✅ Django user created")

mongo_user = User.objects(email='testowner@nestmate.com').first()
if not mongo_user:
    hashed = bcrypt.hashpw(b'test123456', bcrypt.gensalt()).decode('utf-8')
    mongo_user = User(
        username    = 'testowner',
        email       = 'testowner@nestmate.com',
        password    = hashed,
        full_name   = 'Rahul Sharma',
        phone       = '+91 9876543210',
        role        = 'owner',
        city        = 'Mumbai',
        id_verified = True,
        bill_verified = True,
        trust_score = 90,
    )
    mongo_user.save()
    print("✅ MongoDB user created")
else:
    print("✅ User already exists")

# ── Sample listings ────────────────────────────────────────────────────────────
listings_data = [
    {
        'title':        'Spacious 2BHK in Koramangala with Parking',
        'description':  'Beautiful fully furnished apartment near metro station. Close to tech parks, restaurants and cafes. 24/7 security and power backup.',
        'rent':         22000,
        'deposit':      44000,
        'listing_type': 'apartment',
        'bedrooms':     2,
        'bathrooms':    2,
        'area_sqft':    950,
        'furnished':    'fully',
        'city':         'Bangalore',
        'locality':     'Koramangala',
        'address':      '5th Block, Koramangala, Bangalore',
        'latitude':     12.9352,
        'longitude':    77.6245,
        'amenities':    ['wifi', 'ac', 'parking', 'gym', 'lift', 'security'],
        'photos': [
            'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80',
            'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80',
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80',
        ],
        'trust_score':   92,
        'price_verdict': 'fair',
        'market_price':  21000,
        'safety_score':  8.5,
        'walkability':   8.0,
        'noise_level':   'low',
        'nearby': [
            {'name': 'Metro Station', 'distance': 400,  'icon': '🚇', 'category': 'transport'},
            {'name': 'Hospital',      'distance': 800,  'icon': '🏥', 'category': 'hospital'},
            {'name': 'Grocery Store', 'distance': 200,  'icon': '🛒', 'category': 'grocery'},
        ],
    },
    {
        'title':        'Modern Studio Apartment in Bandra West',
        'description':  'Cozy studio apartment perfect for working professionals. Sea view from balcony. Walking distance to Bandra station.',
        'rent':         35000,
        'deposit':      70000,
        'listing_type': 'studio',
        'bedrooms':     1,
        'bathrooms':    1,
        'area_sqft':    500,
        'furnished':    'fully',
        'city':         'Mumbai',
        'locality':     'Bandra',
        'address':      'Bandra West, Mumbai',
        'latitude':     19.0596,
        'longitude':    72.8295,
        'amenities':    ['wifi', 'ac', 'security', 'cctv', 'lift'],
        'photos': [
            'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80',
            'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',
        ],
        'trust_score':   88,
        'price_verdict': 'fair',
        'market_price':  34000,
        'safety_score':  9.0,
        'walkability':   9.0,
        'noise_level':   'medium',
        'nearby': [
            {'name': 'Bandra Station', 'distance': 600,  'icon': '🚇', 'category': 'transport'},
            {'name': 'Linking Road',   'distance': 300,  'icon': '🛒', 'category': 'grocery'},
        ],
    },
    {
        'title':        'Affordable PG near Hinjewadi IT Park',
        'description':  'Student and professional friendly PG with meals included. AC rooms, fast WiFi, laundry service available.',
        'rent':         6000,
        'deposit':      12000,
        'listing_type': 'pg',
        'bedrooms':     1,
        'bathrooms':    1,
        'area_sqft':    200,
        'furnished':    'fully',
        'city':         'Pune',
        'locality':     'Wakad',
        'address':      'Wakad Road, Near Hinjewadi, Pune',
        'latitude':     18.5984,
        'longitude':    73.7626,
        'amenities':    ['wifi', 'ac', 'security', 'washing_machine'],
        'photos': [
            'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&q=80',
            'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
        ],
        'trust_score':    78,
        'price_verdict':  'fair',
        'market_price':   6500,
        'is_student_only': True,
        'safety_score':   7.5,
        'walkability':    7.0,
        'noise_level':    'low',
        'nearby': [
            {'name': 'IT Park Bus Stop', 'distance': 300, 'icon': '🚌', 'category': 'transport'},
            {'name': 'Canteen',          'distance': 100, 'icon': '🍽️', 'category': 'restaurant'},
        ],
    },
    {
        'title':        '3BHK Luxury Villa in Jubilee Hills',
        'description':  'Spacious villa with private garden and terrace. Gated community with 24/7 security. Premium interiors and appliances.',
        'rent':         55000,
        'deposit':      110000,
        'listing_type': 'villa',
        'bedrooms':     3,
        'bathrooms':    3,
        'area_sqft':    2200,
        'furnished':    'fully',
        'city':         'Hyderabad',
        'locality':     'Jubilee Hills',
        'address':      'Road No. 12, Jubilee Hills, Hyderabad',
        'latitude':     17.4325,
        'longitude':    78.4071,
        'amenities':    ['wifi', 'ac', 'parking', 'garden', 'security', 'cctv', 'generator'],
        'photos': [
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80',
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
        ],
        'trust_score':   95,
        'price_verdict': 'fair',
        'market_price':  52000,
        'safety_score':  9.5,
        'walkability':   7.0,
        'noise_level':   'low',
        'nearby': [
            {'name': 'Hospital',      'distance': 500,  'icon': '🏥', 'category': 'hospital'},
            {'name': 'Mall',          'distance': 1200, 'icon': '🛒', 'category': 'grocery'},
            {'name': 'School',        'distance': 800,  'icon': '🎓', 'category': 'education'},
        ],
    },
    {
        'title':        'Coworking Space in HSR Layout',
        'description':  'Premium coworking space with dedicated desks and private cabins. High-speed internet, conference room, and cafeteria.',
        'rent':         8000,
        'deposit':      16000,
        'listing_type': 'coworking',
        'bedrooms':     0,
        'bathrooms':    2,
        'area_sqft':    1200,
        'furnished':    'fully',
        'city':         'Bangalore',
        'locality':     'HSR Layout',
        'address':      'Sector 2, HSR Layout, Bangalore',
        'latitude':     12.9116,
        'longitude':    77.6741,
        'amenities':    ['wifi', 'ac', 'parking', 'cafeteria', 'security', 'lift', 'cctv'],
        'photos': [
            'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80',
            'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800&q=80',
        ],
        'trust_score':   85,
        'price_verdict': 'fair',
        'market_price':  7500,
        'safety_score':  9.0,
        'walkability':   8.5,
        'noise_level':   'low',
        'nearby': [
            {'name': 'Metro Station', 'distance': 900,  'icon': '🚇', 'category': 'transport'},
            {'name': 'Restaurant',    'distance': 150,  'icon': '🍽️', 'category': 'restaurant'},
        ],
    },
    {
        'title':        '1BHK Apartment in Indiranagar',
        'description':  'Well-maintained apartment in prime location. Walking distance to 100 Feet Road, metro, and restaurants.',
        'rent':         18000,
        'deposit':      36000,
        'listing_type': 'apartment',
        'bedrooms':     1,
        'bathrooms':    1,
        'area_sqft':    600,
        'furnished':    'semi',
        'city':         'Bangalore',
        'locality':     'Indiranagar',
        'address':      '100 Feet Road, Indiranagar, Bangalore',
        'latitude':     12.9784,
        'longitude':    77.6408,
        'amenities':    ['wifi', 'parking', 'lift', 'security'],
        'photos': [
            'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
            'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80',
        ],
        'trust_score':   82,
        'price_verdict': 'fair',
        'market_price':  17000,
        'safety_score':  8.0,
        'walkability':   9.0,
        'noise_level':   'medium',
        'nearby': [
            {'name': 'Metro Station', 'distance': 350,  'icon': '🚇', 'category': 'transport'},
            {'name': 'Supermarket',   'distance': 200,  'icon': '🛒', 'category': 'grocery'},
            {'name': 'Hospital',      'distance': 600,  'icon': '🏥', 'category': 'hospital'},
        ],
    },
    {
        'title':        'Shop for Rent in T Nagar',
        'description':  'Prime retail space on busy shopping street. Ground floor with high footfall. Ideal for clothing, electronics or food business.',
        'rent':         40000,
        'deposit':      120000,
        'listing_type': 'shop',
        'bedrooms':     0,
        'bathrooms':    1,
        'area_sqft':    400,
        'furnished':    'unfurnished',
        'city':         'Chennai',
        'locality':     'T Nagar',
        'address':      'Usman Road, T Nagar, Chennai',
        'latitude':     13.0418,
        'longitude':    80.2341,
        'amenities':    ['security', 'cctv', 'parking'],
        'photos': [
            'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80',
            'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=800&q=80',
        ],
        'trust_score':   80,
        'price_verdict': 'fair',
        'market_price':  38000,
        'safety_score':  7.5,
        'walkability':   9.5,
        'noise_level':   'high',
        'nearby': [
            {'name': 'Bus Stop',      'distance': 100,  'icon': '🚌', 'category': 'transport'},
            {'name': 'Bank',          'distance': 300,  'icon': '🏦', 'category': 'bank'},
        ],
    },
    {
        'title':        '2BHK in Andheri West Near Metro',
        'description':  'Spacious 2BHK with modern interiors and great ventilation. Just 5 minutes walk from Andheri metro station.',
        'rent':         28000,
        'deposit':      56000,
        'listing_type': 'apartment',
        'bedrooms':     2,
        'bathrooms':    2,
        'area_sqft':    850,
        'furnished':    'semi',
        'city':         'Mumbai',
        'locality':     'Andheri',
        'address':      'Andheri West, Near Metro, Mumbai',
        'latitude':     19.1196,
        'longitude':    72.8464,
        'amenities':    ['wifi', 'ac', 'parking', 'lift', 'security', 'cctv'],
        'photos': [
            'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80',
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80',
            'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=800&q=80',
        ],
        'trust_score':   86,
        'price_verdict': 'fair',
        'market_price':  27000,
        'safety_score':  8.0,
        'walkability':   8.5,
        'noise_level':   'medium',
        'nearby': [
            {'name': 'Metro Station', 'distance': 400,  'icon': '🚇', 'category': 'transport'},
            {'name': 'D-Mart',        'distance': 600,  'icon': '🛒', 'category': 'grocery'},
            {'name': 'Hospital',      'distance': 900,  'icon': '🏥', 'category': 'hospital'},
        ],
    },
    {
        'title':        'Farmhouse for Weekend Stay near Pune',
        'description':  'Beautiful farmhouse with swimming pool, garden and BBQ area. Perfect for weekend getaway or corporate retreats.',
        'rent':         25000,
        'deposit':      50000,
        'listing_type': 'farmhouse',
        'bedrooms':     4,
        'bathrooms':    3,
        'area_sqft':    3500,
        'furnished':    'fully',
        'city':         'Pune',
        'locality':     'Khed',
        'address':      'Khed-Shivapur Road, Pune',
        'latitude':     18.3167,
        'longitude':    73.8833,
        'amenities':    ['parking', 'garden', 'security', 'generator', 'ac'],
        'photos': [
            'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80',
            'https://images.unsplash.com/photo-1416331108676-a22ccb276e35?w=800&q=80',
        ],
        'trust_score':   75,
        'price_verdict': 'fair',
        'market_price':  24000,
        'safety_score':  8.5,
        'walkability':   4.0,
        'noise_level':   'low',
        'nearby': [
            {'name': 'Highway',  'distance': 2000, 'icon': '🛣️', 'category': 'transport'},
        ],
    },
    {
        'title':        'Office Space in Gachibowli IT Hub',
        'description':  'Ready-to-move office space in prime IT corridor. Fully furnished with reception, 20 seats, and conference room.',
        'rent':         45000,
        'deposit':      90000,
        'listing_type': 'office',
        'bedrooms':     0,
        'bathrooms':    2,
        'area_sqft':    1000,
        'furnished':    'fully',
        'city':         'Hyderabad',
        'locality':     'Gachibowli',
        'address':      'Financial District, Gachibowli, Hyderabad',
        'latitude':     17.4401,
        'longitude':    78.3489,
        'amenities':    ['wifi', 'ac', 'parking', 'security', 'lift', 'cctv', 'cafeteria'],
        'photos': [
            'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80',
            'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&q=80',
        ],
        'trust_score':   90,
        'price_verdict': 'fair',
        'market_price':  43000,
        'safety_score':  9.0,
        'walkability':   7.5,
        'noise_level':   'low',
        'nearby': [
            {'name': 'Metro Station', 'distance': 700,  'icon': '🚇', 'category': 'transport'},
            {'name': 'Restaurant',    'distance': 200,  'icon': '🍽️', 'category': 'restaurant'},
            {'name': 'ATM',           'distance': 100,  'icon': '🏦', 'category': 'bank'},
        ],
    },
]

print(f"\nCreating {len(listings_data)} listings...")

created_count = 0
skipped_count = 0

for data in listings_data:
    existing = Listing.objects(title=data['title']).first()
    if existing:
        print(f"  ⏭️  Already exists: {data['title'][:50]}")
        skipped_count += 1
        continue

    # Build nearby amenities
    nearby_list = []
    for n in data.get('nearby', []):
        nearby_list.append(NearbyAmenity(
            name     = n['name'],
            distance = n['distance'],
            icon     = n['icon'],
            category = n['category'],
        ))

    location = GeoLocation(
        city      = data['city'],
        locality  = data['locality'],
        address   = data.get('address', ''),
        latitude  = data.get('latitude'),
        longitude = data.get('longitude'),
    )

    trust = TrustInfo(
        score             = data.get('trust_score', 70),
        id_verified       = True,
        bill_uploaded     = True,
        video_walkthrough = False,
        reviews_count     = 0,
        avg_rating        = 0.0,
    )

    env = EnvironmentScore(
        safety_score = data.get('safety_score', 7.0),
        walkability  = data.get('walkability',  7.0),
        noise_level  = data.get('noise_level',  'medium'),
        air_quality  = 'good',
        nearby       = nearby_list,
    )

    listing = Listing(
        owner             = mongo_user,
        title             = data['title'],
        description       = data['description'],
        rent              = data['rent'],
        deposit           = data['deposit'],
        listing_type      = data['listing_type'],
        rental_period     = 'monthly',
        bedrooms          = data.get('bedrooms', 1),
        bathrooms         = data.get('bathrooms', 1),
        area_sqft         = data.get('area_sqft'),
        furnished         = data.get('furnished', 'semi'),
        amenities         = data.get('amenities', []),
        photos            = data.get('photos', []),
        is_available      = True,
        is_scam_flagged   = False,
        is_featured       = True,
        is_student_only   = data.get('is_student_only', False),
        is_negotiable     = True,
        pets_allowed      = False,
        smoking_allowed   = False,
        bachelors_allowed = True,
        target_gender     = 'any',
        location          = location,
        trust_info        = trust,
        environment_score = env,
        market_price      = data.get('market_price', data['rent']),
        price_verdict     = data.get('price_verdict', 'fair'),
        price_diff_pct    = 0.0,
        views_count       = 0,
        saves_count       = 0,
    )
    listing.save()
    print(f"  ✅ Created: {data['title'][:50]}")
    created_count += 1

print(f"\n{'=' * 50}")
print(f"  Done! Created {created_count}, Skipped {skipped_count}")
print(f"{'=' * 50}")
print(f"\n  Open: http://localhost:3000")
print(f"  Login: testowner@nestmate.com / test123456")