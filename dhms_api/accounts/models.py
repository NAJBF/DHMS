from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""
    
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for the DHMS system."""
    
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        PROCTOR = 'proctor', 'Proctor'
        STAFF = 'staff', 'Staff'
        SECURITY = 'security', 'Security'
        ADMIN = 'admin', 'Admin'
    
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Student(models.Model):
    """Student profile model linked to User."""
    
    class StudentType(models.TextChoices):
        GOVERNMENT = 'government', 'Government'
        SELF_SPONSORED = 'self_sponsored', 'Self Sponsored'
        DISABLED = 'disabled', 'Disabled'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_code = models.CharField(max_length=20, unique=True)
    student_type = models.CharField(max_length=20, choices=StudentType.choices)
    academic_year = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.PositiveIntegerField(blank=True, null=True)
    semester = models.PositiveIntegerField(blank=True, null=True)
    eligibility_status = models.BooleanField(default=True)
    disciplinary_record = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        return f"{self.student_code} - {self.user.full_name}"


class Proctor(models.Model):
    """Proctor profile model linked to User."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='proctor_profile'
    )
    proctor_code = models.CharField(max_length=20, unique=True)
    assigned_dorm = models.ForeignKey(
        'staff.Dorm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_proctors'
    )
    responsibilities = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'proctors'
        verbose_name = 'Proctor'
        verbose_name_plural = 'Proctors'
    
    def __str__(self):
        return f"{self.proctor_code} - {self.user.full_name}"


class Staff(models.Model):
    """Staff profile model linked to User."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    staff_code = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'staff'
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
    
    def __str__(self):
        return f"{self.staff_code} - {self.user.full_name}"


class Security(models.Model):
    """Security profile model linked to User."""
    
    class Shift(models.TextChoices):
        MORNING = 'morning', 'Morning'
        AFTERNOON = 'afternoon', 'Afternoon'
        NIGHT = 'night', 'Night'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='security_profile'
    )
    security_code = models.CharField(max_length=20, unique=True)
    shift = models.CharField(
        max_length=20,
        choices=Shift.choices,
        blank=True,
        null=True
    )
    assigned_post = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'security'
        verbose_name = 'Security Personnel'
        verbose_name_plural = 'Security Personnel'
    
    def __str__(self):
        return f"{self.security_code} - {self.user.full_name}"


class AuditLog(models.Model):
    """Audit log for tracking user actions."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100)
    table_name = models.CharField(max_length=50, blank=True, null=True)
    record_id = models.PositiveIntegerField(blank=True, null=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at}"
