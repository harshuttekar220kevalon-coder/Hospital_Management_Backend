from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from Doctor.models import Doctor
from Nurse.models import Nurse
from Super_Admin.models import Hospitals

class Patient(models.Model):
    class Meta:
        db_table = "Super_Admin_patient"


    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, unique=True, blank=True)
    address = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient and last_patient.patient_id:
                try:
                    last_number = int(last_patient.patient_id.split('-')[1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1
            self.patient_id = f"PAT-{next_number:04d}"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.patient_id})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'), ('Partial', 'Partial'), ('Pending', 'Pending'), ('Failed', 'Failed'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    PAYMENT_METHOD = [
        ('UPI', 'Upi'), ('Credit Card', 'Credit Card'),
        ('Net Banking', 'Net Banking'), ('Cash', 'Cash'),
    ]
    CONDITION_STATUS = [
        ('Critical', 'Critical'), ('Emergency', 'Emergency'),
        ('Urgent', 'Urgent'), ('Normal', 'Normal'),
    ]
    CHECKUP_STATUS_CHOICES = [('Checkup Done', 'Checkup Done'), ('Pending', 'Pending')]
    GENDER = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    Appoment_id = models.CharField(max_length=10, blank=True)
    patient_Name = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='hospital_appointments', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, related_name='doctor_appointments', null=True, blank=True)
    nurse = models.ForeignKey(Nurse, on_delete=models.SET_NULL, null=True, blank=True)
    visit_date_time = models.DateTimeField(null=True, blank=True)
    Applied_at = models.DateTimeField(blank=True, null=True)
    age = models.CharField(max_length=3, null=True, blank=True)
    symptoms_diagnosis = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    attached_document = models.FileField(upload_to='appointment_documents/', blank=True, null=True)
    contact = models.CharField(max_length=14, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    Gender = models.CharField(null=True, blank=True, choices=GENDER)
    address = models.TextField(null=True, blank=True)
    checkup_status = models.CharField(max_length=50, blank=True, null=True, choices=CHECKUP_STATUS_CHOICES)
    hospitals_charges = models.DecimalField(max_digits=15, default=0, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True, default='Pending')
    condition = models.CharField(choices=CONDITION_STATUS, null=True, blank=True, max_length=40)
    bed_number = models.IntegerField(null=True, blank=True)
    Discharge_DateTime = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Super_Admin_appointment'
        ordering = ['-id']

    @property
    def floor(self):
        if not self.bed_number:
            return 'Not Assigned'
        return f"Floor {((self.bed_number - 1) // 100) + 1}"

    def clean(self):
        super().clean()
        if not self.email:
            raise ValidationError('Appointment booking requires the registered patient email.')
        if not Patient.objects.filter(email__iexact=self.email).exists():
            raise ValidationError('This email does not belong to a registered patient.')

    def save(self, *args, **kwargs):
        if not self.Appoment_id:
            last_appointment = type(self).objects.order_by('-id').first()
            next_id = int(last_appointment.Appoment_id) + 1 if last_appointment and last_appointment.Appoment_id.isdigit() else 1
            self.Appoment_id = str(next_id)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.Appoment_id} - {self.patient_Name}'


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
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_patient_notification_receipt")]
