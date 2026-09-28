from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Hospital_Management_App.models import Login

# Register your models here.



class LoginAdmin(UserAdmin):
    list_display = ['username', 'Select_User']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('Select_User',)}),
    )   
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('Select_User',)}),
    )

admin.site.register(Login, LoginAdmin)