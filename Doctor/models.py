from django.db import models
import random
from Super_Admin.models import Hospitals
from django.utils import timezone
import uuid

class Doctor(models.Model):
    class Meta:
        db_table = "Super_Admin_doctor"



    TYMING = [
        ('Morning First Shift', 'Morning First Shift'),
        ('Afternoon Second Shift', 'Afternoon Second Shift'),
        ('Evening Third Shift', 'Evening Third Shift'),
    ]
    hospitals = models.ManyToManyField(Hospitals, related_name='doctors', blank=False, )
    name = models.CharField(max_length=100)
    doctor_id = models.CharField(max_length=50, unique=True, blank=True)
    specialization = models.TextField(help_text="Enter one or more specializations")
    department = models.TextField(blank=True, null=True, default=None)
    qualification = models.CharField(max_length=150,blank=True, null=True)
    experience = models.CharField(max_length=50,blank=True, null=True)
    Shifts = models.CharField(max_length=100,blank=True, null=True,choices=TYMING)
    phone = models.CharField(max_length=20,blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=50, default='Available')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateField(auto_now_add=True)
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            import random
            random_digits = str(random.randint(1000, 9999))
            self.doctor_id = f"DOC-{random_digits}"
            while Doctor.objects.filter(doctor_id=self.doctor_id).exists():
                random_digits = str(random.randint(1000, 9999))
                self.doctor_id = f"DOC-{random_digits}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.doctor_id}"


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
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_doctor_notification_receipt")]
