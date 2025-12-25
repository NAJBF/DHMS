"""
URL configuration for dhms_api project.
Dorm and Hostel Management System API
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('aau-dhms-api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('aau-dhms-api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('aau-dhms-api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('aau-dhms-api/', include('accounts.urls')),       # /api/auth/...
    path('aau-dhms-api/', include('students.urls')),       # /api/students/..., /api/proctors/...
    path('aau-dhms-api/', include('staff.urls')),          # /api/staff/..., /api/dorms/..., /api/rooms/...
    path('aau-dhms-api/', include('operations.urls')),     # /api/security/...
]
