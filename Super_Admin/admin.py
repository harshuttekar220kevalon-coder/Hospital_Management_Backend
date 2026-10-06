from django.contrib import admin
from Super_Admin.models import  Appointment, Doctor, HospitalAdmin, Hospitals, Nurse, Patient, Receptionist


@admin.register(Hospitals)
class HospitalsAdmin(admin.ModelAdmin):
    search_fields = ('Name', 'Branch_Code', 'city')
    readonly_fields =('Branch_Code','created_at')

admin.site.register(HospitalAdmin)


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    earch_fields = ('name', 'nurse_id', 'email', 'contact')
    readonly_fields = ('nurse_id', 'created_at')


admin.site.register(Receptionist)

@admin.register(Patient)
class patientAdmin(admin.ModelAdmin):
    readonly_fields = ('patient_id',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email', 'specialization', 'doctor_id')
    readonly_fields = ('doctor_id', 'created_at')
admin.site.register(Appointment)
