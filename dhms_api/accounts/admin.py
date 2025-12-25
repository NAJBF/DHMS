from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Proctor, Staff, Security, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = ('username', 'full_name', 'role', 'email', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'full_name', 'email', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'phone')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model."""
    
    list_display = ('student_code', 'get_full_name', 'student_type', 'department', 
                    'year_of_study', 'eligibility_status', 'created_at')
    list_filter = ('student_type', 'eligibility_status', 'year_of_study', 'department')
    search_fields = ('student_code', 'user__full_name', 'user__username', 'department')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
    
    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.full_name


@admin.register(Proctor)
class ProctorAdmin(admin.ModelAdmin):
    """Admin configuration for Proctor model."""
    
    list_display = ('proctor_code', 'get_full_name', 'assigned_dorm', 'is_active')
    list_filter = ('is_active', 'assigned_dorm')
    search_fields = ('proctor_code', 'user__full_name', 'user__username')
    raw_id_fields = ('user', 'assigned_dorm')
    
    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.full_name


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Admin configuration for Staff model."""
    
    list_display = ('staff_code', 'get_full_name', 'department', 'position', 'is_active')
    list_filter = ('is_active', 'department', 'position')
    search_fields = ('staff_code', 'user__full_name', 'user__username', 'department')
    raw_id_fields = ('user',)
    
    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.full_name


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    """Admin configuration for Security model."""
    
    list_display = ('security_code', 'get_full_name', 'shift', 'assigned_post', 'is_active')
    list_filter = ('is_active', 'shift', 'assigned_post')
    search_fields = ('security_code', 'user__full_name', 'user__username')
    raw_id_fields = ('user',)
    
    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.full_name


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""
    
    list_display = ('action', 'user', 'table_name', 'record_id', 'ip_address', 'created_at')
    list_filter = ('action', 'table_name', 'created_at')
    search_fields = ('action', 'user__username', 'table_name', 'ip_address')
    readonly_fields = ('user', 'action', 'table_name', 'record_id', 'old_values', 
                       'new_values', 'ip_address', 'user_agent', 'created_at')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
