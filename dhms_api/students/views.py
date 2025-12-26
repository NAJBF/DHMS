from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import RoomAssignment, MaintenanceRequest, LaundryForm, Penalty
from .serializers import (
    RoomSerializer, RoommateSerializer, RoomAssignmentSerializer,
    MaintenanceRequestCreateSerializer, MaintenanceRequestListSerializer,
    LaundryFormCreateSerializer, LaundryFormListSerializer,
    PenaltySerializer, PenaltyCreateSerializer, RoomAssignmentCreateSerializer,
)
from accounts.models import Student
from staff.models import Room


from dhms_api.permissions import IsStudent, IsProctor


# ==================== STUDENT VIEWS ====================

class StudentDashboardView(APIView):
    """Student dashboard with room info and stats."""
    
    permission_classes = [IsStudent]
    
    @extend_schema(tags=['students'], summary='Student Dashboard')
    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'success': False, 'error': 'Student profile not found'}, status=404)
        
        # Get current room assignment
        assignment = RoomAssignment.objects.filter(
            student=student, status='active'
        ).select_related('room', 'room__dorm').first()
        
        room_data = None
        roommate_data = None
        
        if assignment:
            room = assignment.room
            room_data = {
                'id': room.id,
                'room_number': room.room_number,
                'dorm_name': room.dorm.name,
                'floor': room.floor,
                'check_in_date': assignment.check_in_date,
                'expected_check_out': assignment.expected_check_out,
            }
            
            # Get roommate
            roommate_assignment = RoomAssignment.objects.filter(
                room=room, status='active'
            ).exclude(student=student).select_related('student', 'student__user').first()
            
            if roommate_assignment:
                roommate_data = {
                    'id': roommate_assignment.student.id,
                    'full_name': roommate_assignment.student.user.full_name,
                    'student_code': roommate_assignment.student.student_code,
                }
                room_data['roommate'] = roommate_data
        
        # Get stats
        stats = {
            'active_penalties': Penalty.objects.filter(student=student, status='active').count(),
            'pending_maintenance': MaintenanceRequest.objects.filter(
                student=student, status__in=['pending_proctor', 'approved_by_proctor', 'assigned_to_staff', 'in_progress']
            ).count(),
            'pending_laundry': LaundryForm.objects.filter(
                student=student, status__in=['pending_proctor', 'approved_by_proctor']
            ).count(),
        }
        
        return Response({
            'success': True,
            'data': {
                'student': {
                    'id': student.id,
                    'student_code': student.student_code,
                    'full_name': student.user.full_name,
                    'email': student.user.email,
                    'phone': student.user.phone,
                    'student_type': student.student_type,
                    'academic_year': student.academic_year,
                    'department': student.department,
                },
                'room': room_data,
                'stats': stats,
            }
        })


class StudentRoomView(APIView):
    """Get student's room details and roommates."""
    
    permission_classes = [IsStudent]
    
    @extend_schema(tags=['students'], summary='Get Student Room')
    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'success': False, 'error': 'Student profile not found'}, status=404)
        
        assignment = RoomAssignment.objects.filter(
            student=student, status='active'
        ).select_related('room', 'room__dorm').first()
        
        if not assignment:
            return Response({'success': False, 'error': 'No active room assignment'}, status=404)
        
        room = assignment.room
        room_serializer = RoomSerializer(room)
        
        # Get all roommates
        roommate_assignments = RoomAssignment.objects.filter(
            room=room, status='active'
        ).select_related('student', 'student__user')
        
        roommates = [RoommateSerializer(a.student).data for a in roommate_assignments]
        
        return Response({
            'success': True,
            'data': {
                'room': room_serializer.data,
                'roommates': roommates,
            }
        })


class StudentMaintenanceView(APIView):
    """Handle student maintenance requests."""
    
    permission_classes = [IsStudent]
    
    @extend_schema(tags=['students'], summary='List Student Maintenance Requests')
    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'success': False, 'error': 'Student profile not found'}, status=404)
        
        requests = MaintenanceRequest.objects.filter(student=student).order_by('-reported_date')
        serializer = MaintenanceRequestListSerializer(requests, many=True)
        
        return Response({
            'success': True,
            'data': {'requests': serializer.data}
        })
    
    @extend_schema(tags=['students'], summary='Create Maintenance Request')
    def post(self, request):
        serializer = MaintenanceRequestCreateSerializer(
            data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            maintenance = serializer.save()
            return Response({
                'success': True,
                'message': 'Maintenance request submitted',
                'data': {
                    'id': maintenance.id,
                    'request_code': maintenance.request_code,
                    'status': maintenance.status,
                    'reported_date': maintenance.reported_date,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({'success': False, 'errors': serializer.errors}, status=400)


class StudentLaundryView(APIView):
    """Handle student laundry forms."""
    
    permission_classes = [IsStudent]
    
    @extend_schema(tags=['students'], summary='List Student Laundry Forms')
    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'success': False, 'error': 'Student profile not found'}, status=404)
        
        forms = LaundryForm.objects.filter(student=student).order_by('-submission_date')
        serializer = LaundryFormListSerializer(forms, many=True)
        
        return Response({
            'success': True,
            'data': {'forms': serializer.data}
        })
    
    @extend_schema(tags=['students'], summary='Create Laundry Form')
    def post(self, request):
        serializer = LaundryFormCreateSerializer(
            data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            form = serializer.save()
            return Response({
                'success': True,
                'message': 'Laundry form submitted',
                'data': {
                    'id': form.id,
                    'form_code': form.form_code,
                    'status': form.status,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({'success': False, 'errors': serializer.errors}, status=400)


class StudentPenaltiesView(APIView):
    """Get student's penalties."""
    
    permission_classes = [IsStudent]
    
    @extend_schema(tags=['students'], summary='List Student Penalties')
    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'success': False, 'error': 'Student profile not found'}, status=404)
        
        penalties = Penalty.objects.filter(student=student).order_by('-assigned_date')
        serializer = PenaltySerializer(penalties, many=True)
        
        return Response({
            'success': True,
            'data': {'penalties': serializer.data}
        })


# ==================== PROCTOR VIEWS ====================

class ProctorDashboardView(APIView):
    """Proctor dashboard with stats."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Proctor Dashboard')
    def get(self, request):
        try:
            proctor = request.user.proctor_profile
        except:
            return Response({'success': False, 'error': 'Proctor profile not found'}, status=404)
        
        # Get stats for the assigned dorm
        dorm = proctor.assigned_dorm
        
        if dorm:
            rooms = Room.objects.filter(dorm=dorm)
            pending_maintenance = MaintenanceRequest.objects.filter(
                room__in=rooms, status='pending_proctor'
            ).count()
            pending_laundry = LaundryForm.objects.filter(
                student__room_assignments__room__in=rooms,
                student__room_assignments__status='active',
                status='pending_proctor'
            ).distinct().count()
            active_penalties = Penalty.objects.filter(
                student__room_assignments__room__in=rooms,
                student__room_assignments__status='active',
                status='active'
            ).distinct().count()
        else:
            pending_maintenance = MaintenanceRequest.objects.filter(status='pending_proctor').count()
            pending_laundry = LaundryForm.objects.filter(status='pending_proctor').count()
            active_penalties = Penalty.objects.filter(status='active').count()
        
        return Response({
            'success': True,
            'data': {
                'proctor': {
                    'id': proctor.id,
                    'full_name': proctor.user.full_name,
                    'assigned_dorm': dorm.name if dorm else None,
                },
                'stats': {
                    'pending_maintenance': pending_maintenance,
                    'pending_laundry': pending_laundry,
                    'active_penalties': active_penalties,
                }
            }
        })


class ProctorAssignRoomView(APIView):
    """Assign room to student."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Assign Room to Student')
    def post(self, request):
        serializer = RoomAssignmentCreateSerializer(
            data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            assignment = serializer.save()
            return Response({
                'success': True,
                'message': 'Room assigned',
                'data': {
                    'assignment_id': assignment.id,
                    'status': assignment.status,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({'success': False, 'errors': serializer.errors}, status=400)


class ProctorPendingMaintenanceView(APIView):
    """Get pending maintenance requests for proctor."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='List Pending Maintenance')
    def get(self, request):
        requests = MaintenanceRequest.objects.filter(
            status='pending_proctor'
        ).order_by('-reported_date')
        serializer = MaintenanceRequestListSerializer(requests, many=True)
        
        return Response({
            'success': True,
            'data': {'requests': serializer.data}
        })


class ProctorMaintenanceApproveView(APIView):
    """Approve maintenance request."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Approve Maintenance Request')
    def put(self, request, pk):
        try:
            maintenance = MaintenanceRequest.objects.get(pk=pk)
        except MaintenanceRequest.DoesNotExist:
            return Response({'success': False, 'error': 'Request not found'}, status=404)
        
        maintenance.status = 'approved_by_proctor'
        maintenance.approved_by = request.user
        maintenance.approved_date = timezone.now()
        maintenance.save()
        
        return Response({
            'success': True,
            'message': 'Maintenance approved',
            'data': {'status': maintenance.status}
        })


class ProctorMaintenanceRejectView(APIView):
    """Reject maintenance request."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Reject Maintenance Request')
    def put(self, request, pk):
        try:
            maintenance = MaintenanceRequest.objects.get(pk=pk)
        except MaintenanceRequest.DoesNotExist:
            return Response({'success': False, 'error': 'Request not found'}, status=404)
        
        maintenance.status = 'rejected'
        maintenance.rejection_reason = request.data.get('rejection_reason', '')
        maintenance.save()
        
        return Response({
            'success': True,
            'message': 'Maintenance rejected',
            'data': {'status': maintenance.status}
        })


class ProctorPendingLaundryView(APIView):
    """Get pending laundry forms for proctor."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='List Pending Laundry')
    def get(self, request):
        forms = LaundryForm.objects.filter(
            status='pending_proctor'
        ).order_by('-submission_date')
        serializer = LaundryFormListSerializer(forms, many=True)
        
        return Response({
            'success': True,
            'data': {'forms': serializer.data}
        })


class ProctorLaundryApproveView(APIView):
    """Approve laundry form."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Approve Laundry Form')
    def put(self, request, pk):
        try:
            form = LaundryForm.objects.get(pk=pk)
        except LaundryForm.DoesNotExist:
            return Response({'success': False, 'error': 'Form not found'}, status=404)
        
        form.status = 'approved_by_proctor'
        form.approved_by = request.user
        form.approved_date = timezone.now()
        form.save()
        
        return Response({
            'success': True,
            'message': 'Laundry approved',
            'data': {'status': form.status}
        })


class ProctorLaundryRejectView(APIView):
    """Reject laundry form."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Reject Laundry Form')
    def put(self, request, pk):
        try:
            form = LaundryForm.objects.get(pk=pk)
        except LaundryForm.DoesNotExist:
            return Response({'success': False, 'error': 'Form not found'}, status=404)
        
        form.status = 'rejected'
        form.rejection_reason = request.data.get('rejection_reason', '')
        form.save()
        
        return Response({
            'success': True,
            'message': 'Laundry rejected',
            'data': {'status': form.status}
        })


class ProctorCreatePenaltyView(APIView):
    """Create penalty for student."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='Create Penalty')
    def post(self, request):
        serializer = PenaltyCreateSerializer(
            data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            penalty = serializer.save()
            return Response({
                'success': True,
                'message': 'Penalty assigned',
                'data': {
                    'penalty_code': penalty.penalty_code,
                    'status': penalty.status,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({'success': False, 'errors': serializer.errors}, status=400)


class ProctorStudentsView(APIView):
    """Get students in proctor's dorm."""
    
    permission_classes = [IsProctor]
    
    @extend_schema(tags=['proctors'], summary='List Students in Dorm')
    def get(self, request):
        try:
            proctor = request.user.proctor_profile
        except:
            return Response({'success': False, 'error': 'Proctor profile not found'}, status=404)
        
        dorm = proctor.assigned_dorm
        
        if dorm:
            assignments = RoomAssignment.objects.filter(
                room__dorm=dorm, status='active'
            ).select_related('student', 'student__user')
            
            students = [{
                'id': a.student.id,
                'full_name': a.student.user.full_name,
                'student_code': a.student.student_code,
                'room_number': a.room.room_number,
                'status': 'active',
            } for a in assignments]
        else:
            students = []
        
        return Response({
            'success': True,
            'data': {'students': students}
        })
