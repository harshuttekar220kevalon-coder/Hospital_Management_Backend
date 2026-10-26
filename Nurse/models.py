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
    nurse_id = models.CharField(max_length=50, unique=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, blank=True, null=True, default='')
    ward = models.CharField(max_length=100, choices=WARD_CHOICES, blank=True, null=True, default='')
    shift = models.CharField(max_length=100,blank=True,null=True,choices=TYMING)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) 
    status = models.CharField(max_length=50, choices=status_choise, blank=True, null=True, default='')
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


class NurseNotification(models.Model):
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
        db_table = "Nurse_nursenotification"

    def __str__(self):
        return f"{self.title} (From: {self.sender_email} -> To: {self.recipient_email})"


Notification = NurseNotification


class NurseChat(models.Model):
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

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, null=True, blank=True, related_name='nurse_chats')
    hospital_name = models.CharField(max_length=150, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', 'id']
        db_table = "Nurse_nursechat"

    def __str__(self):
        return f"[NurseChat] {self.sender_name} -> {self.recipient_name}: {self.message[:30]}"

