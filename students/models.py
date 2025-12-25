from django.db import models


class RoomAssignment(models.Model):
    """Room assignment model for tracking student room allocations."""
    
    class AssignmentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='room_assignments'
    )
    room = models.ForeignKey(
        'staff.Room',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    assignment_date = models.DateField()
    check_in_date = models.DateField(blank=True, null=True)
    expected_check_out = models.DateField(blank=True, null=True)
    actual_check_out = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ACTIVE
    )
    assigned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='room_assignments_made'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'room_assignments'
        verbose_name = 'Room Assignment'
        verbose_name_plural = 'Room Assignments'
    
    def __str__(self):
        return f"{self.student} - {self.room} ({self.status})"


class MaintenanceRequest(models.Model):
    """Maintenance request model for tracking room maintenance issues."""
    
    class IssueType(models.TextChoices):
        PLUMBING = 'plumbing', 'Plumbing'
        ELECTRICAL = 'electrical', 'Electrical'
        FURNITURE = 'furniture', 'Furniture'
        CLEANING = 'cleaning', 'Cleaning'
        OTHER = 'other', 'Other'
    
    class Urgency(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
    
    class RequestStatus(models.TextChoices):
        PENDING_PROCTOR = 'pending_proctor', 'Pending Proctor Approval'
        APPROVED_BY_PROCTOR = 'approved_by_proctor', 'Approved by Proctor'
        ASSIGNED_TO_STAFF = 'assigned_to_staff', 'Assigned to Staff'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'
    
    request_code = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    room = models.ForeignKey(
        'staff.Room',
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    issue_type = models.CharField(max_length=20, choices=IssueType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    urgency = models.CharField(
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.MEDIUM
    )
    reported_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING_PROCTOR
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_maintenance_requests'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance_requests'
    )
    assigned_date = models.DateTimeField(blank=True, null=True)
    started_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'maintenance_requests'
        verbose_name = 'Maintenance Request'
        verbose_name_plural = 'Maintenance Requests'
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"{self.request_code} - {self.title}"


class LaundryForm(models.Model):
    """Laundry form model for tracking laundry submissions."""
    
    class FormStatus(models.TextChoices):
        PENDING_PROCTOR = 'pending_proctor', 'Pending Proctor Approval'
        APPROVED_BY_PROCTOR = 'approved_by_proctor', 'Approved by Proctor'
        VERIFIED_BY_SECURITY = 'verified_by_security', 'Verified by Security'
        REJECTED = 'rejected', 'Rejected'
        TAKEN_OUT = 'taken_out', 'Taken Out'
    
    form_code = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='laundry_forms'
    )
    item_count = models.PositiveIntegerField()
    item_list = models.TextField()
    special_instructions = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=FormStatus.choices,
        default=FormStatus.PENDING_PROCTOR
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_laundry_forms'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        'accounts.Security',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_laundry_forms'
    )
    verification_date = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'laundry_forms'
        verbose_name = 'Laundry Form'
        verbose_name_plural = 'Laundry Forms'
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"{self.form_code} - {self.student}"


class Penalty(models.Model):
    """Penalty model for tracking student disciplinary actions."""
    
    class ViolationType(models.TextChoices):
        NOISE = 'noise', 'Noise'
        DAMAGE = 'damage', 'Damage'
        CURFEW = 'curfew', 'Curfew Violation'
        SMOKING = 'smoking', 'Smoking'
        VISITOR = 'visitor', 'Visitor Violation'
        OTHER = 'other', 'Other'
    
    class PenaltyStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    penalty_code = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='penalties'
    )
    violation_type = models.CharField(max_length=20, choices=ViolationType.choices)
    description = models.TextField()
    duration_days = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=PenaltyStatus.choices,
        default=PenaltyStatus.ACTIVE
    )
    assigned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='penalties_assigned'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    consequences = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'penalties'
        verbose_name = 'Penalty'
        verbose_name_plural = 'Penalties'
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.penalty_code} - {self.student} ({self.violation_type})"


class KeyManagement(models.Model):
    """Key management model for tracking room key assignments."""
    
    class KeyStatus(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        ISSUED = 'issued', 'Issued'
        LOST = 'lost', 'Lost'
        DAMAGED = 'damaged', 'Damaged'
    
    room = models.ForeignKey(
        'staff.Room',
        on_delete=models.CASCADE,
        related_name='keys'
    )
    key_number = models.CharField(max_length=20)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_keys'
    )
    issued_date = models.DateField(blank=True, null=True)
    returned_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=KeyStatus.choices,
        default=KeyStatus.AVAILABLE
    )
    
    class Meta:
        db_table = 'key_management'
        verbose_name = 'Key'
        verbose_name_plural = 'Keys'
    
    def __str__(self):
        return f"Key {self.key_number} - {self.room}"
