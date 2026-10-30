from django.contrib import admin
from .models import Appointment, Patient, PatientNotification, PatientNotificationReceipt


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
 

@admin.register(PatientNotification)
class PatientNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "sender_name", "sender_role", "recipient_name", "recipient_email", "is_important", "is_read", "read_at", "created_at")
    list_filter = ("is_important", "is_read", "sender_role", "recipient_role")
    search_fields = ("title", "message", "sender_name", "sender_email", "recipient_name", "recipient_email")
    readonly_fields = ("created_at", "updated_at", "read_at")


@admin.register(PatientNotificationReceipt)
class PatientNotificationReceiptAdmin(admin.ModelAdmin):
    list_display = ("notification", "recipient_email", "read_at")
    search_fields = ("recipient_email", "notification__title")