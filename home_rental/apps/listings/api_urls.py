"""
NestMate — Listings REST API URLs
Prefix: /api/listings/ from main urls.py
"""

from django.urls import path
from apps.listings.api_views import (
    ListingsAPIView,
    ListingDetailAPIView,
    CreateListingAPIView,
    PriceCheckAPIView,
    ScamCheckAPIView,
    NearbyListingsAPIView,
    MarketDataAPIView,
)

urlpatterns = [

    # GET  /api/listings/        → search listings
    # POST /api/listings/        → create listing
    path(
        '',
        ListingsAPIView.as_view(),
        name='api_listings'
    ),

    # POST /api/listings/create/ → create listing (explicit)
    path(
        'create/',
        CreateListingAPIView.as_view(),
        name='api_create_listing'
    ),

    # GET /api/listings/price-check/
    path(
        'price-check/',
        PriceCheckAPIView.as_view(),
        name='api_price_check'
    ),

    # GET /api/listings/nearby/
    path(
        'nearby/',
        NearbyListingsAPIView.as_view(),
        name='api_nearby'
    ),

    # GET /api/listings/market-data/
    path(
        'market-data/',
        MarketDataAPIView.as_view(),
        name='api_market_data'
    ),

    # GET /api/listings/scam-check/<id>/
    path(
        'scam-check/<str:listing_id>/',
        ScamCheckAPIView.as_view(),
        name='api_scam_check'
    ),

    # GET /api/listings/<id>/
    path(
        '<str:listing_id>/',
        ListingDetailAPIView.as_view(),
        name='api_listing_detail'
    ),
]