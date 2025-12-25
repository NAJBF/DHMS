from django.urls import path
from .views import (
    # Student views
    StudentDashboardView,
    StudentRoomView,
    StudentMaintenanceView,
    StudentLaundryView,
    StudentPenaltiesView,
    # Proctor views
    ProctorDashboardView,
    ProctorAssignRoomView,
    ProctorPendingMaintenanceView,
    ProctorMaintenanceApproveView,
    ProctorMaintenanceRejectView,
    ProctorPendingLaundryView,
    ProctorLaundryApproveView,
    ProctorLaundryRejectView,
    ProctorCreatePenaltyView,
    ProctorStudentsView,
)

app_name = 'students'

urlpatterns = [
    # Student endpoints
    path('students/dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('students/room/', StudentRoomView.as_view(), name='student_room'),
    path('students/maintenance/', StudentMaintenanceView.as_view(), name='student_maintenance'),
    path('students/laundry/', StudentLaundryView.as_view(), name='student_laundry'),
    path('students/penalties/', StudentPenaltiesView.as_view(), name='student_penalties'),
    
    # Proctor endpoints
    path('proctors/dashboard/', ProctorDashboardView.as_view(), name='proctor_dashboard'),
    path('proctors/assign-room/', ProctorAssignRoomView.as_view(), name='proctor_assign_room'),
    path('proctors/maintenance/pending/', ProctorPendingMaintenanceView.as_view(), name='proctor_pending_maintenance'),
    path('proctors/maintenance/<int:pk>/approve/', ProctorMaintenanceApproveView.as_view(), name='proctor_approve_maintenance'),
    path('proctors/maintenance/<int:pk>/reject/', ProctorMaintenanceRejectView.as_view(), name='proctor_reject_maintenance'),
    path('proctors/laundry/pending/', ProctorPendingLaundryView.as_view(), name='proctor_pending_laundry'),
    path('proctors/laundry/<int:pk>/approve/', ProctorLaundryApproveView.as_view(), name='proctor_approve_laundry'),
    path('proctors/laundry/<int:pk>/reject/', ProctorLaundryRejectView.as_view(), name='proctor_reject_laundry'),
    path('proctors/penalties/', ProctorCreatePenaltyView.as_view(), name='proctor_create_penalty'),
    path('proctors/students/', ProctorStudentsView.as_view(), name='proctor_students'),
]
