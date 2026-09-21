from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Hospital_Management_App.models import Login

# Register your models here.



class LoginAdmin(UserAdmin):
    # Admin list view me dikhane ke liye
    list_display = ['username', 'Select_User']
    
    # Existing user ko edit karte waqt field dikhane ke liye
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('Select_User',)}),
    )   
    
    # Naya User ADD karte waqt form me field dikhane ke liye
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('Select_User',)}),
    )

admin.site.register(Login, LoginAdmin)