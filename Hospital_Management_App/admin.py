from django.contrib import admin
from Hospital_Management_App.models import Signup


class SignupAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name', 'Select_User']

admin.site.register(Signup, SignupAdmin)