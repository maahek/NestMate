"""
NestMate — Roommate Matching URL Configuration
All URLs prefixed with /roommate/ from main urls.py

Full URL list:
  /roommate/                          → Landing page
  /roommate/quiz/                     → Questionnaire (4 steps)
  /roommate/matches/                  → AI match results
  /roommate/profile/<user_id>/        → View another user's profile
  /roommate/connect/<user_id>/        → Send connection request (POST)
  /roommate/respond/<match_id>/       → Accept / reject request (POST)
  /roommate/requests/                 → Inbox: received & sent requests
  /roommate/toggle-looking/           → Toggle active/hidden status (POST)
  /roommate/delete-profile/           → Delete roommate profile (POST)
"""

from django.urls import path
from apps.roommate.views import (
    RoommateHomeView,
    RoommateQuestionnaireView,
    RoommateMatchesView,
    SendConnectRequestView,
    RespondToRequestView,
    RoommateRequestsView,
    ToggleLookingView,
)

urlpatterns = [
    path('',                              RoommateHomeView.as_view(),         name='roommate_home'),
    path('quiz/',                         RoommateQuestionnaireView.as_view(),name='roommate_questionnaire'),
    path('matches/',                      RoommateMatchesView.as_view(),      name='roommate_matches'),
    path('connect/<str:user_id>/',        SendConnectRequestView.as_view(),   name='send_connect_request'),
    path('respond/<str:match_id>/',       RespondToRequestView.as_view(),     name='respond_to_request'),
    path('requests/',                     RoommateRequestsView.as_view(),     name='roommate_requests'),
    path('toggle-looking/',              ToggleLookingView.as_view(),         name='toggle_looking'),
]