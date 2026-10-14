from django.db import models
from Super_Admin.models import Hospitals
from django.utils import timezone
import uuid

class Receptionist(models.Model):
    class Meta:
        db_table = "Super_Admin_receptionist"

    ROLE_CHOICES = [
        ('Front Desk Receptionist', 'Front Desk Receptionist'),
        ('Patient Registration Receptionist', 'Patient Registration Receptionist'),
        ('Appointment Receptionist', 'Appointment Receptionist'),
        ('Admission Receptionist', 'Admission Receptionist'),
        ('Billing Receptionist', 'Billing Receptionist'),
        ('Emergency Receptionist', 'Emergency Receptionist'),
    ]
    TYMING = [
        ('Morning First Shift', 'Morning First Shift'),
        ('Afternoon Second Shift', 'Afternoon Second Shift'),
        ('Evening Third Shift', 'Evening Third Shift'),
    ]
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='receptionists', null=True, blank=True)
    name = models.CharField(max_length=100)
    receptionist_id = models.CharField(max_length=50, unique=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES,blank=True,null=True)
    shift = models.CharField(max_length=100,blank=True,null=True,choices=TYMING) 
    languages = models.CharField(max_length=150)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) 
    status = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receptionist_id:
            import random
            random_digits = str(random.randint(1000, 9999))
            self.receptionist_id = f"REC-{random_digits}"
            while Receptionist.objects.filter(receptionist_id=self.receptionist_id).exists():
                random_digits = str(random.randint(1000, 9999))
                self.receptionist_id = f"REC-{random_digits}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Notification(models.Model):
    CATEGORY_CHOICES = [(value, value.title()) for value in ("SYSTEM", "ACCOUNT", "APPOINTMENT", "BILLING", "GENERAL")]
    recipient_email = models.EmailField(blank=True, null=True, db_index=True)
    recipient_role = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    sender_email = models.EmailField(blank=True, null=True, db_index=True)
    sender_name = models.CharField(max_length=100, blank=True)
    sender_role = models.CharField(max_length=32, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="GENERAL")
    title = models.CharField(max_length=160)
    message = models.TextField()
    message_id = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)
    thread_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    reply_to = models.UUIDField(blank=True, null=True, db_index=True)
    is_important = models.BooleanField(default=False, db_index=True)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class NotificationReceipt(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="receipts")
    recipient_email = models.EmailField(db_index=True)
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_receptionist_notification_receipt")]
