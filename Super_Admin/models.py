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
    departments = models.TextField(blank=True, null=True, help_text="Enter departments separated by commas (e.g. Cardiology, Neurology, Orthopedics)")
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
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE)
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
    hospitals = models.ManyToManyField(Hospitals, related_name='doctors', blank=True)
    name = models.CharField(max_length=100)
    doctor_id = models.CharField(max_length=50, unique=True, blank=True)
    specialization = models.TextField(help_text="Enter one or more specializations")
    additional_skills = models.TextField(blank=True, null=True)
    department = models.TextField(blank=True, null=True, help_text="Enter departments associated with selected hospitals")
    qualification = models.CharField(max_length=150)
    experience = models.CharField(max_length=50)
    opd_timings = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=50, default='Available')
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

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
        return f"{self.name} ({self.specialization}) - {self.doctor_id}"










class Nurse(models.Model):
    ROLE_CHOICES = [
        ('Head Nurse', 'Head Nurse'),
        ('Staff Nurse', 'Staff Nurse'),
        ('ICU Nurse', 'ICU Nurse'),
        ('Emergency Nurse', 'Emergency Nurse'),
        ('OT Nurse', 'OT Nurse'),
        ('Ward Nurse', 'Ward Nurse'),
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
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='Staff Nurse')
    ward = models.CharField(max_length=100, choices=WARD_CHOICES, default='General Ward')
    shift = models.CharField(max_length=100)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='nurse123') 
    status = models.CharField(max_length=50, default='On Duty')
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
    languages = models.CharField(max_length=150, default='English, Hindi')
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='rec123') 
    status = models.CharField(max_length=50, default='Active')
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

    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, related_name='patient_appointments', null=True, blank=True, help_text="Assigned automatically or by receptionist based on availability")
    
    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, unique=True, blank=True)
    
    # Separated age and gender
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Male')
    
    contact = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    visit_date_time = models.DateTimeField(null=True, blank=True) 
    applied_at = models.DateTimeField(auto_now_add=True)
    
    symptoms_diagnosis = models.TextField(help_text="Patient describes symptoms or illness",blank=True,null=True) 
    attached_document = models.FileField(upload_to='patient_documents/', blank=True, null=True, help_text="Upload prescription, photo, or medical PDF report")
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending') 
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            import random
            random_digits = str(random.randint(10000, 99999))
            self.patient_id = f"PAT-{random_digits}"
            while Patient.objects.filter(patient_id=self.patient_id).exists():
                random_digits = str(random.randint(10000, 99999))
                self.patient_id = f"PAT-{random_digits}"
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.patient_id}) - Hospital: {self.hospital}"


    










