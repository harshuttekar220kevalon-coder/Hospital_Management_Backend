from django.contrib import admin
from Super_Admin.models import Notification, NotificationReceipt
from .models import HospitalAdmin


@admin.register(HospitalAdmin)
class HospitalAdminAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "employee_id")
    readonly_fields = ("employee_id", "created_at")

admin.site.register(Notification)
admin.site.register(NotificationReceipt)