"""
NestMate — Listings URL Configuration
Prefix: / (root) from main urls.py
"""

from django.urls import path
from apps.listings.views import (
    HomeView,
    SearchView,
    MapSearchView,
    ListingDetailView,
    CreateListingView,
    EditListingView,
    DeleteListingView,
    toggle_save_listing,
    submit_review,
)

urlpatterns = [

    # ── Home Page ──────────────────────────────────────────────────────────────
    # /
    path('', HomeView.as_view(), name='home'),

    # ── Search ─────────────────────────────────────────────────────────────────
    # /search/?city=Mumbai&type=apartment&max_rent=20000&trust_min=80
    path('search/', SearchView.as_view(), name='search'),

    # ── Map Search (Feature 4) ──────────────────────────────────────────────────
    # /map/?city=Bangalore
    path('map/', MapSearchView.as_view(), name='map_search'),

    # ── Listing Detail ─────────────────────────────────────────────────────────
    # /listing/<listing_id>/
    path(
        'listing/<str:listing_id>/',
        ListingDetailView.as_view(),
        name='listing_detail'
    ),

    # ── Create Listing ─────────────────────────────────────────────────────────
    # /listing/create/  (login required)
    path(
        'listing/create/',
        CreateListingView.as_view(),
        name='create_listing'
    ),

    # ── Edit Listing ───────────────────────────────────────────────────────────
    # /listing/<listing_id>/edit/  (owner only)
    path(
        'listing/<str:listing_id>/edit/',
        EditListingView.as_view(),
        name='edit_listing'
    ),

    # ── Delete Listing ─────────────────────────────────────────────────────────
    # /listing/<listing_id>/delete/  POST only (owner only)
    path(
        'listing/<str:listing_id>/delete/',
        DeleteListingView.as_view(),
        name='delete_listing'
    ),

    # ── Save / Unsave Listing (AJAX) ───────────────────────────────────────────
    # /listing/<listing_id>/save/  POST → returns JSON { saved: true/false }
    path(
        'listing/<str:listing_id>/save/',
        toggle_save_listing,
        name='toggle_save'
    ),

    # ── Submit Review ──────────────────────────────────────────────────────────
    # /listing/<listing_id>/review/  POST
    path(
        'listing/<str:listing_id>/review/',
        submit_review,
        name='submit_review'
    ),
]