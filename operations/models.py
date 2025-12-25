from django.db import models

# Operations app - shared utilities and base models
# The main operational models are distributed across their respective apps:
# - accounts: User, Student, Proctor, Staff, Security, AuditLog
# - staff: Dorm, Room, RoomInventory
# - students: RoomAssignment, MaintenanceRequest, LaundryForm, Penalty, KeyManagement

# This app can be used for:
# - Shared abstract models
# - Cross-cutting operational utilities
# - Reports and analytics models
# - System configuration models


class SystemConfiguration(models.Model):
    """System-wide configuration settings."""
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configuration'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
