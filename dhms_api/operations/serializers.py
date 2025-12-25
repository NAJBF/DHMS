from rest_framework import serializers
from .models import SystemConfiguration


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for system configuration."""
    
    class Meta:
        model = SystemConfiguration
        fields = ['id', 'key', 'value', 'description', 'is_active']
