from django.db import models
import random








class Hospitals(models.Model):
    Name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    Branch_Code = models.CharField(max_length=50, unique=True, blank=True) # blank=True zaroori hai
    address = models.TextField()
    contact = models.CharField(max_length=11)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.Branch_Code:
            city_code = self.city[:3].upper()
            area_code = self.area[:3].upper()
            
            random_digits = str(random.randint(1000, 9999))
            
            generated_code = f"{city_code}-{area_code}-{random_digits}"
            
            while Hospitals.objects.filter(Branch_Code=generated_code).exists():
                random_digits = str(random.randint(1000, 9999))
                generated_code = f"{city_code}-{area_code}-{random_digits}"
                
            self.Branch_Code = generated_code
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Name} ({self.Branch_Code})"




  
