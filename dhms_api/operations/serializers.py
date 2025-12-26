from rest_framework import serializers
from .models import SystemConfiguration


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for system configuration."""
    
    class Meta:
        model = SystemConfiguration
        fields = ['id', 'key', 'value', 'description', 'is_active']


class LaundryVerificationSerializer(serializers.Serializer):
    """Serializer for verifying laundry."""
    verification_notes = serializers.CharField(required=False, allow_blank=True)


class LaundryQRScanSerializer(serializers.Serializer):
    """Serializer for washing QR scan."""
    qr_code = serializers.CharField(required=True)
