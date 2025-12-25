from django.contrib import admin
from .models import SystemConfiguration


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """Admin configuration for SystemConfiguration model."""
    
    list_display = ('key', 'value_preview', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('key', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('key', 'value')}),
        ('Details', {'fields': ('description', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    @admin.display(description='Value')
    def value_preview(self, obj):
        """Show truncated value for display."""
        if len(obj.value) > 50:
            return f"{obj.value[:50]}..."
        return obj.value
