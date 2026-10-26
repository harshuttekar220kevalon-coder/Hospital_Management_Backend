from django.contrib import admin
from .models import Nurse, NurseNotification, NurseChat


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "nurse_id", "contact")
    readonly_fields = ("nurse_id", "created_at")


@admin.register(NurseNotification)
class NurseNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "sender_name", "sender_role", "recipient_name", "recipient_email", "recipient_role", "is_important", "is_read", "read_at", "created_at")
    list_filter = ("is_important", "is_read", "sender_role", "recipient_role")
    search_fields = ("title", "message", "sender_name", "sender_email", "recipient_name", "recipient_email")
    readonly_fields = ("created_at", "updated_at", "read_at")


@admin.register(NurseChat)
class NurseChatAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_name", "sender_email", "sender_role", "recipient_name", "recipient_email", "recipient_role", "is_broadcast", "is_read", "hospital", "created_at")
    list_filter = ("is_broadcast", "is_read", "sender_role", "recipient_role", "hospital")
    search_fields = ("sender_name", "sender_email", "recipient_name", "recipient_email", "message")
    readonly_fields = ("created_at", "updated_at", "read_at")
