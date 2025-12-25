"""
Tests for authentication endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLogin:
    """Test login endpoint."""
    
    def test_login_success(self, api_client, student_user):
        """Test successful login."""
        url = '/aau-dhms-api/auth/login/'
        data = {
            'username': 'teststudent',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'token' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'teststudent'
        assert response.data['user']['role'] == 'student'
    
    def test_login_invalid_credentials(self, api_client, student_user):
        """Test login with invalid credentials."""
        url = '/aau-dhms-api/auth/login/'
        data = {
            'username': 'teststudent',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with nonexistent user."""
        url = '/aau-dhms-api/auth/login/'
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRegister:
    """Test registration endpoint."""
    
    def test_register_success(self, api_client):
        """Test successful registration."""
        url = '/aau-dhms-api/auth/register/'
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'full_name': 'New User',
            'role': 'student',
            'email': 'newuser@test.com'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'token' in response.data
        assert response.data['user']['username'] == 'newuser'
    
    def test_register_password_mismatch(self, api_client):
        """Test registration with password mismatch."""
        url = '/aau-dhms-api/auth/register/'
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'full_name': 'New User',
            'role': 'student'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_username(self, api_client, student_user):
        """Test registration with duplicate username."""
        url = '/aau-dhms-api/auth/register/'
        data = {
            'username': 'teststudent',  # Already exists
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'full_name': 'New User',
            'role': 'student'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCurrentUser:
    """Test current user endpoint."""
    
    def test_get_current_user(self, authenticated_client, student_user):
        """Test getting current user info."""
        url = '/aau-dhms-api/auth/me/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['user']['username'] == 'teststudent'
        assert 'permissions' in response.data['user']
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test getting current user without authentication."""
        url = '/aau-dhms-api/auth/me/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogout:
    """Test logout endpoint."""
    
    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        url = '/aau-dhms-api/auth/logout/'
        response = authenticated_client.post(url, {})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Logged out successfully'
    
    def test_logout_unauthenticated(self, api_client):
        """Test logout without authentication."""
        url = '/aau-dhms-api/auth/logout/'
        response = api_client.post(url, {})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_token_refresh_success(self, api_client, student_user):
        """Test successful token refresh."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(student_user)
        
        url = '/aau-dhms-api/auth/refresh/'
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_token_refresh_invalid(self, api_client):
        """Test token refresh with invalid token."""
        url = '/aau-dhms-api/auth/refresh/'
        data = {'refresh': 'invalid-token'}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
