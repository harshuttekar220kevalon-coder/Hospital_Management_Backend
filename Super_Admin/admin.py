from django.contrib import admin

from Super_Admin.models import Department, Doctor, HospitalAdmin, Hospitals, Nurse, Patient, Receptionist

# Register your models here.



admin.site.register(Hospitals)
admin.site.register(Department)
admin.site.register(HospitalAdmin)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Receptionist)
admin.site.register(Patient)
