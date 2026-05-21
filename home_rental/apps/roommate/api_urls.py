"""
NestMate — Roommate Matching REST API URLs
Prefix: /api/roommate/ from main urls.py

Used by:
  - AJAX compatibility widget on profile pages
  - Live score update when editing questionnaire
  - External mobile app integrations

Full API URL list:
  GET  /api/roommate/matches/                 → top matches for logged-in user
  GET  /api/roommate/compare/<user_id>/       → compare me vs one user
  GET  /api/roommate/profiles/               → browse all active profiles
  GET  /api/roommate/profile/<user_id>/      → one user's profile (JSON)
  GET  /api/roommate/profile/me/            → current user's roommate profile
  POST /api/roommate/profile/me/           → save/update current roommate profile
  POST /api/roommate/score/                 → score two raw dicts (no auth)
  GET  /api/roommate/city-stats/             → seekers per city
"""

from django.urls import path
from apps.roommate.api_views import (
    MyProfileView,
    MatchesAPIView,
    ProfilesAPIView,
    ProfileDetailAPIView,
    ScoreAPIView,
    CityStatsAPIView,
    CompareAPIView,
)

urlpatterns = [
    path('profile/me/',              MyProfileView.as_view(),       name='api_my_profile'),
    path('matches/',                 MatchesAPIView.as_view(),      name='api_roommate_matches'),
    path('profiles/',                ProfilesAPIView.as_view(),     name='api_roommate_profiles'),
    path('profile/<str:user_id>/',   ProfileDetailAPIView.as_view(),name='api_roommate_profile'),
    path('score/',                   ScoreAPIView.as_view(),        name='api_roommate_score'),
    path('city-stats/',              CityStatsAPIView.as_view(),    name='api_roommate_city_stats'),
    path('compare/<str:user_id>/',   CompareAPIView.as_view(),      name='api_roommate_compare'),
]