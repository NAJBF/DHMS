from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Student, Proctor, Staff, Security

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'full_name', 'email', 'phone', 'is_active']
        read_only_fields = ['id', 'is_active']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'full_name', 'role', 'email', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user data."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'role': self.user.role,
            'full_name': self.user.full_name,
            'email': self.user.email,
        }
        
        return data


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for Student profile."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_code', 'full_name', 'email', 'phone',
            'student_type', 'academic_year', 'department',
            'year_of_study', 'semester', 'eligibility_status'
        ]


class ProctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Proctor profile."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    assigned_dorm_name = serializers.CharField(source='assigned_dorm.name', read_only=True)
    
    class Meta:
        model = Proctor
        fields = ['id', 'proctor_code', 'full_name', 'assigned_dorm', 'assigned_dorm_name', 'is_active']


class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for Staff profile."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Staff
        fields = ['id', 'staff_code', 'full_name', 'department', 'position', 'is_active']


class SecurityProfileSerializer(serializers.ModelSerializer):
    """Serializer for Security profile."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Security
        fields = ['id', 'security_code', 'full_name', 'shift', 'assigned_post', 'is_active']


class CurrentUserSerializer(serializers.ModelSerializer):
    """Serializer for current user with permissions."""
    
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'full_name', 'email', 'phone', 'permissions']
    
    def get_permissions(self, obj):
        """Get role-based permissions."""
        permissions_map = {
            'student': ['view_room', 'submit_maintenance', 'submit_laundry', 'view_penalties'],
            'proctor': ['manage_students', 'assign_rooms', 'approve_maintenance', 'approve_laundry', 'assign_penalties'],
            'staff': ['view_maintenance', 'update_maintenance', 'complete_maintenance'],
            'security': ['verify_laundry', 'mark_laundry_taken'],
            'admin': ['full_access'],
        }
        return permissions_map.get(obj.role, [])
