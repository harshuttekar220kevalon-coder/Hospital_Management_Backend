from django.db import models
from django.utils import timezone
import uuid
import random

class Hospitals(models.Model):
    Name = models.CharField(max_length=100, unique=True)
    Branch_Code = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    established_year = models.CharField(max_length=10, blank=True, null=True)
    total_beds = models.IntegerField()
    icu_beds = models.IntegerField()
    operation_theatres = models.IntegerField()
    nicu_beds = models.IntegerField(default=0, blank=True)
    restroom_for_relatives = models.IntegerField(default=0)
    ambulances_count = models.IntegerField()
    departments = models.TextField(blank=True, null=True, help_text="You Can enter Multy Departments")
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.total_beds is not None and self.icu_beds is not None:
            self.nicu_beds = max(0, self.total_beds - self.icu_beds)

        if not self.Branch_Code:
            city_code = self.city[:3].upper() if self.city else 'GEN'
            area_code = self.area[:3].upper() if self.area else 'GEN'
            random_digits = str(random.randint(1000, 9999))
            generated_code = f"{city_code}-{area_code}-{random_digits}"
            
            while Hospitals.objects.filter(Branch_Code=generated_code).exists():
                random_digits = str(random.randint(1000, 9999))
                generated_code = f"{city_code}-{area_code}-{random_digits}"
                
            self.Branch_Code = generated_code
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Name} ({self.Branch_Code})"


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
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_superadmin_notification_receipt")]
