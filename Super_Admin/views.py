from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Super_Admin.models import Appointment, Doctor, HospitalAdmin, Hospitals, Nurse, Patient, Receptionist
from Super_Admin.serializers import AppointmentSerializer, DoctorSerializer, HospitalAdminserializer, Hospitalsserializer, NurseSerializer, PatientSerializer, ReceptionistSerializer


class Hospitalsviewset(viewsets.ModelViewSet):
    queryset = Hospitals.objects.all()
    serializer_class = Hospitalsserializer


class HospitalAdminViewSet(viewsets.ModelViewSet):
    queryset = HospitalAdmin.objects.all()
    serializer_class = HospitalAdminserializer

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        try:
            admin_user = HospitalAdmin.objects.get(email=email)
            admin_user.password = new_password
            admin_user.save()
            return Response({"message": "Hospital Admin password reset successfully!"}, status=200)
        except HospitalAdmin.DoesNotExist:
            return Response({"error": "Hospital Admin with this email not found."}, status=404)




class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


    @action(detail=False, methods=['post'])
    def chno_reset_password(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        try:
            doctor = Doctor.objects.get(email=email)
            doctor.password = new_password
            doctor.save()
            return Response({"message": "Password reset successfully!"}, status=200)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor with this email not found."}, status=404)



class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        try:
            nurse = Nurse.objects.get(email=email)
            nurse.password = new_password
            nurse.save()
            return Response({"message": "Nurse password reset successfully!"}, status=200)
        except Nurse.DoesNotExist:
            return Response({"error": "Nurse with this email not found."}, status=404)


    
class ReceptionistViewSet(viewsets.ModelViewSet):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistSerializer

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        try:
            receptionist = Receptionist.objects.get(email=email)
            receptionist.password = new_password
            receptionist.save()
            return Response({"message": "Password reset successfully!"}, status=200)
        except Receptionist.DoesNotExist:
            return Response({"error": "Receptionist with this email not found."}, status=404)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer



class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('-id')
    serializer_class = AppointmentSerializer


@api_view(['POST'])
def create_appointment(request):
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        appointment = serializer.save()
        return Response({
            "message": "Appointment booked successfully!",
            "appointment_id": appointment.id,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_appointments(request):
    # Optional filter by patient_id if passed in query params (?patient=1)
    patient_id = request.GET.get('patient')
    if patient_id:
        appointments = Appointment.objects.filter(patient_id=patient_id)
    else:
        appointments = Appointment.objects.all()

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)