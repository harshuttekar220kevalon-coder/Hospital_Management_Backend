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
    designation = models.CharField(max_length=100, blank=True, null=True, default='')
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

class AdminNotification(models.Model):
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
        db_table = "Admin_adminnotification"

    def __str__(self):
        return f"{self.title} (From: {self.sender_email} -> To: {self.recipient_email})"


class AdminNotificationReceipt(models.Model):
    notification = models.ForeignKey(AdminNotification, on_delete=models.CASCADE, related_name="receipts")
    recipient_email = models.EmailField(db_index=True)
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Admin_adminnotificationreceipt"
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_admin_notification_receipt")]

    def __str__(self):
        return f"Receipt for {self.notification_id} by {self.recipient_email}"


Notification = AdminNotification
NotificationReceipt = AdminNotificationReceipt


class AdminChat(models.Model):
    sender_name = models.CharField(max_length=150)
    sender_email = models.EmailField(db_index=True)
    sender_role = models.CharField(max_length=50, db_index=True)

    recipient_name = models.CharField(max_length=150, blank=True, default='')
    recipient_email = models.CharField(max_length=254, db_index=True)
    recipient_role = models.CharField(max_length=50, db_index=True)

    message = models.TextField()
    is_broadcast = models.BooleanField(default=False, db_index=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_chats')
    hospital_name = models.CharField(max_length=150, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', 'id']
        db_table = "Admin_adminchat"

    def __str__(self):
        return f"[AdminChat] {self.sender_name} -> {self.recipient_name}: {self.message[:30]}"

