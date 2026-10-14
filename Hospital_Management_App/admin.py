from django.contrib import admin
from .models import Appointment, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "patient_id")
    readonly_fields = ("patient_id",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("Appoment_id", "patient_Name", "hospital", "visit_date_time", "status", "payment_status")
    list_filter = ("status", "payment_status", "hospital")
    search_fields = ("Appoment_id", "patient_Name", "email")
    readonly_fields = ("Appoment_id",)
