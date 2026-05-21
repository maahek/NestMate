"""
NestMate - Django Settings
Database: MongoDB via MongoEngine
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# ── Installed Apps ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    # Third party
    'rest_framework',
    'corsheaders',
    'channels',

    # Our apps — using AppConfig for proper loading
    'apps.accounts.apps.AccountsConfig',
    'apps.listings.apps.ListingsConfig',
    'apps.roommate.apps.RoommateConfig',
    'apps.chat.apps.ChatConfig',
    'apps.agreements.apps.AgreementsConfig',
    'apps.analytics.apps.AnalyticsConfig',
]


# ── Middleware ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',    # ← must be here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ── URL & WSGI ────────────────────────────────────────────────────────────────
ROOT_URLCONF = 'home_rental.urls'
WSGI_APPLICATION = 'home_rental.wsgi.application'
ASGI_APPLICATION = 'home_rental.asgi.application'

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ── MongoDB (Primary Database) ────────────────────────────────────────────────
import mongoengine

MONGO_URI = os.getenv('MONGO_URI', '')
MONGO_DB  = os.getenv('MONGO_DB', 'nestmate')

if MONGO_URI:
    # Atlas connection
    mongoengine.connect(
        host = MONGO_URI,
        db   = MONGO_DB,
        uuidRepresentation = 'standard',
    )
    MONGODB_SETTINGS = {
        'db':   MONGO_DB,
        'host': MONGO_URI,
    }
else:
    # Local MongoDB fallback
    mongoengine.connect(
        db   = MONGO_DB,
        host = os.getenv('MONGO_HOST', 'localhost'),
        port = int(os.getenv('MONGO_PORT', 27017)),
        uuidRepresentation = 'standard',
    )
    MONGODB_SETTINGS = {
        'db':   MONGO_DB,
        'host': os.getenv('MONGO_HOST', 'localhost'),
        'port': int(os.getenv('MONGO_PORT', 27017)),
    }

# ── SQLite (Only for Django admin, sessions, auth) ────────────────────────────
# All real app data goes to MongoDB above
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Password Validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Static & Media Files ──────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS  = True
CORS_ALLOW_ALL_ORIGINS  = False

# ── CSRF ──────────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CSRF_COOKIE_SAMESITE  = 'Lax'
CSRF_COOKIE_HTTPONLY  = False      # React MUST be able to read this
CSRF_COOKIE_SECURE    = False      # False for localhost http
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE   = False

# ── Django Channels (WebSocket for Chat) ──────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ── Email Configuration ───────────────────────────────────────────────────────
EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST       = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT       = 587
EMAIL_USE_TLS    = True
EMAIL_HOST_USER  = os.getenv('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.getenv('EMAIL_USER', 'noreply@nestmate.in')

# ── Google Maps ───────────────────────────────────────────────────────────────
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

# ── AI / ML Settings ──────────────────────────────────────────────────────────

# Roommate matching feature weights (must sum to 1.0)
ROOMMATE_MATCH_WEIGHTS = {
    'budget':           0.25,
    'sleep_schedule':   0.18,
    'smoking':          0.15,
    'pets':             0.10,
    'cleanliness':      0.10,
    'guests_frequency': 0.08,
    'work_schedule':    0.07,
    'diet':             0.07,
}

# Scam detection thresholds
SCAM_PRICE_THRESHOLD = 0.40   # 40% below market = suspicious
SCAM_TRUST_MINIMUM   = 40     # trust score below this + low price = scam flag

# Trust score points breakdown
TRUST_SCORE_WEIGHTS = {
    'id_verified':       40,
    'bill_uploaded':     25,
    'video_walkthrough': 20,
    'per_review':         3,   # +3 per review, max 15
    'max_reviews_bonus': 15,
}

# ── Localization ──────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

# ── Default Primary Key ───────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Login / Logout Redirects ──────────────────────────────────────────────────
LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ── Session ───────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE     = 60 * 60 * 24 * 30   # 30 days
SESSION_SAVE_EVERY_REQUEST = True

# ── File Upload Limits ────────────────────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB

# ── Production Settings ────────────────────────────────────────────────────────
import os

if os.getenv('RENDER') or not DEBUG:

    # Security
    ALLOWED_HOSTS = [
        '.onrender.com',
        'localhost',
        '127.0.0.1',
    ]

    # CORS — allow your Vercel frontend
    CORS_ALLOWED_ORIGINS = [
        os.getenv('FRONTEND_URL', ''),
    ]
    CORS_ALLOW_CREDENTIALS = True

    CSRF_TRUSTED_ORIGINS = [
        os.getenv('FRONTEND_URL', ''),
        'https://*.onrender.com',
    ]

    # Static files with WhiteNoise
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = BASE_DIR / 'staticfiles'