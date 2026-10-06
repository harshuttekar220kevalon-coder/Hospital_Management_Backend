from django.db import models

class Signup(models.Model):
    USER_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('NURSES', 'Nurses'),
        ('RECEPTIONISTS', 'Receptionists'),
        ('PATIENTS', 'Patients'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    Select_User = models.CharField(max_length=20, choices=USER_CHOICES, blank=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.Select_User})"

    def save(self, *args, **kwargs):
        print(">>> SIGNUP SAVE METHOD CALLED! <<<")  
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            full_name = f"{self.first_name} {self.last_name}"
            role_type = str(self.Select_User).upper().strip()
            
            print(f"DEBUG: Saved Role -> [{role_type}]")

            if role_type in ['DOCTOR', 'DOCTORS']:
                from Super_Admin.models import Doctor
                if not Doctor.objects.filter(email=self.email).exists():
                    try:
                        Doctor.objects.create(name=full_name, email=self.email, password=self.password)
                        print("SUCCESS: Doctor created!")
                    except Exception as e:
                        print("DOCTOR ERROR --->", str(e))

            elif role_type in ['NURSE', 'NURSES']:
                from Super_Admin.models import Nurse 
                if not Nurse.objects.filter(email=self.email).exists():
                    try:
                        Nurse.objects.create(name=full_name, email=self.email, password=self.password)
                        print("SUCCESS: Nurse created!")
                    except Exception as e:
                        print("NURSE ERROR --->", str(e))

            elif role_type in ['RECEPTIONIST', 'RECEPTIONISTS']:
                from Super_Admin.models import Receptionist 
                if not Receptionist.objects.filter(email=self.email).exists():
                    try:
                        Receptionist.objects.create(name=full_name, email=self.email, password=self.password)
                        print("SUCCESS: Receptionist created!")
                    except Exception as e:
                        print("RECEPTIONIST ERROR --->", str(e))

            elif role_type in ['PATIENT', 'PATIENTS']:
                from Super_Admin.models import Patient
                if not Patient.objects.filter(email=self.email).exists():
                    try:
                        Patient.objects.create(name=full_name, email=self.email, password=self.password)
                        print("SUCCESS: Patient successfully created in Super_Admin!")
                    except Exception as e:
                        print("PATIENT ERROR --->", str(e))
                else:
                    print("SKIPPED: Patient already exists!")