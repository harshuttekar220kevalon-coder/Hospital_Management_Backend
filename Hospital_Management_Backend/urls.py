"""
URL configuration for Hospital_Management_Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from Hospital_Management_App.views import (
    AppointmentViewSet,
    NotificationViewSet as PatientNotificationViewSet,
    PatientViewSet,
    create_appointment,
    list_appointments,
    notification_recipients,
    send_notification_message,
    user_login,
    user_reset_password,
    user_signup,
)

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "Hospital Management Backend API",
        "environment": "online" if not request.get_host().startswith(('localhost', '127.0.0.1')) else "offline"
    })

patient_router = DefaultRouter()
patient_router.register('notifications', PatientNotificationViewSet, basename='patient-notification')
patient_router.register('', PatientViewSet, basename='patient')

appointment_router = DefaultRouter()
appointment_router.register('', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', health_check, name='root_health_check'),
    path('api/', health_check, name='api_health_check'),
    path('healthz/', health_check, name='render_health_check'),
    path('admin/', admin.site.urls),
    path('api/login/', user_login, name='user_login'),
    path('api/reset-password/', user_reset_password, name='user_reset_password'),
    path('api/signup/', user_signup, name='user_signup'),
    path('api/notifications/recipients/', notification_recipients, name='notification_recipients'),
    path('api/notifications/send/', send_notification_message, name='send_notification_message'),
    path('api/patients/', include(patient_router.urls)),
    path('api/appointments/create/', create_appointment, name='create_appointment'),
    path('api/appointments/list/', list_appointments, name='list_appointments'),
    path('api/appointments/', include(appointment_router.urls)),
    path('api/admins/', include('Admin.urls')),
    path('api/doctors/', include('Doctor.urls')),
    path('api/nurses/', include('Nurse.urls')),
    path('api/receptionists/', include('Receptionist.urls')),
    path('api/super-admin/', include('Super_Admin.urls')),
]
