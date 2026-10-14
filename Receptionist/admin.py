from django.contrib import admin
from .models import Receptionist


@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "receptionist_id", "contact")
    readonly_fields = ("receptionist_id", "created_at")
