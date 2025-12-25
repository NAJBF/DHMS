from rest_framework import serializers
from django.utils import timezone
import uuid

from .models import RoomAssignment, MaintenanceRequest, LaundryForm, Penalty, KeyManagement
from staff.models import Dorm, Room
from accounts.models import Student


class DormSerializer(serializers.ModelSerializer):
    """Serializer for Dorm model."""
    
    class Meta:
        model = Dorm
        fields = ['id', 'name', 'type', 'location']


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model."""
    
    dorm = DormSerializer(read_only=True)
    amenities = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'dorm', 'capacity', 'current_occupancy', 'floor', 'amenities']
    
    def get_amenities(self, obj):
        if obj.amenities:
            return [a.strip() for a in obj.amenities.split(',')]
        return []


class RoommateSerializer(serializers.ModelSerializer):
    """Serializer for roommate info."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'full_name', 'student_code', 'year_of_study']


class RoomAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Room Assignment."""
    
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    dorm_name = serializers.CharField(source='room.dorm.name', read_only=True)
    floor = serializers.IntegerField(source='room.floor', read_only=True)
    
    class Meta:
        model = RoomAssignment
        fields = [
            'id', 'room_id', 'room_number', 'dorm_name', 'floor',
            'assignment_date', 'check_in_date', 'expected_check_out',
            'actual_check_out', 'status'
        ]


# Maintenance Request Serializers
class MaintenanceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating maintenance requests."""
    
    class Meta:
        model = MaintenanceRequest
        fields = ['room_id', 'issue_type', 'title', 'description', 'urgency']
        extra_kwargs = {
            'room_id': {'source': 'room', 'required': True}
        }
    
    def create(self, validated_data):
        # Generate request code
        validated_data['request_code'] = f"MNT-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        validated_data['student'] = self.context['request'].user.student_profile
        return super().create(validated_data)


class MaintenanceRequestListSerializer(serializers.ModelSerializer):
    """Serializer for listing maintenance requests."""
    
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    dorm_name = serializers.CharField(source='room.dorm.name', read_only=True)
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_code', 'issue_type', 'title', 'description',
            'urgency', 'status', 'reported_date', 'student_name',
            'room_number', 'dorm_name', 'approved_date', 'completed_date'
        ]


# Laundry Form Serializers
class LaundryFormCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating laundry forms."""
    
    class Meta:
        model = LaundryForm
        fields = ['item_count', 'item_list', 'special_instructions']
    
    def create(self, validated_data):
        # Generate form code
        validated_data['form_code'] = f"LAU-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        validated_data['student'] = self.context['request'].user.student_profile
        return super().create(validated_data)


class LaundryFormListSerializer(serializers.ModelSerializer):
    """Serializer for listing laundry forms."""
    
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_code', read_only=True)
    
    class Meta:
        model = LaundryForm
        fields = [
            'id', 'form_code', 'item_count', 'item_list', 'special_instructions',
            'status', 'submission_date', 'student_name', 'student_code',
            'approved_date', 'verification_date'
        ]


# Penalty Serializers
class PenaltySerializer(serializers.ModelSerializer):
    """Serializer for penalties."""
    
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    
    class Meta:
        model = Penalty
        fields = [
            'id', 'penalty_code', 'violation_type', 'description',
            'duration_days', 'start_date', 'end_date', 'status',
            'consequences', 'student_name', 'assigned_by_name', 'assigned_date'
        ]


class PenaltyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating penalties."""
    
    student_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Penalty
        fields = [
            'student_id', 'violation_type', 'description',
            'duration_days', 'start_date', 'consequences'
        ]
    
    def validate_student_id(self, value):
        try:
            Student.objects.get(id=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found.")
        return value
    
    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        validated_data['student'] = Student.objects.get(id=student_id)
        validated_data['penalty_code'] = f"PEN-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        validated_data['assigned_by'] = self.context['request'].user
        
        # Calculate end date
        from datetime import timedelta
        validated_data['end_date'] = validated_data['start_date'] + timedelta(days=validated_data['duration_days'])
        
        return super().create(validated_data)


# Room Assignment Create Serializer
class RoomAssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating room assignments."""
    
    student_id = serializers.IntegerField(write_only=True)
    room_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = RoomAssignment
        fields = ['student_id', 'room_id', 'assignment_date', 'expected_check_out']
    
    def validate_student_id(self, value):
        try:
            Student.objects.get(id=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found.")
        return value
    
    def validate_room_id(self, value):
        try:
            room = Room.objects.get(id=value)
            if room.current_occupancy >= room.capacity:
                raise serializers.ValidationError("Room is full.")
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room not found.")
        return value
    
    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        room_id = validated_data.pop('room_id')
        
        validated_data['student'] = Student.objects.get(id=student_id)
        validated_data['room'] = Room.objects.get(id=room_id)
        validated_data['assigned_by'] = self.context['request'].user
        
        # Update room occupancy
        room = validated_data['room']
        room.current_occupancy += 1
        if room.current_occupancy >= room.capacity:
            room.status = 'occupied'
        room.save()
        
        return super().create(validated_data)
