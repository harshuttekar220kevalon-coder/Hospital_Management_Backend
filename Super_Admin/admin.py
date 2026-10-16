from django.contrib import admin
from .models import Hospitals, SuperAdminNotification, SuperAdminNotificationReceipt


@admin.register(Hospitals)
class HospitalsAdmin(admin.ModelAdmin):
    search_fields = ("Name", "Branch_Code", "city")
    readonly_fields = ("Branch_Code", "created_at")


@admin.register(SuperAdminNotification)
class SuperAdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "sender_name", "sender_role", "recipient_name", "recipient_email", "recipient_role", "is_important", "is_read", "read_at", "created_at")
    list_filter = ("is_important", "is_read", "sender_role", "recipient_role")
    search_fields = ("title", "message", "sender_name", "sender_email", "recipient_name", "recipient_email")
    readonly_fields = ("created_at", "updated_at", "read_at")


@admin.register(SuperAdminNotificationReceipt)
class SuperAdminNotificationReceiptAdmin(admin.ModelAdmin):
    list_display = ("notification", "recipient_email", "read_at")
    search_fields = ("recipient_email", "notification__title")



