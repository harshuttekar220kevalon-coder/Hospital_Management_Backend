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
        ('Not Need For Admitt', 'Not Need For Admitt'),
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
    HEALTH = [
    ('Done', 'Done'),
    ('Not Done', 'Not Done'),
    ('Fully Recovered', 'Fully Recovered'),
    ('Recovering', 'Recovering'),
    ('No Significant Change', 'No Significant Change'),
]
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
    Health_Care = models.CharField(max_length=50, choices=HEALTH, default='Not Done')
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
        if self.email:
            self.email = str(self.email).strip().lower()

    def clean_fields(self, exclude=None):
        if self.contact and len(str(self.contact)) > 14:
            clean_digits = ''.join(c for c in str(self.contact) if c.isdigit())
            self.contact = clean_digits[-10:] if len(clean_digits) >= 10 else clean_digits[:14]

        if self.age and len(str(self.age)) > 3:
            clean_age = ''.join(c for c in str(self.age) if c.isdigit())
            self.age = clean_age[:3] if clean_age else '30'

        if self.status:
            matched_status = None
            for choice, _ in self.STATUS_CHOICES:
                if str(self.status).lower().strip() == choice.lower():
                    matched_status = choice
                    break
            if matched_status:
                self.status = matched_status
            elif 'discharg' in str(self.status).lower():
                self.status = 'Discharged'
            elif 'admit' in str(self.status).lower():
                self.status = 'Admitted'
            else:
                self.status = 'Pending'

        if self.checkup_status and self.checkup_status not in [c[0] for c in self.CHECKUP_STATUS_CHOICES]:
            if 'done' in str(self.checkup_status).lower() or 'completed' in str(self.checkup_status).lower():
                self.checkup_status = 'Checkup Done'
            else:
                self.checkup_status = 'Pending'

        if self.payment_status:
            matched_ps = None
            for choice, _ in self.PAYMENT_STATUS_CHOICES:
                if str(self.payment_status).lower().strip() == choice.lower():
                    matched_ps = choice
                    break
            if matched_ps:
                self.payment_status = matched_ps
            else:
                self.payment_status = 'Pending'

        if self.payment_method:
            matched_pm = None
            for choice, _ in self.PAYMENT_METHOD:
                if str(self.payment_method).lower().strip() == choice.lower():
                    matched_pm = choice
                    break
            if matched_pm:
                self.payment_method = matched_pm
            elif 'card' in str(self.payment_method).lower():
                self.payment_method = 'Credit Card'
            elif 'upi' in str(self.payment_method).lower() or 'qr' in str(self.payment_method).lower():
                self.payment_method = 'UPI'
            elif 'bank' in str(self.payment_method).lower():
                self.payment_method = 'Net Banking'
            else:
                self.payment_method = 'Cash'

        if self.Health_Care:
            matched_hc = None
            for choice, _ in self.HEALTH:
                if str(self.Health_Care).lower().strip() == choice.lower():
                    matched_hc = choice
                    break
            if matched_hc:
                self.Health_Care = matched_hc
            elif 'recover' in str(self.Health_Care).lower() or 'done' in str(self.Health_Care).lower():
                self.Health_Care = 'Fully Recovered'
            else:
                self.Health_Care = 'Not Done'

        if self.blood_group and self.blood_group not in [c[0] for c in self.BLOOD_GROUP_CHOICES]:
            clean_bg = str(self.blood_group).strip().upper().replace(' ', '')
            matched_bg = next((c[0] for c in self.BLOOD_GROUP_CHOICES if c[0] == clean_bg), None)
            self.blood_group = matched_bg or 'O+'

        if self.condition and self.condition not in [c[0] for c in self.CONDITION_STATUS]:
            matched_cond = next((c[0] for c in self.CONDITION_STATUS if c[0].lower() == str(self.condition).lower().strip()), None)
            self.condition = matched_cond or 'Normal'

        super().clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        if not self.Appoment_id:
            last_appointment = type(self).objects.order_by('-id').first()
            next_id = int(last_appointment.Appoment_id) + 1 if last_appointment and last_appointment.Appoment_id.isdigit() else 1
            self.Appoment_id = str(next_id)
        if not self.Applied_at:
            self.Applied_at = timezone.now()
        if not self.visit_date_time:
            self.visit_date_time = timezone.now()
        try:
            self.full_clean()
        except ValidationError:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.Appoment_id} - {self.patient_Name}'


class PatientNotification(models.Model):
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
        db_table = "Hospital_Management_App_patientnotification"

    def __str__(self):
        return f"{self.title} (From: {self.sender_email} -> To: {self.recipient_email})"


class PatientNotificationReceipt(models.Model):
    notification = models.ForeignKey(PatientNotification, on_delete=models.CASCADE, related_name="receipts")
    recipient_email = models.EmailField(db_index=True)
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "Hospital_Management_App_patientnotificationreceipt"
        constraints = [models.UniqueConstraint(fields=("notification", "recipient_email"), name="uniq_patient_notification_receipt")]

    def __str__(self):
        return f"Receipt for {self.notification_id} by {self.recipient_email}"


Notification = PatientNotification
NotificationReceipt = PatientNotificationReceipt

