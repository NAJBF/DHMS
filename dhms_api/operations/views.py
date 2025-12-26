from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

from students.models import LaundryForm
from students.serializers import LaundryFormListSerializer
from .serializers import LaundryVerificationSerializer, LaundryQRScanSerializer


from dhms_api.permissions import IsSecurity


# ==================== SECURITY VIEWS ====================

class SecurityDashboardView(APIView):
    """Security dashboard."""
    
    permission_classes = [IsSecurity]
    
    @extend_schema(tags=['security'], summary='Security Dashboard')
    def get(self, request):
        try:
            security = request.user.security_profile
        except:
            return Response({'success': False, 'error': 'Security profile not found'}, status=404)
        
        stats = {
            'pending_verification': LaundryForm.objects.filter(status='approved_by_proctor').count(),
            'verified_today': LaundryForm.objects.filter(
                status='verified_by_security',
                verification_date__date=timezone.now().date()
            ).count(),
            'taken_out_today': LaundryForm.objects.filter(
                status='taken_out',
                verification_date__date=timezone.now().date()
            ).count(),
        }
        
        return Response({
            'success': True,
            'data': {
                'security': {
                    'id': security.id,
                    'full_name': security.user.full_name,
                    'shift': security.shift,
                    'assigned_post': security.assigned_post,
                },
                'stats': stats,
            }
        })


class SecurityPendingLaundryView(APIView):
    """Get laundry forms pending security verification."""
    
    permission_classes = [IsSecurity]
    
    @extend_schema(tags=['security'], summary='List Pending Laundry for Verification')
    def get(self, request):
        forms = LaundryForm.objects.filter(
            status='approved_by_proctor'
        ).order_by('-approved_date')
        
        serializer = LaundryFormListSerializer(forms, many=True)
        
        return Response({
            'success': True,
            'data': {'forms': serializer.data}
        })


class SecurityVerifyLaundryView(APIView):
    """Verify a laundry form."""
    
    permission_classes = [IsSecurity]
    
    @extend_schema(
        tags=['security'], 
        summary='Verify Laundry Form',
        request=LaundryVerificationSerializer
    )
    def put(self, request, pk):
        try:
            form = LaundryForm.objects.get(pk=pk, status='approved_by_proctor')
        except LaundryForm.DoesNotExist:
            return Response({'success': False, 'error': 'Form not found or not ready for verification'}, status=404)
        
        try:
            security = request.user.security_profile
        except:
            return Response({'success': False, 'error': 'Security profile not found'}, status=404)
        
        form.status = 'verified_by_security'
        form.verified_by = security
        form.verification_date = timezone.now()
        form.verification_notes = request.data.get('verification_notes', '')
        form.save()
        
        return Response({
            'success': True,
            'message': 'Laundry verified',
            'data': {'status': form.status}
        })


class SecurityLaundryTakenOutView(APIView):
    """Mark laundry as taken out."""
    
    permission_classes = [IsSecurity]
    
    @extend_schema(tags=['security'], summary='Mark Laundry as Taken Out')
    def put(self, request, pk):
        try:
            form = LaundryForm.objects.get(pk=pk, status='verified_by_security')
        except LaundryForm.DoesNotExist:
            return Response({'success': False, 'error': 'Form not found or not verified'}, status=404)
        
        form.status = 'taken_out'
        form.save()
        
        return Response({
            'success': True,
            'message': 'Laundry taken out',
            'data': {'status': form.status}
        })


class SecurityLaundryQRScanView(APIView):
    """Handle QR code scan for laundry."""
    
    permission_classes = [IsSecurity]
    
    @extend_schema(
        tags=['security'], 
        summary='Scan Laundry QR Code',
        request=LaundryQRScanSerializer
    )
    def post(self, request):
        qr_code = request.data.get('qr_code')
        
        if not qr_code:
            return Response({'success': False, 'error': 'QR code required'}, status=400)
        
        try:
            form = LaundryForm.objects.get(form_code=qr_code)
        except LaundryForm.DoesNotExist:
            return Response({'success': False, 'error': 'Invalid QR code'}, status=404)
        
        if form.status == 'taken_out':
            return Response({'success': False, 'error': 'Laundry already taken out'}, status=400)
        
        if form.status != 'verified_by_security':
            return Response({'success': False, 'error': 'Laundry not yet verified'}, status=400)
        
        form.status = 'taken_out'
        form.save()
        
        return Response({
            'success': True,
            'message': 'Laundry taken out',
            'data': {
                'form_code': form.form_code,
                'student_name': form.student.user.full_name,
                'item_count': form.item_count,
                'status': form.status,
            }
        })


# ==================== PUBLIC QR LINK ====================

class PublicLaundryTakenOutView(APIView):
    """
    Public endpoint for QR code scanning.
    When the QR code is scanned, this endpoint is visited and updates the laundry status.
    URL: /aau-dhms-api/public/laundry/<form_code>/taken/
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['public'],
        summary='Public QR Code Link - Mark Laundry Taken Out',
        description='Public endpoint that can be embedded in QR codes. When scanned/visited, marks laundry as taken out.',
        parameters=[
            OpenApiParameter(name='form_code', type=str, location=OpenApiParameter.PATH, description='Laundry form code'),
        ]
    )
    def get(self, request, form_code):
        """Handle GET request from QR code scan."""
        try:
            form = LaundryForm.objects.select_related('student', 'student__user').get(form_code=form_code)
        except LaundryForm.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid laundry form code',
                'message': 'The QR code is invalid or expired.'
            }, status=404)
        
        # Check current status
        if form.status == 'taken_out':
            return Response({
                'success': False,
                'error': 'Already taken out',
                'message': f'This laundry was already taken out.',
                'data': {
                    'form_code': form.form_code,
                    'student_name': form.student.user.full_name,
                    'status': form.status,
                }
            }, status=400)
        
        if form.status != 'verified_by_security':
            return Response({
                'success': False,
                'error': 'Not verified',
                'message': f'This laundry has not been verified by security yet. Current status: {form.get_status_display()}',
                'data': {
                    'form_code': form.form_code,
                    'status': form.status,
                }
            }, status=400)
        
        # Update status to taken_out
        form.status = 'taken_out'
        form.save()
        
        return Response({
            'success': True,
            'message': 'Laundry successfully marked as taken out!',
            'data': {
                'form_code': form.form_code,
                'student_name': form.student.user.full_name,
                'student_code': form.student.student_code,
                'item_count': form.item_count,
                'status': form.status,
                'taken_out_at': timezone.now().isoformat(),
            }
        })


class PublicLaundryStatusView(APIView):
    """
    Public endpoint to check laundry status.
    URL: /aau-dhms-api/public/laundry/<form_code>/status/
    """
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['public'],
        summary='Public - Check Laundry Status',
        description='Check the current status of a laundry form without authentication.'
    )
    def get(self, request, form_code):
        """Get laundry form status."""
        try:
            form = LaundryForm.objects.select_related('student', 'student__user').get(form_code=form_code)
        except LaundryForm.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid laundry form code'
            }, status=404)
        
        return Response({
            'success': True,
            'data': {
                'form_code': form.form_code,
                'student_name': form.student.user.full_name,
                'item_count': form.item_count,
                'status': form.status,
                'status_display': form.get_status_display(),
                'submission_date': form.submission_date,
                'can_take_out': form.status == 'verified_by_security',
            }
        })
