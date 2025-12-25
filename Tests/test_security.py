"""
Tests for security endpoints.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestSecurityDashboard:
    """Test security dashboard endpoint."""
    
    def test_dashboard(self, security_client, security_profile):
        """Test security dashboard."""
        url = '/aau-dhms-api/security/dashboard/'
        response = security_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'security' in response.data['data']
        assert 'stats' in response.data['data']
    
    def test_dashboard_wrong_role(self, authenticated_client, student_profile):
        """Test dashboard with student role."""
        url = '/aau-dhms-api/security/dashboard/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestSecurityLaundry:
    """Test security laundry endpoints."""
    
    def test_list_pending_laundry(self, security_client, security_profile, approved_laundry_form):
        """Test listing pending laundry for verification."""
        url = '/aau-dhms-api/security/laundry/pending/'
        response = security_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'forms' in response.data['data']
        assert len(response.data['data']['forms']) == 1
    
    def test_verify_laundry(self, security_client, security_profile, approved_laundry_form):
        """Test verifying laundry form."""
        url = f'/aau-dhms-api/security/laundry/{approved_laundry_form.id}/verify/'
        data = {'verification_notes': 'Items verified'}
        response = security_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'verified_by_security'
    
    def test_mark_laundry_taken_out(self, security_client, security_profile, verified_laundry_form):
        """Test marking laundry as taken out."""
        url = f'/aau-dhms-api/security/laundry/{verified_laundry_form.id}/taken-out/'
        response = security_client.put(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'taken_out'
    
    def test_qr_scan(self, security_client, security_profile, verified_laundry_form):
        """Test QR code scanning."""
        url = '/aau-dhms-api/security/laundry/scan/'
        data = {'qr_code': verified_laundry_form.form_code}
        response = security_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'taken_out'
    
    def test_qr_scan_invalid_code(self, security_client, security_profile):
        """Test QR scanning with invalid code."""
        url = '/aau-dhms-api/security/laundry/scan/'
        data = {'qr_code': 'INVALID-CODE'}
        response = security_client.post(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_qr_scan_already_taken(self, security_client, security_profile, verified_laundry_form):
        """Test QR scanning for already taken laundry."""
        # First scan
        url = '/aau-dhms-api/security/laundry/scan/'
        data = {'qr_code': verified_laundry_form.form_code}
        security_client.post(url, data)
        
        # Second scan should fail
        response = security_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already taken out' in response.data['error']


@pytest.mark.django_db
class TestPublicLaundryEndpoints:
    """Test public laundry endpoints (no auth required)."""
    
    def test_public_laundry_status(self, api_client, verified_laundry_form):
        """Test checking laundry status publicly."""
        url = f'/aau-dhms-api/public/laundry/{verified_laundry_form.form_code}/status/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['form_code'] == verified_laundry_form.form_code
        assert response.data['data']['can_take_out'] is True
    
    def test_public_laundry_taken_out(self, api_client, verified_laundry_form):
        """Test public QR link for taking out laundry."""
        url = f'/aau-dhms-api/public/laundry/{verified_laundry_form.form_code}/taken/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'taken_out'
    
    def test_public_laundry_taken_out_already_taken(self, api_client, verified_laundry_form):
        """Test public link for already taken laundry."""
        # First take out
        url = f'/aau-dhms-api/public/laundry/{verified_laundry_form.form_code}/taken/'
        api_client.get(url)
        
        # Second attempt should fail
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Already taken out' in response.data['error']
    
    def test_public_laundry_taken_out_not_verified(self, api_client, laundry_form):
        """Test public link for not verified laundry."""
        url = f'/aau-dhms-api/public/laundry/{laundry_form.form_code}/taken/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'not verified' in response.data['error'].lower()
    
    def test_public_laundry_invalid_code(self, api_client):
        """Test public link with invalid code."""
        url = '/aau-dhms-api/public/laundry/INVALID-CODE/status/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
