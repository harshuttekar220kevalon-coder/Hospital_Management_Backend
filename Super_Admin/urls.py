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
router.register(r'Hospital', Hospitalsviewset, basename='super-admin-hospital')
router.register(r'hospital', Hospitalsviewset, basename='super-admin-hospital-lower')
router.register(r'hospitals', Hospitalsviewset, basename='super-admin-hospitals')
router.register(r'notifications', NotificationViewSet, basename='super-admin-notification')
router.register(r'Admins', HospitalAdminViewSet, basename='super-admin-admin')

hospital_list = Hospitalsviewset.as_view({
    'get': 'list',
    'post': 'create'
})
hospital_detail = Hospitalsviewset.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

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


urlpatterns = [
    path('Hospital', hospital_list, name='super-admin-hospital-list-noslash'),
    path('Hospital/', hospital_list, name='super-admin-hospital-list'),
    path('Hospital/<int:pk>', hospital_detail, name='super-admin-hospital-detail-noslash'),
    path('Hospital/<int:pk>/', hospital_detail, name='super-admin-hospital-detail'),
    path('hospital', hospital_list, name='super-admin-hospital-lower-list-noslash'),
    path('hospital/', hospital_list, name='super-admin-hospital-lower-list'),
    path('hospital/<int:pk>', hospital_detail, name='super-admin-hospital-lower-detail-noslash'),
    path('hospital/<int:pk>/', hospital_detail, name='super-admin-hospital-lower-detail'),
    path('hospitals', hospital_list, name='super-admin-hospitals-list-noslash'),
    path('hospitals/', hospital_list, name='super-admin-hospitals-list'),
    path('hospitals/<int:pk>', hospital_detail, name='super-admin-hospitals-detail-noslash'),
    path('hospitals/<int:pk>/', hospital_detail, name='super-admin-hospitals-detail'),
    path('', include(router.urls)),
]

