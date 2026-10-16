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
            try:
                self.nicu_beds = max(0, int(self.total_beds) - int(self.icu_beds))
            except (ValueError, TypeError):
                self.nicu_beds = 0

        if not self.Branch_Code or not str(self.Branch_Code).strip():
            city_code = str(self.city or 'GEN').strip()[:3].upper() if self.city else 'GEN'
            area_code = str(self.area or 'GEN').strip()[:3].upper() if self.area else 'GEN'
            random_digits = str(random.randint(1000, 9999))
            generated_code = f"{city_code}-{area_code}-{random_digits}"
            
            while Hospitals.objects.filter(Branch_Code=generated_code).exists():
                random_digits = str(random.randint(1000, 9999))
                generated_code = f"{city_code}-{area_code}-{random_digits}"
                
            self.Branch_Code = generated_code
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Name} ({self.Branch_Code})"


class SuperAdminNotification(models.Model):
    sender_email = models.EmailField(blank=True, null=True, db_index=True)
    sender_name = models.CharField(max_length=150, blank=True)
    sender_role = models.CharField(max_length=50, blank=True, db_index=True)

    recipient_email = models.EmailField(blank=True, null=True, db_index=True)
    recipient_name = models.CharField(max_length=150, blank=True)
    recipient_role = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    title = models.CharField(max_length=200)
    message = models.TextField()
    is_important = models.BooleanField(default=False, db_index=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        db_table = "Super_Admin_superadminnotification"

    def __str__(self):
        return f"{self.title} (From: {self.sender_email} -> To: {self.recipient_email})"


class SuperAdminNotificationReceipt(models.Model):
    notification = models.ForeignKey(SuperAdminNotification, on_delete=models.CASCADE, related_name="receipts")
    recipient_email = models.EmailField(db_index=True)
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Super_Admin_superadminnotificationreceipt"
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_superadmin_notification_receipt")]

    def __str__(self):
        return f"Receipt for {self.notification_id} by {self.recipient_email}"


Notification = SuperAdminNotification
NotificationReceipt = SuperAdminNotificationReceipt

