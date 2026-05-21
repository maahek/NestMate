"""
NestMate — Listings Models
All MongoDB documents for listings, reviews, market data,
roommate profiles, chat rooms, and agreements live here.
"""

from mongoengine import (
    Document, EmbeddedDocument,
    StringField, IntField, FloatField, BooleanField,
    ListField, DictField, DateTimeField,
    ReferenceField, EmbeddedDocumentField,
    EmbeddedDocumentListField, EmailField
)
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# EMBEDDED DOCUMENTS
# These are nested inside Listing — not separate collections
# ══════════════════════════════════════════════════════════════════════════════

class GeoLocation(EmbeddedDocument):
    """
    Geographic location of a property.
    Used by Leaflet.js map (Feature 4).
    """
    latitude  = FloatField()
    longitude = FloatField()
    address   = StringField(max_length=300)    # full street address
    city      = StringField(max_length=100)
    locality  = StringField(max_length=100)    # neighbourhood / area
    pincode   = StringField(max_length=10)
    landmark  = StringField(max_length=200)    # optional: "near XYZ college"


class NearbyAmenity(EmbeddedDocument):
    """
    One nearby amenity entry.
    Example: { name: 'Metro Station', distance: 450, icon: '🚇' }
    Used in Environment Score (Feature 5).
    """
    name     = StringField(max_length=100)
    distance = FloatField()         # in metres
    icon     = StringField(max_length=10)    # emoji
    category = StringField(
        choices=['transport', 'hospital', 'grocery', 'education', 'restaurant', 'bank', 'other'],
        default='other'
    )


class EnvironmentScore(EmbeddedDocument):
    """
    Feature 5 — House Environment Score.
    Shows area safety, noise, walkability, and nearby places.
    """
    safety_score  = FloatField(default=0.0, min_value=0, max_value=10)
    noise_level   = StringField(
        choices=['low', 'medium', 'high'],
        default='medium'
    )
    air_quality   = StringField(
        choices=['good', 'moderate', 'poor'],
        default='good'
    )
    walkability   = FloatField(default=0.0, min_value=0, max_value=10)
    nearby        = EmbeddedDocumentListField(NearbyAmenity)


class TrustInfo(EmbeddedDocument):
    """
    Feature 2 — Verified Listings / Trust Score.
    Embedded inside Listing so it shows on search results.
    Score breakdown:
      ID Verified      → +40
      Bill Uploaded    → +25
      Video Walkthrough → +20
      Reviews          → +3 each, max +15
    """
    score              = IntField(default=0, min_value=0, max_value=100)
    id_verified        = BooleanField(default=False)
    bill_uploaded      = BooleanField(default=False)
    video_walkthrough  = BooleanField(default=False)
    reviews_count      = IntField(default=0)
    avg_rating         = FloatField(default=0.0)


# ══════════════════════════════════════════════════════════════════════════════
# LISTING DOCUMENT
# Main collection — one document per property listing
# ══════════════════════════════════════════════════════════════════════════════

class Listing(Document):
    """
    Core listing document.
    Covers Features: 2, 3, 4, 5, 6, 7, 8
    """

    # ── Owner ─────────────────────────────────────────────────────────────────
    # Lazy reference to User in 'users' collection
    from apps.accounts.models import User
    owner = ReferenceField(User, required=True)

    # ── Basic Info ────────────────────────────────────────────────────────────
    title       = StringField(required=True, max_length=200)
    description = StringField(max_length=3000)
    slug        = StringField(max_length=220, unique=False)    # for SEO URLs

    # ── Pricing ───────────────────────────────────────────────────────────────
    rent        = IntField(required=True, min_value=0)        # monthly ₹
    deposit     = IntField(default=0, min_value=0)
    maintenance = IntField(default=0)                          # monthly maintenance
    is_negotiable = BooleanField(default=True)

    # ── Type & Duration ───────────────────────────────────────────────────────

    listing_type = StringField(
    choices=[
        # ── Residential ───────────────────────────────────────
        ('apartment',    'Apartment'),
        ('house',        'Independent House'),
        ('villa',        'Villa / Bungalow'),
        ('studio',       'Studio Apartment'),
        ('pg',           'PG / Paying Guest'),
        ('shared_room',  'Shared Room'),
        ('hostel',       'Hostel'),

        # ── Commercial ────────────────────────────────────────
        ('shop',         'Shop / Retail Space'),
        ('office',       'Office Space'),
        ('warehouse',    'Warehouse / Godown'),
        ('showroom',     'Showroom'),
        ('coworking',    'Coworking Space'),

        # ── Creative / Special ─────────────────────────────────
        ('studio_space', 'Studio Space (Photo/Music/Art)'),
        ('event_hall',   'Event Hall / Banquet'),
        ('garage',       'Garage / Parking Space'),
        ('farmhouse',    'Farmhouse'),
        ('plot',         'Plot / Land'),
    ],
    default='apartment'
    )
    rental_period = StringField(
        choices=['monthly', 'short_term', 'student'],
        default='monthly'
    )
    min_stay_months = IntField(default=1)    # minimum stay required

    # ── Media (Feature 6 — Virtual Tour) ──────────────────────────────────────
    photos         = ListField(StringField())    # list of /media/listings/ URLs
    video_tour_url = StringField()               # YouTube / Drive / direct URL
    tour_360_url   = StringField()               # 360° virtual tour embed URL

    # ── Location (Feature 4 — Map Search) ────────────────────────────────────
    location = EmbeddedDocumentField(GeoLocation)

    # ── Property Details ──────────────────────────────────────────────────────
    bedrooms      = IntField(default=1, min_value=0)
    bathrooms     = IntField(default=1, min_value=0)
    area_sqft     = IntField(min_value=0)
    floor_number  = IntField(default=0)
    total_floors  = IntField(default=1)
    facing        = StringField(
        choices=['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'],
        default='east'
    )
    furnished     = StringField(
        choices=['unfurnished', 'semi', 'fully'],
        default='semi'
    )
    amenities = ListField(StringField())
    # Example amenities: wifi, ac, parking, gym, lift, geyser,
    # washing_machine, fridge, tv, gas, security, cctv, garden, terrace

    # ── Commercial-specific fields ─────────────────────────────────────────────
    carpet_area      = IntField()
    frontage         = FloatField()
    commercial_floor = StringField( 
        choices=[
            ('basement',  'Basement'),
            ('ground',    'Ground Floor'),
            ('mezzanine', 'Mezzanine'),
            ('1',         '1st Floor'),
            ('2',         '2nd Floor'),
            ('3plus',     '3rd Floor and above'),
            ],
            default='ground'
            )
    seating_capacity = IntField()
    ceiling_height   = FloatField()
    lease_type       = StringField(
        choices=[
            ('monthly',       'Monthly'),
            ('annual',        'Annual'),
            ('long_term',     'Long Term (3+ years)'),
            ('revenue_share', 'Revenue Share'),
            ],
            default='monthly'
            )
    lockin_months  = IntField(default=0)
    permitted_uses = ListField(StringField())
    is_commercial  = BooleanField(default=False)

    # ── Rules ─────────────────────────────────────────────────────────────────
    pets_allowed    = BooleanField(default=False)
    smoking_allowed = BooleanField(default=False)
    bachelors_allowed = BooleanField(default=True)
    target_gender   = StringField(
        choices=['any', 'male', 'female'],
        default='any'
    )

    # ── Student Rental (Feature 8) ────────────────────────────────────────────
    is_student_only  = BooleanField(default=False)
    near_college     = StringField(max_length=200)    # "Near IIT Bombay"
    college_distance = IntField()                     # in metres

    # ── AI Fields ─────────────────────────────────────────────────────────────
    # Feature 2 — Trust Score
    trust_info = EmbeddedDocumentField(TrustInfo, default=TrustInfo)

    # Feature 3 — AI Price Estimator
    market_price  = IntField(default=0)
    price_verdict = StringField(
        choices=['fair', 'overpriced', 'underpriced', 'unknown'],
        default='unknown'
    )
    price_diff_pct = FloatField(default=0.0)    # +30 = 30% overpriced

    # Feature 5 — Environment Score
    environment_score = EmbeddedDocumentField(EnvironmentScore, default=EnvironmentScore)

    # Feature 7 — Scam Detection
    is_scam_flagged = BooleanField(default=False)
    scam_risk_score = IntField(default=0)
    scam_reasons    = ListField(StringField())

    # ── Status & Meta ─────────────────────────────────────────────────────────
    is_available  = BooleanField(default=True)
    is_featured   = BooleanField(default=False)
    views_count   = IntField(default=0)
    saves_count   = IntField(default=0)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    available_from = DateTimeField()

    meta = {
        'collection': 'listings',
        'indexes': [
            'owner',
            'rent',
            'listing_type',
            'rental_period',
            'is_available',
            'is_scam_flagged',
            'is_featured',
            ('location.city', 'listing_type'),
            ('location.city', 'location.locality'),
            ('is_available', '-created_at'),
            ('is_available', 'rent'),
        ],
        'ordering': ['-created_at'],
    }

    def get_absolute_url(self):
        return f'/listing/{self.id}/'

    def get_main_photo(self):
        if self.photos:
            return self.photos[0]
        return '/static/images/placeholder.jpg'

    def get_price_display(self):
        return f'₹{self.rent:,}/mo'

    def compute_trust_score(self):
        """Recompute trust info score from its components."""
        if not self.trust_info:
            self.trust_info = TrustInfo()
        score = 0
        if self.trust_info.id_verified:       score += 40
        if self.trust_info.bill_uploaded:     score += 25
        if self.trust_info.video_walkthrough: score += 20
        score += min(15, self.trust_info.reviews_count * 3)
        self.trust_info.score = min(100, score)
        return self.trust_info.score

    def __str__(self):
        return f'{self.title} — ₹{self.rent:,}/mo'


# ══════════════════════════════════════════════════════════════════════════════
# REVIEW DOCUMENT
# One review per tenant per listing
# ══════════════════════════════════════════════════════════════════════════════

class Review(Document):
    """
    Tenant review of a listing.
    Affects listing's trust_info.avg_rating and trust score.
    """
    from apps.accounts.models import User

    listing    = ReferenceField(Listing,  required=True)
    reviewer   = ReferenceField(User,     required=True)
    rating     = IntField(required=True, min_value=1, max_value=5)
    comment    = StringField(max_length=1000)

    # Sub-ratings
    cleanliness_rating  = IntField(min_value=1, max_value=5)
    owner_rating        = IntField(min_value=1, max_value=5)
    value_rating        = IntField(min_value=1, max_value=5)
    location_rating     = IntField(min_value=1, max_value=5)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'reviews',
        'indexes': [
            'listing',
            'reviewer',
            ('listing', 'reviewer'),    # one review per tenant per listing
        ],
        'ordering': ['-created_at'],
    }


# ══════════════════════════════════════════════════════════════════════════════
# MARKET PRICE DATA (Feature 3 — AI Price Estimator)
# Stores average rents by city/locality/type/bedrooms
# ══════════════════════════════════════════════════════════════════════════════

class MarketPriceData(Document):
    """
    Aggregated market rent data used by the AI Price Estimator.
    Populated from Kaggle datasets / scraping / manual entry.
    """
    city         = StringField(required=True)
    locality     = StringField(required=True)
    listing_type = StringField(required=True)
    bedrooms     = IntField(default=1)
    avg_rent     = IntField(required=True)
    min_rent     = IntField()
    max_rent     = IntField()
    data_points  = IntField(default=0)    # how many listings this is based on
    updated_at   = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'market_prices',
        'indexes': [
            ('city', 'locality', 'listing_type', 'bedrooms'),
        ],
    }


# ══════════════════════════════════════════════════════════════════════════════
# ROOMMATE PROFILE (Feature 1 — AI Roommate Matching)
# ══════════════════════════════════════════════════════════════════════════════

class RoommateProfile(Document):
    """
    Lifestyle preferences used for AI roommate matching.
    One profile per user — upserted via the questionnaire.
    """
    from apps.accounts.models import User
    user = ReferenceField(User, required=True, unique=True)

    # Budget
    budget_min = IntField(required=True, min_value=0)
    budget_max = IntField(required=True, min_value=0)

    # Location preference
    city     = StringField(required=True)
    locality = StringField()

    # Lifestyle
    sleep_schedule   = StringField(
        choices=['early_bird', 'night_owl', 'flexible'],
        default='flexible'
    )
    smoking          = BooleanField(default=False)
    drinking         = BooleanField(default=False)
    pets             = BooleanField(default=False)
    cleanliness      = IntField(min_value=1, max_value=5, default=3)
    guests_frequency = StringField(
        choices=['never', 'rarely', 'sometimes', 'often'],
        default='rarely'
    )
    work_schedule    = StringField(
        choices=['day_shift', 'night_shift', 'wfh', 'student'],
        default='day_shift'
    )
    diet             = StringField(
        choices=['veg', 'non_veg', 'vegan', 'any'],
        default='any'
    )
    gender_pref      = StringField(
        choices=['any', 'male', 'female'],
        default='any'
    )

    # Personal info
    about      = StringField(max_length=500)
    profession = StringField(max_length=100)
    age        = IntField(min_value=18, max_value=80)
    gender     = StringField(choices=['male', 'female', 'other'])

    is_looking = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'roommate_profiles',
        'indexes': [
            'user',
            'city',
            'is_looking',
            ('city', 'is_looking'),
        ],
    }


# ══════════════════════════════════════════════════════════════════════════════
# ROOMMATE MATCH (Feature 1 — Store Match Results)
# ══════════════════════════════════════════════════════════════════════════════

class RoommateMatch(Document):
    from apps.accounts.models import User
    user_a        = ReferenceField(User)
    user_b        = ReferenceField(User)
    score         = FloatField(default=0.0)
    status        = StringField(
        choices=['pending', 'accepted', 'declined'],
        default='pending'
    )
    created_at    = DateTimeField(default=datetime.utcnow)
    responded_at  = DateTimeField()

    meta = {
        'collection': 'roommate_matches',
        'indexes': [
            'user_a',
            'user_b',
            'status',
        ]
    }


# ══════════════════════════════════════════════════════════════════════════════
# CHAT ROOM + MESSAGES (Feature 10 — Negotiation Chat)
# ══════════════════════════════════════════════════════════════════════════════

class Message(EmbeddedDocument):
    """
    One chat message embedded inside ChatRoom.
    msg_type controls how it renders in the UI:
      text    → normal bubble
      offer   → yellow offer card
      counter → blue counter card
      deal    → green deal banner
    """
    sender_id = StringField(required=True)    # MongoDB User ID as string
    content   = StringField(required=True, max_length=1000)
    msg_type  = StringField(
        choices=['text', 'offer', 'counter', 'deal'],
        default='text'
    )
    offer_amt = IntField()                    # filled for offer/counter/deal types
    timestamp = DateTimeField(default=datetime.utcnow)
    is_read   = BooleanField(default=False)


class ChatRoom(Document):
    """
    One chat room per (listing, tenant) pair.
    Contains all messages and the negotiation state.
    """
    from apps.accounts.models import User
    listing     = ReferenceField(Listing, required=True)
    tenant      = ReferenceField(User, required=True)
    owner       = ReferenceField(User, required=True)
    messages    = EmbeddedDocumentListField(Message)
    agreed_rent = IntField()        # set when deal type message is sent
    status      = StringField(
        choices=['active', 'deal_done', 'closed'],
        default='active'
    )
    last_message_at = DateTimeField(default=datetime.utcnow)
    created_at      = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'chat_rooms',
        'indexes': [
            'listing',
            'tenant',
            'owner',
            ('listing', 'tenant'),    # unique chat per listing-tenant pair
        ],
        'ordering': ['-last_message_at'],
    }

    def get_unread_count(self, user_id: str) -> int:
        """Count unread messages for a specific user."""
        return sum(
            1 for m in self.messages
            if not m.is_read and m.sender_id != user_id
        )

    def get_last_message(self):
        if self.messages:
            return self.messages[-1]
        return None


# ══════════════════════════════════════════════════════════════════════════════
# RENTAL AGREEMENT (Feature 9 — PDF Generator)
# ══════════════════════════════════════════════════════════════════════════════

class RentalAgreement(Document):
    """
    Stores agreement details and tracks e-signature status.
    PDF is generated by ml/agreement_generator.py and stored in /media/agreements/
    """
    from apps.accounts.models import User
    listing  = ReferenceField(Listing, required=True)
    tenant   = ReferenceField(User,    required=True)
    owner    = ReferenceField(User,    required=True)

    # Financial terms
    rent             = IntField(required=True)
    deposit          = IntField(default=0)
    maintenance      = IntField(default=0)
    duration_months  = IntField(required=True)
    start_date       = DateTimeField(required=True)
    end_date         = DateTimeField(required=True)

    # Addresses (filled in agreement form)
    tenant_address = StringField(max_length=500)
    owner_address  = StringField(max_length=500)

    # Custom clauses added by owner/tenant
    custom_terms = ListField(StringField())

    # PDF
    pdf_url = StringField()    # /media/agreements/agreement_<id>.pdf

    # E-signature (Feature 9)
    tenant_signed    = BooleanField(default=False)
    owner_signed     = BooleanField(default=False)
    tenant_signed_at = DateTimeField()
    owner_signed_at  = DateTimeField()

    # Status flow: draft → pending → active → expired
    status = StringField(
        choices=['draft', 'pending', 'active', 'expired'],
        default='draft'
    )

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'agreements',
        'indexes': [
            'listing',
            'tenant',
            'owner',
            'status',
        ],
        'ordering': ['-created_at'],
    }

    def both_signed(self):
        return self.tenant_signed and self.owner_signed

    def __str__(self):
        return f'Agreement: {self.tenant} @ {self.listing.title}'


# ══════════════════════════════════════════════════════════════════════════════
# SAVED LISTING (Wishlist)
# ══════════════════════════════════════════════════════════════════════════════

class SavedListing(Document):
    """
    Allows tenants to save/bookmark listings.
    """
    from apps.accounts.models import User
    user       = ReferenceField(User,    required=True)
    listing    = ReferenceField(Listing, required=True)
    saved_at   = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'saved_listings',
        'indexes': [
            ('user', 'listing'),
        ],
    }