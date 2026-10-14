from django.db import models
import random
from Super_Admin.models import Hospitals
from django.utils import timezone
import uuid


class HospitalAdmin(models.Model):
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, null=True, blank=True) 
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    designation = models.CharField(max_length=100, default='Hospital Administrator')
    employee_id = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Super_Admin_hospitaladmin"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            random_digits = str(random.randint(1000, 9999))
            self.employee_id = f"ADM-{random_digits}"
            while HospitalAdmin.objects.filter(employee_id=self.employee_id).exists():
                random_digits = str(random.randint(1000, 9999))
                self.employee_id = f"ADM-{random_digits}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.hospital.Name}"

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
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_admin_notification_receipt")]
