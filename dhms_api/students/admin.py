from django.contrib import admin
from .models import RoomAssignment, MaintenanceRequest, LaundryForm, Penalty, KeyManagement


@admin.register(RoomAssignment)
class RoomAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for RoomAssignment model."""
    
    list_display = ('student', 'room', 'assignment_date', 'check_in_date', 
                    'expected_check_out', 'status', 'assigned_by')
    list_filter = ('status', 'assignment_date', 'room__dorm')
    search_fields = ('student__student_code', 'student__user__full_name', 
                     'room__room_number', 'room__dorm__name')
    raw_id_fields = ('student', 'room', 'assigned_by')
    date_hierarchy = 'assignment_date'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('student', 'room', 'assigned_by')}),
        ('Dates', {'fields': ('assignment_date', 'check_in_date', 'expected_check_out', 'actual_check_out')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    """Admin configuration for MaintenanceRequest model."""
    
    list_display = ('request_code', 'title', 'student', 'room', 'issue_type', 
                    'urgency', 'status', 'reported_date')
    list_filter = ('status', 'issue_type', 'urgency', 'room__dorm')
    search_fields = ('request_code', 'title', 'student__student_code', 
                     'student__user__full_name', 'room__room_number')
    raw_id_fields = ('student', 'room', 'approved_by', 'assigned_to')
    date_hierarchy = 'reported_date'
    readonly_fields = ('reported_date',)
    
    fieldsets = (
        (None, {'fields': ('request_code', 'student', 'room')}),
        ('Issue Details', {'fields': ('issue_type', 'title', 'description', 'urgency')}),
        ('Status & Workflow', {'fields': ('status', 'rejection_reason')}),
        ('Approval', {'fields': ('approved_by', 'approved_date')}),
        ('Assignment', {'fields': ('assigned_to', 'assigned_date')}),
        ('Progress', {'fields': ('started_date', 'completed_date')}),
        ('Timestamps', {'fields': ('reported_date',)}),
    )


@admin.register(LaundryForm)
class LaundryFormAdmin(admin.ModelAdmin):
    """Admin configuration for LaundryForm model."""
    
    list_display = ('form_code', 'student', 'item_count', 'status', 
                    'submission_date', 'approved_by', 'verified_by')
    list_filter = ('status', 'submission_date')
    search_fields = ('form_code', 'student__student_code', 'student__user__full_name')
    raw_id_fields = ('student', 'approved_by', 'verified_by')
    date_hierarchy = 'submission_date'
    readonly_fields = ('submission_date',)
    
    fieldsets = (
        (None, {'fields': ('form_code', 'student')}),
        ('Items', {'fields': ('item_count', 'item_list', 'special_instructions')}),
        ('Status', {'fields': ('status', 'rejection_reason')}),
        ('Approval', {'fields': ('approved_by', 'approved_date')}),
        ('Verification', {'fields': ('verified_by', 'verification_date', 'verification_notes')}),
        ('Timestamps', {'fields': ('submission_date',)}),
    )


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    """Admin configuration for Penalty model."""
    
    list_display = ('penalty_code', 'student', 'violation_type', 'duration_days', 
                    'start_date', 'end_date', 'status', 'assigned_by')
    list_filter = ('status', 'violation_type', 'start_date')
    search_fields = ('penalty_code', 'student__student_code', 'student__user__full_name')
    raw_id_fields = ('student', 'assigned_by')
    date_hierarchy = 'start_date'
    readonly_fields = ('assigned_date',)
    
    fieldsets = (
        (None, {'fields': ('penalty_code', 'student', 'assigned_by')}),
        ('Violation Details', {'fields': ('violation_type', 'description')}),
        ('Duration', {'fields': ('duration_days', 'start_date', 'end_date')}),
        ('Status & Consequences', {'fields': ('status', 'consequences')}),
        ('Timestamps', {'fields': ('assigned_date',)}),
    )


@admin.register(KeyManagement)
class KeyManagementAdmin(admin.ModelAdmin):
    """Admin configuration for KeyManagement model."""
    
    list_display = ('key_number', 'room', 'student', 'status', 'issued_date', 'returned_date')
    list_filter = ('status', 'room__dorm')
    search_fields = ('key_number', 'room__room_number', 'student__student_code', 
                     'student__user__full_name')
    raw_id_fields = ('room', 'student')
    
    fieldsets = (
        (None, {'fields': ('room', 'key_number')}),
        ('Assignment', {'fields': ('student', 'status')}),
        ('Dates', {'fields': ('issued_date', 'returned_date')}),
    )
