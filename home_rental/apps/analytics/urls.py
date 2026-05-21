"""
NestMate — Analytics URL Configuration
All URLs prefixed with /analytics/ from main urls.py

Full URL list:

  HTML Pages (public):
    GET /analytics/market/                → Market price dashboard
    GET /analytics/environment/           → Environment score dashboard
    GET /analytics/trust-leaderboard/     → Trust score leaderboard
    GET /analytics/city/<city>/           → City-level deep dive

  HTML Pages (admin only):
    GET  /analytics/platform/             → Platform stats dashboard
    GET  /analytics/scam/                 → Scam report dashboard
    POST /analytics/scam/                 → Admin unflag / remove action

  Admin Quick Actions (POST):
    POST /analytics/admin/listing/<id>/   → verify/unflag/feature/remove

  JSON APIs:
    GET /analytics/api/heatmap/           → Price heatmap coordinates
    GET /analytics/api/market-data/       → Market rent for a location
    GET /analytics/api/city-stats/        → Key stats per city
"""

from django.urls import path
from apps.analytics.views import (
    PlatformStatsView,
    MarketPriceView,
    EnvironmentScoreView,
    CityInsightsView,
    TrustLeaderboardView,
    ScamDashboardView,
    PriceHeatmapAPIView,
    MarketDataAPIView,
    CityStatsAPIView,
    AdminListingActionView,
)

urlpatterns = [
    path('market/', MarketPriceView.as_view(), name='market_price'),
    path('environment/', EnvironmentScoreView.as_view(), name='environment_score'),
    path('trust-leaderboard/', TrustLeaderboardView.as_view(), name='trust_leaderboard'),
    path('city/<str:city>/', CityInsightsView.as_view(), name='city_insights'),
    path('platform/', PlatformStatsView.as_view(), name='platform_stats'),
    path('scam/', ScamDashboardView.as_view(), name='scam_dashboard'),
    path('admin/listing/<str:listing_id>/', AdminListingActionView.as_view(), name='admin_listing_action'),
    path('api/heatmap/', PriceHeatmapAPIView.as_view(), name='api_price_heatmap'),
    path('api/market-data/', MarketDataAPIView.as_view(), name='api_market_data'),
    path('api/city-stats/', CityStatsAPIView.as_view(), name='api_city_stats'),
]