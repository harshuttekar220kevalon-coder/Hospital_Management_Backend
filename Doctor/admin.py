from django.contrib import admin
from .models import Doctor, DoctorNotification, DoctorNotificationReceipt, DoctorChat


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "specialization", "doctor_id")
    readonly_fields = ("doctor_id", "created_at")


@admin.register(DoctorNotification)
class DoctorNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "sender_name", "sender_role", "recipient_name", "recipient_email", "recipient_role", "is_important", "is_read", "read_at", "created_at")
    list_filter = ("is_important", "is_read", "sender_role", "recipient_role")
    search_fields = ("title", "message", "sender_name", "sender_email", "recipient_name", "recipient_email")
    readonly_fields = ("created_at", "updated_at", "read_at")


@admin.register(DoctorNotificationReceipt)
class DoctorNotificationReceiptAdmin(admin.ModelAdmin):
    list_display = ("notification", "recipient_email", "read_at")
    search_fields = ("recipient_email", "notification__title")


@admin.register(DoctorChat)
class DoctorChatAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_name", "sender_email", "sender_role", "recipient_name", "recipient_email", "recipient_role", "is_broadcast", "is_read", "hospital", "created_at")
    list_filter = ("is_broadcast", "is_read", "sender_role", "recipient_role", "hospital")
    search_fields = ("sender_name", "sender_email", "recipient_name", "recipient_email", "message")
    readonly_fields = ("created_at", "updated_at", "read_at")
