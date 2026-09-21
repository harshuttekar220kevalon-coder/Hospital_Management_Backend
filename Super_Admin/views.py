from django.shortcuts import render
from rest_framework import viewsets

from Super_Admin.models import Department, Doctor, HospitalAdmin, Hospitals, Nurse, Patient, Receptionist
from Super_Admin.serializers import Departmentserializer, DoctorSerializer, HospitalAdminserializer, Hospitalsserializer, NurseSerializer, PatientSerializer, ReceptionistSerializer






class Hospitalsviewset(viewsets.ModelViewSet):
    queryset = Hospitals.objects.all()
    serializer_class = Hospitalsserializer






class Departmentviewset(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = Departmentserializer



class HospitalAdminViewSet(viewsets.ModelViewSet):
    queryset = HospitalAdmin.objects.all()
    serializer_class = HospitalAdminserializer




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
    queryset = Patient.objects.all().order_by('-applied_at')
    serializer_class = PatientSerializer
