from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Super_Admin.views import  DoctorViewSet, HospitalAdminViewSet, Hospitalsviewset, NurseViewSet, PatientViewSet, ReceptionistViewSet
from Super_Admin import views

router = DefaultRouter()
router.register(r'Hospital',Hospitalsviewset)
router.register(r'Admins', HospitalAdminViewSet)
router.register(r'Doctors', DoctorViewSet)
router.register(r'Nurses', NurseViewSet)
router.register(r'Receptionists', ReceptionistViewSet)
router.register(r'Patients', PatientViewSet)


urlpatterns =[
    path('',include(router.urls)),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/list/', views.list_appointments, name='list_appointments'),
]