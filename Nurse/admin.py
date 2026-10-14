from django.contrib import admin
from .models import Nurse


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "nurse_id", "contact")
    readonly_fields = ("nurse_id", "created_at")

