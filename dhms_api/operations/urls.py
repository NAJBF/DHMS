from django.urls import path
from .views import (
    SecurityDashboardView,
    SecurityPendingLaundryView,
    SecurityVerifyLaundryView,
    SecurityLaundryTakenOutView,
    SecurityLaundryQRScanView,
    PublicLaundryTakenOutView,
    PublicLaundryStatusView,
)

app_name = 'operations'

urlpatterns = [
    # Security endpoints (authenticated)
    path('security/dashboard/', SecurityDashboardView.as_view(), name='security_dashboard'),
    path('security/laundry/pending/', SecurityPendingLaundryView.as_view(), name='security_pending_laundry'),
    path('security/laundry/<int:pk>/verify/', SecurityVerifyLaundryView.as_view(), name='security_verify_laundry'),
    path('security/laundry/<int:pk>/taken-out/', SecurityLaundryTakenOutView.as_view(), name='security_laundry_taken_out'),
    path('security/laundry/scan/', SecurityLaundryQRScanView.as_view(), name='security_laundry_scan'),
    
    # Public QR code endpoints (no authentication required)
    # QR Code should contain: {BASE_URL}/aau-dhms-api/public/laundry/{form_code}/taken/
    path('public/laundry/<str:form_code>/taken/', PublicLaundryTakenOutView.as_view(), name='public_laundry_taken'),
    path('public/laundry/<str:form_code>/status/', PublicLaundryStatusView.as_view(), name='public_laundry_status'),
]
