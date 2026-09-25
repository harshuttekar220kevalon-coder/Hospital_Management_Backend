from django.db import models
import random




class Hospitals(models.Model):
    Name = models.CharField(max_length=100)
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





class HospitalAdmin(models.Model):
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE,null=False,blank=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    designation = models.CharField(max_length=100, default='Hospital Administrator')
    employee_id = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

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





class Doctor(models.Model):
    hospitals = models.ManyToManyField(Hospitals, related_name='doctors', blank=False, )
    name = models.CharField(max_length=100)
    doctor_id = models.CharField(max_length=50, unique=True, blank=True)
    specialization = models.TextField(help_text="Enter one or more specializations")
    additional_skills = models.TextField(blank=True, null=True)
    department = models.TextField(blank=True, null=True, default=None)
    qualification = models.CharField(max_length=150)
    experience = models.CharField(max_length=50)
    opd_timings = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=50, default='Available')
    is_active = models.BooleanField(default=True)
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


class Nurse(models.Model):
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

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='nurses', null=True, blank=True)
    name = models.CharField(max_length=100)
    nurse_id = models.CharField(max_length=50, unique=True, blank=False)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    ward = models.CharField(max_length=100, choices=WARD_CHOICES)
    shift = models.CharField(max_length=100)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=12) 
    status = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

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



class Receptionist(models.Model):
    ROLE_CHOICES = [
        ('Front Desk Receptionist', 'Front Desk Receptionist'),
        ('Patient Registration Receptionist', 'Patient Registration Receptionist'),
        ('Appointment Receptionist', 'Appointment Receptionist'),
        ('Admission Receptionist', 'Admission Receptionist'),
        ('Billing Receptionist', 'Billing Receptionist'),
        ('Emergency Receptionist', 'Emergency Receptionist'),
    ]

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='receptionists', null=True, blank=True)
    name = models.CharField(max_length=100)
    receptionist_id = models.CharField(max_length=50, unique=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='Front Desk Receptionist')
    shift = models.CharField(max_length=100) 
    languages = models.CharField(max_length=150)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) 
    status = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receptionist_id:
            import random
            random_digits = str(random.randint(1000, 9999))
            self.receptionist_id = f"REC-{random_digits}"
            while Receptionist.objects.filter(receptionist_id=self.receptionist_id).exists():
                random_digits = str(random.randint(1000, 9999))
                self.receptionist_id = f"REC-{random_digits}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.role})" 


class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ]

    Blood_Group = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    PAYMENT_METHOD = [
        ('UPI', 'Upi'),
        ('Credit Card', 'Credit Card'),
        ('Net Banking', 'Net Banking'),
        ('Cash', 'Cash'),
    ]

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, related_name='patient_appointments', null=True, blank=True, help_text="Assigned automatically or by receptionist based on availability")
    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, unique=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    visit_date_time = models.DateTimeField(null=True, blank=True) 
    applied_at = models.DateTimeField(auto_now_add=True)
    symptoms_diagnosis = models.TextField(help_text="Patient describes symptoms or illness", blank=True, null=True) 
    Blood_Group = models.CharField(max_length=10, choices=Blood_Group, null=True,blank=True)
    attached_document = models.FileField(upload_to='patient_documents/', blank=True, null=True, help_text="Upload prescription, photo, or medical PDF report")
    Hospitals_Chargies = models.DecimalField(max_digits=15, default=0,decimal_places=2)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD,blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES) 
    is_active = models.BooleanField(default=True)

def save(self, *args, **kwargs):
    if not self.patient_id:
        last_patient = Patient.objects.order_by('-id').first()
        if last_patient:
            last_number = int(last_patient.patient_id.split('-')[1])
            next_number = last_number + 1
        else:
            next_number = 1
        self.patient_id = f"PAT-{next_number:04d}"
    super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.patient_id}) - Paid: ₹{self.amount_paid}"
