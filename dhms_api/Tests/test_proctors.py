"""
Tests for proctor endpoints.
"""
import pytest
from rest_framework import status
from datetime import date, timedelta


@pytest.mark.django_db
class TestProctorDashboard:
    """Test proctor dashboard endpoint."""
    
    def test_dashboard(self, proctor_client, proctor_profile):
        """Test proctor dashboard."""
        url = '/aau-dhms-api/proctors/dashboard/'
        response = proctor_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'proctor' in response.data['data']
        assert 'stats' in response.data['data']
    
    def test_dashboard_wrong_role(self, authenticated_client, student_profile):
        """Test dashboard with student role."""
        url = '/aau-dhms-api/proctors/dashboard/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProctorRoomAssignment:
    """Test room assignment endpoint."""
    
    def test_assign_room(self, proctor_client, proctor_profile, student_profile, room):
        """Test assigning room to student."""
        url = '/aau-dhms-api/proctors/assign-room/'
        data = {
            'student_id': student_profile.id,
            'room_id': room.id,
            'assignment_date': str(date.today()),
            'expected_check_out': str(date.today() + timedelta(days=180))
        }
        response = proctor_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'active'
    
    def test_assign_room_invalid_student(self, proctor_client, proctor_profile, room):
        """Test assigning room to non-existent student."""
        url = '/aau-dhms-api/proctors/assign-room/'
        data = {
            'student_id': 99999,
            'room_id': room.id,
            'assignment_date': str(date.today()),
            'expected_check_out': str(date.today() + timedelta(days=180))
        }
        response = proctor_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProctorMaintenance:
    """Test proctor maintenance endpoints."""
    
    def test_list_pending_maintenance(self, proctor_client, proctor_profile, maintenance_request):
        """Test listing pending maintenance requests."""
        url = '/aau-dhms-api/proctors/maintenance/pending/'
        response = proctor_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'requests' in response.data['data']
    
    def test_approve_maintenance(self, proctor_client, proctor_profile, maintenance_request):
        """Test approving maintenance request."""
        url = f'/aau-dhms-api/proctors/maintenance/{maintenance_request.id}/approve/'
        response = proctor_client.put(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'approved_by_proctor'
    
    def test_reject_maintenance(self, proctor_client, proctor_profile, maintenance_request):
        """Test rejecting maintenance request."""
        url = f'/aau-dhms-api/proctors/maintenance/{maintenance_request.id}/reject/'
        data = {'rejection_reason': 'Not a valid issue'}
        response = proctor_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'rejected'


@pytest.mark.django_db
class TestProctorLaundry:
    """Test proctor laundry endpoints."""
    
    def test_list_pending_laundry(self, proctor_client, proctor_profile, laundry_form):
        """Test listing pending laundry forms."""
        url = '/aau-dhms-api/proctors/laundry/pending/'
        response = proctor_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'forms' in response.data['data']
    
    def test_approve_laundry(self, proctor_client, proctor_profile, laundry_form):
        """Test approving laundry form."""
        url = f'/aau-dhms-api/proctors/laundry/{laundry_form.id}/approve/'
        response = proctor_client.put(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'approved_by_proctor'
    
    def test_reject_laundry(self, proctor_client, proctor_profile, laundry_form):
        """Test rejecting laundry form."""
        url = f'/aau-dhms-api/proctors/laundry/{laundry_form.id}/reject/'
        data = {'rejection_reason': 'Too many items'}
        response = proctor_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'rejected'


@pytest.mark.django_db
class TestProctorPenalty:
    """Test proctor penalty endpoint."""
    
    def test_create_penalty(self, proctor_client, proctor_profile, student_profile):
        """Test creating a penalty."""
        url = '/aau-dhms-api/proctors/penalties/'
        data = {
            'student_id': student_profile.id,
            'violation_type': 'noise',
            'description': 'Playing loud music',
            'duration_days': 3,
            'start_date': str(date.today()),
            'consequences': 'Restricted access'
        }
        response = proctor_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'penalty_code' in response.data['data']
        assert response.data['data']['status'] == 'active'


@pytest.mark.django_db
class TestProctorStudents:
    """Test proctor students list endpoint."""
    
    def test_list_students(self, proctor_client, proctor_profile, student_profile, room_assignment):
        """Test listing students in dorm."""
        url = '/aau-dhms-api/proctors/students/'
        response = proctor_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'students' in response.data['data']
