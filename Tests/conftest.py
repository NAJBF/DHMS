"""
Pytest configuration and fixtures for DHMS API tests.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== API CLIENT FIXTURES ====================

@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, student_user):
    """Return an API client authenticated as a student."""
    refresh = RefreshToken.for_user(student_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def proctor_client(api_client, proctor_user):
    """Return an API client authenticated as a proctor."""
    refresh = RefreshToken.for_user(proctor_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def staff_client(api_client, staff_user):
    """Return an API client authenticated as staff."""
    refresh = RefreshToken.for_user(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def security_client(api_client, security_user):
    """Return an API client authenticated as security."""
    refresh = RefreshToken.for_user(security_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


# ==================== USER FIXTURES ====================

@pytest.fixture
def student_user(db):
    """Create a student user."""
    user = User.objects.create_user(
        username='teststudent',
        password='testpass123',
        full_name='Test Student',
        role='student',
        email='student@test.com'
    )
    return user


@pytest.fixture
def proctor_user(db):
    """Create a proctor user."""
    user = User.objects.create_user(
        username='testproctor',
        password='testpass123',
        full_name='Test Proctor',
        role='proctor',
        email='proctor@test.com'
    )
    return user


@pytest.fixture
def staff_user(db):
    """Create a staff user."""
    user = User.objects.create_user(
        username='teststaff',
        password='testpass123',
        full_name='Test Staff',
        role='staff',
        email='staff@test.com'
    )
    return user


@pytest.fixture
def security_user(db):
    """Create a security user."""
    user = User.objects.create_user(
        username='testsecurity',
        password='testpass123',
        full_name='Test Security',
        role='security',
        email='security@test.com'
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User.objects.create_superuser(
        username='testadmin',
        password='testpass123',
        full_name='Test Admin',
        email='admin@test.com'
    )
    return user


# ==================== PROFILE FIXTURES ====================

@pytest.fixture
def student_profile(db, student_user):
    """Create a student profile."""
    from accounts.models import Student
    return Student.objects.create(
        user=student_user,
        student_code='STU-TEST-001',
        student_type='government',
        department='Computer Science',
        year_of_study=3,
        semester=1
    )


@pytest.fixture
def proctor_profile(db, proctor_user, dorm):
    """Create a proctor profile."""
    from accounts.models import Proctor
    return Proctor.objects.create(
        user=proctor_user,
        proctor_code='PRO-TEST-001',
        assigned_dorm=dorm,
        is_active=True
    )


@pytest.fixture
def staff_profile(db, staff_user):
    """Create a staff profile."""
    from accounts.models import Staff
    return Staff.objects.create(
        user=staff_user,
        staff_code='STF-TEST-001',
        department='Maintenance',
        position='Technician',
        is_active=True
    )


@pytest.fixture
def security_profile(db, security_user):
    """Create a security profile."""
    from accounts.models import Security
    return Security.objects.create(
        user=security_user,
        security_code='SEC-TEST-001',
        shift='morning',
        assigned_post='Main Gate',
        is_active=True
    )


# ==================== DORM & ROOM FIXTURES ====================

@pytest.fixture
def dorm(db):
    """Create a test dorm."""
    from staff.models import Dorm
    return Dorm.objects.create(
        dorm_code='DORM-TEST-001',
        name='Test Dorm',
        type='male',
        location='Campus Block A',
        total_rooms=50,
        capacity=100,
        current_occupancy=0,
        status='active'
    )


@pytest.fixture
def room(db, dorm):
    """Create a test room."""
    from staff.models import Room
    return Room.objects.create(
        dorm=dorm,
        room_number='101',
        floor=1,
        capacity=2,
        current_occupancy=0,
        room_type='double',
        status='available'
    )


@pytest.fixture
def room_assignment(db, student_profile, room, proctor_user):
    """Create a room assignment."""
    from students.models import RoomAssignment
    from datetime import date, timedelta
    return RoomAssignment.objects.create(
        student=student_profile,
        room=room,
        assignment_date=date.today(),
        check_in_date=date.today(),
        expected_check_out=date.today() + timedelta(days=180),
        status='active',
        assigned_by=proctor_user
    )


# ==================== REQUEST FIXTURES ====================

@pytest.fixture
def maintenance_request(db, student_profile, room):
    """Create a maintenance request."""
    from students.models import MaintenanceRequest
    return MaintenanceRequest.objects.create(
        request_code='MNT-TEST-001',
        student=student_profile,
        room=room,
        issue_type='plumbing',
        title='Leaking Faucet',
        description='The bathroom faucet is leaking water.',
        urgency='medium',
        status='pending_proctor'
    )


@pytest.fixture
def approved_maintenance_request(db, student_profile, room, proctor_user):
    """Create an approved maintenance request."""
    from students.models import MaintenanceRequest
    from django.utils import timezone
    return MaintenanceRequest.objects.create(
        request_code='MNT-TEST-002',
        student=student_profile,
        room=room,
        issue_type='electrical',
        title='Light Not Working',
        description='The ceiling light is not working.',
        urgency='high',
        status='approved_by_proctor',
        approved_by=proctor_user,
        approved_date=timezone.now()
    )


@pytest.fixture
def laundry_form(db, student_profile):
    """Create a laundry form."""
    from students.models import LaundryForm
    return LaundryForm.objects.create(
        form_code='LAU-TEST-001',
        student=student_profile,
        item_count=5,
        item_list='3 shirts, 2 pants',
        status='pending_proctor'
    )


@pytest.fixture
def approved_laundry_form(db, student_profile, proctor_user):
    """Create an approved laundry form."""
    from students.models import LaundryForm
    from django.utils import timezone
    return LaundryForm.objects.create(
        form_code='LAU-TEST-002',
        student=student_profile,
        item_count=3,
        item_list='2 shirts, 1 pants',
        status='approved_by_proctor',
        approved_by=proctor_user,
        approved_date=timezone.now()
    )


@pytest.fixture
def verified_laundry_form(db, student_profile, proctor_user, security_profile):
    """Create a verified laundry form."""
    from students.models import LaundryForm
    from django.utils import timezone
    return LaundryForm.objects.create(
        form_code='LAU-TEST-003',
        student=student_profile,
        item_count=4,
        item_list='2 shirts, 2 pants',
        status='verified_by_security',
        approved_by=proctor_user,
        approved_date=timezone.now(),
        verified_by=security_profile,
        verification_date=timezone.now()
    )


@pytest.fixture
def penalty(db, student_profile, proctor_user):
    """Create a penalty."""
    from students.models import Penalty
    from datetime import date, timedelta
    return Penalty.objects.create(
        penalty_code='PEN-TEST-001',
        student=student_profile,
        violation_type='noise',
        description='Playing loud music after curfew',
        duration_days=3,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=3),
        status='active',
        assigned_by=proctor_user,
        consequences='Restricted access to common areas'
    )
