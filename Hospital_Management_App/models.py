from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.





class Login(AbstractUser):
    USER_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('NURSES', 'Nurses'),
        ('RECEPTIONISTS', 'Receptionists'),
        ('PATIENTS', 'Patients'),
    ]

    Select_User = models.CharField(max_length=20, choices=USER_CHOICES, blank=False)

    def __str__(self):
        name = self.first_name if self.first_name else self.username
        role = self.Select_User if self.Select_User else 'USER'
        return f"{name} ({role})"