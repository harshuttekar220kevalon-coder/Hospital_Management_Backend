from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "specialization", "doctor_id")
    readonly_fields = ("doctor_id", "created_at")

