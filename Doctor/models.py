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
    specialization = models.TextField(help_text="Enter one or more specializations", blank=True, null=True, default='')
    department = models.TextField(blank=True, null=True, default=None)
    qualification = models.CharField(max_length=150,blank=True, null=True)
    experience = models.CharField(max_length=50,blank=True, null=True)
    Shifts = models.CharField(max_length=100,blank=True, null=True,choices=TYMING)
    phone = models.CharField(max_length=20,blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=50, blank=True, null=True, default='')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateField(auto_now_add=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
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


class DoctorNotification(models.Model):
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
        db_table = "Doctor_doctornotification"

    def __str__(self):
        return f"{self.title} (From: {self.sender_email} -> To: {self.recipient_email})"


Notification = DoctorNotification


class DoctorChat(models.Model):
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

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_chats')
    hospital_name = models.CharField(max_length=150, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', 'id']
        db_table = "Doctor_doctorchat"

    def __str__(self):
        return f"[DoctorChat] {self.sender_name} -> {self.recipient_name}: {self.message[:30]}"

