from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Hospital_Management_App.models import Signup


class SignupAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'Select_User', 'is_active']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('Select_User',)}),
    )   
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('Select_User',)}),
    )

admin.site.register(Signup, SignupAdmin)