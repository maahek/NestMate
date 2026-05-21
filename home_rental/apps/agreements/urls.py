"""
NestMate — Agreements URL Configuration
All URLs prefixed with /agreements/ from main urls.py

Full URL list:

  GET  /agreements/                           → List all my agreements
  GET  /agreements/create/<listing_id>/       → Agreement creation form
  POST /agreements/create/<listing_id>/       → Save + generate PDF
  GET  /agreements/<agreement_id>/            → Agreement detail + sign buttons
  GET  /agreements/<agreement_id>/download/   → Download PDF (attachment)
  GET  /agreements/<agreement_id>/view/       → View PDF in browser (inline)
  POST /agreements/<agreement_id>/sign/       → E-sign as tenant or owner
  POST /agreements/<agreement_id>/regenerate/ → Force-regenerate PDF
  POST /agreements/<agreement_id>/delete/     → Delete draft agreement
  GET  /agreements/<agreement_id>/status/     → Agreement status as JSON (AJAX)
"""

from django.urls import path
from apps.agreements.views import (
    AgreementListView,
    CreateAgreementView,
    AgreementDetailView,
    DownloadAgreementView,
    ViewAgreementPDFView,
    SignAgreementView,
    RegeneratePDFView,
    DeleteAgreementView,
    agreement_status_api,
)

urlpatterns = [
    path('', AgreementListView.as_view(), name='agreement_list'),
    path('create/<str:listing_id>/', CreateAgreementView.as_view(), name='create_agreement'),
    path('<str:agreement_id>/', AgreementDetailView.as_view(), name='agreement_detail'),
    path('<str:agreement_id>/download/', DownloadAgreementView.as_view(), name='download_agreement'),
    path('<str:agreement_id>/view/', ViewAgreementPDFView.as_view(), name='view_agreement_pdf'),
    path('<str:agreement_id>/sign/', SignAgreementView.as_view(), name='sign_agreement'),
    path('<str:agreement_id>/regenerate/', RegeneratePDFView.as_view(), name='regenerate_pdf'),
    path('<str:agreement_id>/delete/', DeleteAgreementView.as_view(), name='delete_agreement'),
    path('<str:agreement_id>/status/', agreement_status_api, name='agreement_status_api'),
]