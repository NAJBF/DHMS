"""
Tests for staff endpoints.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestStaffDashboard:
    """Test staff dashboard endpoint."""
    
    def test_dashboard(self, staff_client, staff_profile):
        """Test staff dashboard."""
        url = '/aau-dhms-api/staff/dashboard/'
        response = staff_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'staff' in response.data['data']
        assert 'stats' in response.data['data']
    
    def test_dashboard_wrong_role(self, authenticated_client, student_profile):
        """Test dashboard with student role."""
        url = '/aau-dhms-api/staff/dashboard/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestStaffMaintenance:
    """Test staff maintenance endpoints."""
    
    def test_list_available_jobs(self, staff_client, staff_profile, approved_maintenance_request):
        """Test listing available maintenance jobs."""
        url = '/aau-dhms-api/staff/maintenance/'
        response = staff_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'jobs' in response.data['data']
        assert len(response.data['data']['jobs']) == 1
    
    def test_list_my_jobs(self, staff_client, staff_profile):
        """Test listing assigned jobs."""
        url = '/aau-dhms-api/staff/maintenance/my-jobs/'
        response = staff_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'jobs' in response.data['data']
    
    def test_accept_job(self, staff_client, staff_profile, approved_maintenance_request):
        """Test accepting a maintenance job."""
        url = f'/aau-dhms-api/staff/maintenance/{approved_maintenance_request.id}/accept/'
        response = staff_client.put(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'assigned_to_staff'
    
    def test_start_job(self, staff_client, staff_profile, approved_maintenance_request):
        """Test starting a maintenance job."""
        # First accept the job
        accept_url = f'/aau-dhms-api/staff/maintenance/{approved_maintenance_request.id}/accept/'
        staff_client.put(accept_url, {})
        
        # Then start it
        url = f'/aau-dhms-api/staff/maintenance/{approved_maintenance_request.id}/start/'
        response = staff_client.put(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'in_progress'
    
    def test_complete_job(self, staff_client, staff_profile, approved_maintenance_request):
        """Test completing a maintenance job."""
        # Accept and start the job first
        accept_url = f'/aau-dhms-api/staff/maintenance/{approved_maintenance_request.id}/accept/'
        staff_client.put(accept_url, {})
        
        start_url = f'/aau-dhms-api/staff/maintenance/{approved_maintenance_request.id}/start/'
        staff_client.put(start_url, {})
        
        # Complete it
        url = f'/aau-dhms-api/staff/maintenance/{approved_maintenance_request.id}/complete/'
        response = staff_client.put(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'completed'


@pytest.mark.django_db
class TestDormList:
    """Test dorm listing endpoint."""
    
    def test_list_dorms(self, staff_client, dorm):
        """Test listing dorms."""
        url = '/aau-dhms-api/dorms/'
        response = staff_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'dorms' in response.data['data']
        assert len(response.data['data']['dorms']) == 1


@pytest.mark.django_db
class TestRoomList:
    """Test room listing endpoints."""
    
    def test_list_rooms_in_dorm(self, staff_client, dorm, room):
        """Test listing rooms in a dorm."""
        url = f'/aau-dhms-api/dorms/{dorm.id}/rooms/'
        response = staff_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'rooms' in response.data['data']
        assert len(response.data['data']['rooms']) == 1
    
    def test_list_available_rooms(self, staff_client, room):
        """Test listing available rooms."""
        url = '/aau-dhms-api/rooms/available/'
        response = staff_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'rooms' in response.data['data']
