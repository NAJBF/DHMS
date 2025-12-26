from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

from .models import User, Student, Proctor, Staff, Security

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a corresponding profile when a User is created.
    """
    if created:
        if instance.role == User.Role.STUDENT:
            Student.objects.create(
                user=instance,
                student_code=f"STU-{instance.id}-{uuid.uuid4().hex[:4].upper()}",
                student_type=Student.StudentType.GOVERNMENT,  # Default
                year_of_study=1,
                semester=1
            )
        elif instance.role == User.Role.PROCTOR:
            Proctor.objects.create(
                user=instance,
                proctor_code=f"PROC-{instance.id}-{uuid.uuid4().hex[:4].upper()}"
            )
        elif instance.role == User.Role.STAFF:
            Staff.objects.create(
                user=instance,
                staff_code=f"STF-{instance.id}-{uuid.uuid4().hex[:4].upper()}"
            )
        elif instance.role == User.Role.SECURITY:
            Security.objects.create(
                user=instance,
                security_code=f"SEC-{instance.id}-{uuid.uuid4().hex[:4].upper()}"
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the corresponding profile when a User is saved.
    """
    if instance.role == User.Role.STUDENT and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == User.Role.PROCTOR and hasattr(instance, 'proctor_profile'):
        instance.proctor_profile.save()
    elif instance.role == User.Role.STAFF and hasattr(instance, 'staff_profile'):
        instance.staff_profile.save()
    elif instance.role == User.Role.SECURITY and hasattr(instance, 'security_profile'):
        instance.security_profile.save()
