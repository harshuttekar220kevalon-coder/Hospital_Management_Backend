from django.db import models
import random




class Hospitals(models.Model):
    Name = models.CharField(max_length=100)
    Branch_Code = models.CharField(max_length=50, unique=True, blank=True)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, null=True)
    registration_no = models.CharField(max_length=50, blank=True, null=True)
    license_no = models.CharField(max_length=50, blank=True, null=True)
    established_year = models.CharField(max_length=10, blank=True, null=True)
    total_beds = models.IntegerField()
    icu_beds = models.IntegerField()
    nicu_beds = models.IntegerField()
    operation_theatres = models.IntegerField()
    ambulances_count = models.IntegerField()
    pharmacy = models.CharField(max_length=100, default='24x7 In-House Pharmacy')
    overview = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
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



class Department(models.Model):
    Hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField()
    created = models.DateField(auto_now_add=True)



    def __str__(self):
        return f'{self.name} - {self.Hospital.Name}'




class HospitalAdmin(models.Model):
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
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
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='doctors')
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=150)
    experience = models.CharField(max_length=50)
    opd_timings = models.CharField(max_length=100)
    chamber = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=50, default='Available') # Available, On Leave, Busy
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.specialization})"











class Nurse(models.Model):
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='nurses', null=True, blank=True)
    name = models.CharField(max_length=100)
    nurse_id = models.CharField(max_length=50, unique=True, blank=True)
    role = models.CharField(max_length=100, default='Staff Nurse') # Staff Nurse, Head Nurse, ICU Specialist
    ward = models.CharField(max_length=100) # e.g. General Ward 2A, ICU, NICU
    shift = models.CharField(max_length=100) # Morning (08:00 AM - 04:00 PM), Night, etc.
    qualification = models.CharField(max_length=150, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=50, default='On Duty') # On Duty, On Leave, Off Shift
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
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='receptionists', null=True, blank=True)
    name = models.CharField(max_length=100)
    receptionist_id = models.CharField(max_length=50, unique=True, blank=True)
    role = models.CharField(max_length=100, default='Front Desk Executive')
    desk = models.CharField(max_length=100) # e.g. Main Lobby Desk 1, Emergency Reception
    shift = models.CharField(max_length=100) # Morning Shift, Evening Shift
    languages = models.CharField(max_length=150, default='English, Hindi')
    extension = models.CharField(max_length=20, blank=True, null=True)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=50, default='Active') # Active, On Leave, Off Duty
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
        return f"{self.name} ({self.role}) - Desk: {self.desk}"    


class Patient(models.Model):
    hospital = models.ForeignKey(Hospitals, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    hospital_admin = models.ForeignKey(HospitalAdmin, on_delete=models.SET_NULL, related_name='managed_patients', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, related_name='patient_appointments', null=True, blank=True)
    
    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, unique=True, blank=True)
    age_gender = models.CharField(max_length=50) # e.g. "32 M" or "28 F"
    contact = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    # Visit & Application Details
    visit_date_time = models.DateTimeField() # Which time / date patient wants to visit
    applied_at = models.DateTimeField(auto_now_add=True) # When he applied
    symptoms_diagnosis = models.TextField(blank=True, null=True)
    
    # Attached documents (file URL or name)
    attached_document = models.CharField(max_length=255, blank=True, null=True) # file name or path
    
    status = models.CharField(max_length=50, default='Pending') # Pending, Confirmed, Admitted, Completed, Cancelled
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            import random
            random_digits = str(random.randint(10000, 99999))
            self.patient_id = f"PAT-{random_digits}"
            while Patient.objects.filter(patient_id=self.patient_id).exists():
                random_digits = str(random.randint(10000, 99999))
                self.patient_id = f"PAT-{random_digits}"
                
        # Automatically map hospital admin if hospital is selected and admin exists for that hospital
        if self.hospital and not self.hospital_admin:
            admin_obj = HospitalAdmin.objects.filter(hospital=self.hospital).first()
            if admin_obj:
                self.hospital_admin = admin_obj
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.patient_id}) - Visit: {self.hospital}"


    










