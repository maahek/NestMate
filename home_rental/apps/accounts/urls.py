"""
NestMate — Accounts URL Configuration
All URLs are prefixed with /accounts/ from main urls.py
"""

from django.urls import path
from apps.accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    UploadVerificationView,
    ChangePasswordView,
    PublicProfileView,
)

urlpatterns = [

    # ── Auth ──────────────────────────────────────────────────────────────────
    path('register/',   RegisterView.as_view(),  name='register'),
    path('login/',      LoginView.as_view(),      name='login'),
    path('logout/',     LogoutView.as_view(),     name='logout'),

    # ── Profile ───────────────────────────────────────────────────────────────
    # /accounts/profile/               → view & edit your own profile
    path('profile/',    ProfileView.as_view(),    name='profile'),

    # /accounts/profile/<user_id>/     → view someone else's public profile
    path('profile/<str:user_id>/',
         PublicProfileView.as_view(),
         name='public_profile'),

    # ── Verification (Feature 2 — Trust Score) ────────────────────────────────
    # /accounts/verify/    → upload ID / utility bill
    path('verify/',
         UploadVerificationView.as_view(),
         name='upload_verification'),

    # ── Password ──────────────────────────────────────────────────────────────
    # /accounts/change-password/
    path('change-password/',
         ChangePasswordView.as_view(),
         name='change_password'),
]