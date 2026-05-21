"""
NestMate — Accounts Models
All user-related MongoDB documents live here.
"""

from mongoengine import (
    Document, EmbeddedDocument,
    StringField, BooleanField, IntField,
    EmailField, DateTimeField,
    EmbeddedDocumentListField
)
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# EMBEDDED: VERIFICATION DOCUMENT
# Stored inside User document (not a separate collection)
# ══════════════════════════════════════════════════════════════════════════════

class VerificationDocument(EmbeddedDocument):
    """
    Represents one uploaded verification file.
    Example: Aadhaar card, electricity bill, passport.

    Stored as embedded list inside User.
    """
    doc_type = StringField(
        required=True,
        choices=['aadhaar', 'pan', 'passport', 'driving_license', 'electricity_bill', 'water_bill']
    )
    file_url    = StringField(required=True)      # path inside /media/verification/
    verified    = BooleanField(default=False)      # admin manually marks True
    uploaded_at = DateTimeField(default=datetime.utcnow)
    verified_at = DateTimeField()                  # set when admin approves
    notes       = StringField(max_length=300)      # admin notes


# ══════════════════════════════════════════════════════════════════════════════
# MAIN: USER DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════

class User(Document):
    """
    Main user document stored in MongoDB 'users' collection.

    Roles:
      - tenant : looking to rent
      - owner  : listing properties
      - both   : doing both
    """

    # ── Basic Info ────────────────────────────────────────────────────────────
    username    = StringField(required=True, unique=True, max_length=50)
    email       = EmailField(required=True, unique=True)
    password    = StringField(required=True)          # bcrypt hashed
    full_name   = StringField(max_length=100)
    phone       = StringField(max_length=15)
    avatar_url  = StringField(default='')
    bio         = StringField(max_length=500)

    # ── Role ──────────────────────────────────────────────────────────────────
    role = StringField(
        choices=['tenant', 'owner', 'both'],
        default='tenant'
    )

    # ── Location ──────────────────────────────────────────────────────────────
    city     = StringField(max_length=100)
    locality = StringField(max_length=100)

    # ── Verification (Feature 2 — Trust Score) ────────────────────────────────
    id_verified       = BooleanField(default=False)   # True when admin approves ID
    bill_verified     = BooleanField(default=False)   # True when bill is approved
    verification_docs = EmbeddedDocumentListField(VerificationDocument)
    trust_score       = IntField(default=0, min_value=0, max_value=100)

    # ── Account Status ────────────────────────────────────────────────────────
    is_active     = BooleanField(default=True)
    is_admin      = BooleanField(default=False)
    email_verified = BooleanField(default=False)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at   = DateTimeField(default=datetime.utcnow)
    last_login   = DateTimeField()
    updated_at   = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'username',
            'city',
            'role',
        ],
        'ordering': ['-created_at'],
    }

    # ── Helper Methods ────────────────────────────────────────────────────────
    def get_full_name(self):
        return self.full_name or self.username

    def get_avatar(self):
        if self.avatar_url:
            return self.avatar_url
        # Return a default avatar based on first letter
        return f'/static/images/avatars/default.png'

    def compute_trust_score(self):
        """
        Recalculate trust score based on verification status.
        Call this whenever verification status changes.
        """
        score = 0
        if self.id_verified:    score += 40
        if self.bill_verified:  score += 25
        if self.email_verified: score += 10
        if self.phone:          score += 10
        if self.avatar_url:     score += 5
        if self.bio:            score += 5
        if self.full_name:      score += 5
        self.trust_score = min(100, score)
        return self.trust_score

    def account_age_days(self):
        return (datetime.utcnow() - self.created_at).days

    def __str__(self):
        return f'{self.username} ({self.email})'