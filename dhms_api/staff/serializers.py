from rest_framework import serializers
from .models import Dorm, Room, RoomInventory


class DormListSerializer(serializers.ModelSerializer):
    """Serializer for listing dorms."""
    
    proctor_name = serializers.CharField(source='proctor.user.full_name', read_only=True)
    
    class Meta:
        model = Dorm
        fields = [
            'id', 'dorm_code', 'name', 'type', 'location',
            'total_rooms', 'capacity', 'current_occupancy',
            'status', 'proctor_name', 'created_at'
        ]


class RoomListSerializer(serializers.ModelSerializer):
    """Serializer for listing rooms."""
    
    dorm_name = serializers.CharField(source='dorm.name', read_only=True)
    dorm_code = serializers.CharField(source='dorm.dorm_code', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'dorm', 'dorm_name', 'dorm_code',
            'floor', 'capacity', 'current_occupancy',
            'room_type', 'amenities', 'status', 'created_at'
        ]


class RoomInventorySerializer(serializers.ModelSerializer):
    """Serializer for room inventory."""
    
    class Meta:
        model = RoomInventory
        fields = ['id', 'room', 'item_name', 'quantity', 'condition', 'last_check_date', 'notes']
