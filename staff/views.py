from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Dorm, Room
from .serializers import DormListSerializer, RoomListSerializer
from students.models import MaintenanceRequest
from students.serializers import MaintenanceRequestListSerializer


class IsStaffMember(IsAuthenticated):
    """Permission class for staff members."""
    
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'staff'


# ==================== STAFF VIEWS ====================

class StaffDashboardView(APIView):
    """Staff dashboard."""
    
    permission_classes = [IsStaffMember]
    
    @extend_schema(tags=['staff'], summary='Staff Dashboard')
    def get(self, request):
        try:
            staff = request.user.staff_profile
        except:
            return Response({'success': False, 'error': 'Staff profile not found'}, status=404)
        
        # Get maintenance stats
        assigned_jobs = MaintenanceRequest.objects.filter(
            assigned_to=staff
        )
        
        stats = {
            'pending_jobs': assigned_jobs.filter(status='assigned_to_staff').count(),
            'in_progress_jobs': assigned_jobs.filter(status='in_progress').count(),
            'completed_jobs': assigned_jobs.filter(status='completed').count(),
            'available_jobs': MaintenanceRequest.objects.filter(status='approved_by_proctor').count(),
        }
        
        return Response({
            'success': True,
            'data': {
                'staff': {
                    'id': staff.id,
                    'full_name': staff.user.full_name,
                    'department': staff.department,
                    'position': staff.position,
                },
                'stats': stats,
            }
        })


class StaffMaintenanceListView(APIView):
    """List available maintenance jobs for staff."""
    
    permission_classes = [IsStaffMember]
    
    @extend_schema(tags=['staff'], summary='List Available Maintenance Jobs')
    def get(self, request):
        # Get jobs approved by proctor (available for staff to accept)
        jobs = MaintenanceRequest.objects.filter(
            status='approved_by_proctor'
        ).order_by('-urgency', '-reported_date')
        
        serializer = MaintenanceRequestListSerializer(jobs, many=True)
        
        return Response({
            'success': True,
            'data': {'jobs': serializer.data}
        })


class StaffMyJobsView(APIView):
    """List staff's assigned jobs."""
    
    permission_classes = [IsStaffMember]
    
    @extend_schema(tags=['staff'], summary='List My Assigned Jobs')
    def get(self, request):
        try:
            staff = request.user.staff_profile
        except:
            return Response({'success': False, 'error': 'Staff profile not found'}, status=404)
        
        jobs = MaintenanceRequest.objects.filter(
            assigned_to=staff,
            status__in=['assigned_to_staff', 'in_progress']
        ).order_by('-urgency', '-assigned_date')
        
        serializer = MaintenanceRequestListSerializer(jobs, many=True)
        
        return Response({
            'success': True,
            'data': {'jobs': serializer.data}
        })


class StaffMaintenanceAcceptView(APIView):
    """Accept a maintenance job."""
    
    permission_classes = [IsStaffMember]
    
    @extend_schema(tags=['staff'], summary='Accept Maintenance Job')
    def put(self, request, pk):
        try:
            maintenance = MaintenanceRequest.objects.get(pk=pk, status='approved_by_proctor')
        except MaintenanceRequest.DoesNotExist:
            return Response({'success': False, 'error': 'Job not found or not available'}, status=404)
        
        try:
            staff = request.user.staff_profile
        except:
            return Response({'success': False, 'error': 'Staff profile not found'}, status=404)
        
        maintenance.status = 'assigned_to_staff'
        maintenance.assigned_to = staff
        maintenance.assigned_date = timezone.now()
        maintenance.save()
        
        return Response({
            'success': True,
            'message': 'Job accepted',
            'data': {'status': maintenance.status}
        })


class StaffMaintenanceStartView(APIView):
    """Start working on a maintenance job."""
    
    permission_classes = [IsStaffMember]
    
    @extend_schema(tags=['staff'], summary='Start Maintenance Job')
    def put(self, request, pk):
        try:
            staff = request.user.staff_profile
            maintenance = MaintenanceRequest.objects.get(pk=pk, assigned_to=staff)
        except MaintenanceRequest.DoesNotExist:
            return Response({'success': False, 'error': 'Job not found'}, status=404)
        except:
            return Response({'success': False, 'error': 'Staff profile not found'}, status=404)
        
        maintenance.status = 'in_progress'
        maintenance.started_date = timezone.now()
        maintenance.save()
        
        return Response({
            'success': True,
            'message': 'Job started',
            'data': {'status': maintenance.status}
        })


class StaffMaintenanceCompleteView(APIView):
    """Complete a maintenance job."""
    
    permission_classes = [IsStaffMember]
    
    @extend_schema(tags=['staff'], summary='Complete Maintenance Job')
    def put(self, request, pk):
        try:
            staff = request.user.staff_profile
            maintenance = MaintenanceRequest.objects.get(pk=pk, assigned_to=staff)
        except MaintenanceRequest.DoesNotExist:
            return Response({'success': False, 'error': 'Job not found'}, status=404)
        except:
            return Response({'success': False, 'error': 'Staff profile not found'}, status=404)
        
        maintenance.status = 'completed'
        maintenance.completed_date = timezone.now()
        maintenance.save()
        
        return Response({
            'success': True,
            'message': 'Job completed',
            'data': {'status': maintenance.status}
        })


# ==================== DORM & ROOM VIEWS ====================

class DormListView(APIView):
    """List all dorms."""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(tags=['dorms'], summary='List Dorms')
    def get(self, request):
        dorms = Dorm.objects.filter(status='active').order_by('name')
        serializer = DormListSerializer(dorms, many=True)
        
        return Response({
            'success': True,
            'data': {'dorms': serializer.data}
        })


class DormRoomsView(APIView):
    """List rooms in a dorm."""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(tags=['rooms'], summary='List Rooms in Dorm')
    def get(self, request, dorm_id):
        try:
            dorm = Dorm.objects.get(pk=dorm_id)
        except Dorm.DoesNotExist:
            return Response({'success': False, 'error': 'Dorm not found'}, status=404)
        
        rooms = Room.objects.filter(dorm=dorm).order_by('floor', 'room_number')
        serializer = RoomListSerializer(rooms, many=True)
        
        return Response({
            'success': True,
            'data': {
                'dorm': DormListSerializer(dorm).data,
                'rooms': serializer.data
            }
        })


class AvailableRoomsView(APIView):
    """List available rooms."""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(tags=['rooms'], summary='List Available Rooms')
    def get(self, request):
        rooms = Room.objects.filter(
            status='available'
        ).select_related('dorm').order_by('dorm__name', 'floor', 'room_number')
        
        serializer = RoomListSerializer(rooms, many=True)
        
        return Response({
            'success': True,
            'data': {'rooms': serializer.data}
        })
