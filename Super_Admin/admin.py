from django.contrib import admin
from .models import Hospitals


@admin.register(Hospitals)
class HospitalsAdmin(admin.ModelAdmin):
    search_fields = ("Name", "Branch_Code", "city")
    readonly_fields = ("Branch_Code", "created_at")


