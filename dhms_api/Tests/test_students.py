"""
Tests for student endpoints.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestStudentDashboard:
    """Test student dashboard endpoint."""
    
    def test_dashboard_with_room(self, authenticated_client, student_profile, room_assignment):
        """Test dashboard with active room assignment."""
        url = '/aau-dhms-api/students/dashboard/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'student' in response.data['data']
        assert 'room' in response.data['data']
        assert 'stats' in response.data['data']
        assert response.data['data']['student']['student_code'] == 'STU-TEST-001'
    
    def test_dashboard_without_room(self, authenticated_client, student_profile):
        """Test dashboard without room assignment."""
        url = '/aau-dhms-api/students/dashboard/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['room'] is None
    
    def test_dashboard_unauthenticated(self, api_client):
        """Test dashboard without authentication."""
        url = '/aau-dhms-api/students/dashboard/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_dashboard_wrong_role(self, proctor_client):
        """Test dashboard with wrong role."""
        url = '/aau-dhms-api/students/dashboard/'
        response = proctor_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestStudentRoom:
    """Test student room endpoint."""
    
    def test_get_room_details(self, authenticated_client, student_profile, room_assignment):
        """Test getting room details."""
        url = '/aau-dhms-api/students/room/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'room' in response.data['data']
        assert 'roommates' in response.data['data']
    
    def test_get_room_no_assignment(self, authenticated_client, student_profile):
        """Test getting room without assignment."""
        url = '/aau-dhms-api/students/room/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestStudentMaintenance:
    """Test student maintenance endpoints."""
    
    def test_list_maintenance_requests(self, authenticated_client, student_profile, maintenance_request):
        """Test listing maintenance requests."""
        url = '/aau-dhms-api/students/maintenance/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'requests' in response.data['data']
        assert len(response.data['data']['requests']) == 1
    
    def test_create_maintenance_request(self, authenticated_client, student_profile, room):
        """Test creating a maintenance request."""
        url = '/aau-dhms-api/students/maintenance/'
        data = {
            'room_id': room.id,
            'issue_type': 'plumbing',
            'title': 'Broken Shower',
            'description': 'The shower head is broken.',
            'urgency': 'high'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'request_code' in response.data['data']
        assert response.data['data']['status'] == 'pending_proctor'


@pytest.mark.django_db
class TestStudentLaundry:
    """Test student laundry endpoints."""
    
    def test_list_laundry_forms(self, authenticated_client, student_profile, laundry_form):
        """Test listing laundry forms."""
        url = '/aau-dhms-api/students/laundry/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'forms' in response.data['data']
        assert len(response.data['data']['forms']) == 1
    
    def test_create_laundry_form(self, authenticated_client, student_profile):
        """Test creating a laundry form."""
        url = '/aau-dhms-api/students/laundry/'
        data = {
            'item_count': 5,
            'item_list': '3 shirts, 2 pants',
            'special_instructions': 'Handle with care'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'form_code' in response.data['data']
        assert response.data['data']['status'] == 'pending_proctor'


@pytest.mark.django_db
class TestStudentPenalties:
    """Test student penalties endpoint."""
    
    def test_list_penalties(self, authenticated_client, student_profile, penalty):
        """Test listing penalties."""
        url = '/aau-dhms-api/students/penalties/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'penalties' in response.data['data']
        assert len(response.data['data']['penalties']) == 1
        assert response.data['data']['penalties'][0]['penalty_code'] == 'PEN-TEST-001'
