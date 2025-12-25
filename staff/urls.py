from django.urls import path
from .views import (
    # Staff views
    StaffDashboardView,
    StaffMaintenanceListView,
    StaffMyJobsView,
    StaffMaintenanceAcceptView,
    StaffMaintenanceStartView,
    StaffMaintenanceCompleteView,
    # Dorm & Room views
    DormListView,
    DormRoomsView,
    AvailableRoomsView,
)

app_name = 'staff'

urlpatterns = [
    # Staff endpoints
    path('staff/dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/maintenance/', StaffMaintenanceListView.as_view(), name='staff_maintenance_list'),
    path('staff/maintenance/my-jobs/', StaffMyJobsView.as_view(), name='staff_my_jobs'),
    path('staff/maintenance/<int:pk>/accept/', StaffMaintenanceAcceptView.as_view(), name='staff_accept_maintenance'),
    path('staff/maintenance/<int:pk>/start/', StaffMaintenanceStartView.as_view(), name='staff_start_maintenance'),
    path('staff/maintenance/<int:pk>/complete/', StaffMaintenanceCompleteView.as_view(), name='staff_complete_maintenance'),
    
    # Dorm & Room endpoints
    path('dorms/', DormListView.as_view(), name='dorm_list'),
    path('dorms/<int:dorm_id>/rooms/', DormRoomsView.as_view(), name='dorm_rooms'),
    path('rooms/available/', AvailableRoomsView.as_view(), name='available_rooms'),
]
