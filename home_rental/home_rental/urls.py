"""
NestMate — Master URL Configuration
Every app's URLs are included here.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.middleware.csrf import get_token

def csrf_view(request):
    """Endpoint that sets the CSRF cookie so React can read it."""
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

urlpatterns = [

    # ── Django Admin ──────────────────────────────────────────────────────────
    path('admin/', admin.site.urls),
    path('api/csrf/', csrf_view, name='csrf'),

    # ── Main Pages ────────────────────────────────────────────────────────────
    # Home, Search, Map, Listing Detail, Create Listing
    path('', include('apps.listings.urls')),

    # ── Accounts ──────────────────────────────────────────────────────────────
    # Register, Login, Logout, Profile, ID Verification
    path('accounts/', include('apps.accounts.urls')),

    # ── Roommate Matching ─────────────────────────────────────────────────────
    # /roommate/        → landing page
    # /roommate/quiz/   → personality questionnaire
    # /roommate/matches → AI match results
    path('roommate/', include('apps.roommate.urls')),

    # ── Chat & Negotiation ────────────────────────────────────────────────────
    # /chat/             → all chat rooms
    # /chat/<room_id>/   → specific chat room
    # /chat/start/<listing_id>/ → start new chat
    path('chat/', include('apps.chat.urls')),

    # ── Rental Agreements ─────────────────────────────────────────────────────
    # /agreements/create/<listing_id>/   → create agreement
    # /agreements/download/<id>/         → download PDF
    # /agreements/sign/<id>/             → e-sign
    path('agreements/', include('apps.agreements.urls')),

    # ── Analytics & Market Data ───────────────────────────────────────────────
    # /analytics/market/      → market price data
    # /analytics/environment/ → environment scores
    path('analytics/', include('apps.analytics.urls')),

    # ── REST API Endpoints (JSON) ─────────────────────────────────────────────
    # Used by Leaflet map and AJAX price checker
    path('api/listings/', include('apps.listings.api_urls')),
    path('api/roommate/', include('apps.roommate.api_urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  # ↑ Serves uploaded files (photos, PDFs) in development