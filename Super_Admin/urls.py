from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Super_Admin.views import Hospitalsviewset, NotificationViewSet
from Admin.views import HospitalAdminViewSet
from Hospital_Management_App.views import AppointmentViewSet
from Doctor.models import Doctor
from Doctor.serializers import DoctorSerializer
from Nurse.models import Nurse
from Nurse.serializers import NurseSerializer
from Receptionist.models import Receptionist
from Receptionist.serializers import ReceptionistSerializer
from Hospital_Management_App.models import Patient
from Hospital_Management_App.serializers import PatientSerializer
from rest_framework import viewsets

router = DefaultRouter()
router.register(r'Hospital',Hospitalsviewset)
router.register(r'notifications', NotificationViewSet, basename='super-admin-notification')
router.register(r'Admins', HospitalAdminViewSet, basename='super-admin-admin')

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer

class ReceptionistViewSet(viewsets.ModelViewSet):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

router.register(r'Doctors', DoctorViewSet, basename='super-admin-doctor')
router.register(r'Nurses', NurseViewSet, basename='super-admin-nurse')
router.register(r'Receptionists', ReceptionistViewSet, basename='super-admin-receptionist')
router.register(r'Patients', PatientViewSet, basename='super-admin-patient')
router.register(r'appointments', AppointmentViewSet, basename='super-admin-appointment')


urlpatterns =[
    path('',include(router.urls)),
]
