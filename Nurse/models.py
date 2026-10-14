from django.db import models
import random
from Super_Admin.models import Hospitals
from django.utils import timezone
import uuid

class Nurse(models.Model):
    class Meta:
        db_table = "Super_Admin_nurse"

    ROLE_CHOICES = [
        ('Head Nurse', 'Head Nurse'),
        ('Staff Nurse', 'Staff Nurse'),
    ]

    WARD_CHOICES = [
        ('ICU', 'ICU'),
        ('NICU', 'NICU'),
        ('General Ward', 'General Ward'),
        ('Emergency Ward', 'Emergency Ward'),
        ('Operation Theatre', 'Operation Theatre'),
        ('OPD', 'OPD'),
    ]

    status_choise = [
        ('On_Duty','On_Duty'),
        ('Off_Duty','Off_Duty'),
    ]

    TYMING = [
        ('Morning First Shift', 'Morning First Shift'),
        ('Afternoon Second Shift', 'Afternoon Second Shift'),
        ('Evening Third Shift', 'Evening Third Shift'),
    ]

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='nurses', null=True, blank=True)
    name = models.CharField(max_length=100)
    nurse_id = models.CharField(max_length=50, unique=True, blank=False)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    ward = models.CharField(max_length=100, choices=WARD_CHOICES)
    shift = models.CharField(max_length=100,blank=True,null=True,choices=TYMING)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=12) 
    status = models.CharField(max_length=50,choices=status_choise)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateField(auto_now_add=True)
    max_patient_capacity = models.IntegerField(default=50)
    assigned_floor = models.IntegerField(blank=True,null=True)


    def save(self, *args, **kwargs):
        if not self.nurse_id:
            import random
            random_digits = str(random.randint(1000, 9999))
            self.nurse_id = f"NUR-{random_digits}"
            while Nurse.objects.filter(nurse_id=self.nurse_id).exists():
                random_digits = str(random.randint(1000, 9999))
                self.nurse_id = f"NUR-{random_digits}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.role}) - Ward: {self.ward}"


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
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_nurse_notification_receipt")]
