from django.shortcuts import render
from rest_framework import viewsets
from Hospital_Management_App.models import Login
from Hospital_Management_App.serializers import Loginserializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model


from Super_Admin.models import Doctor, HospitalAdmin, Nurse, Receptionist




class Loginviewset(viewsets.ModelViewSet):
    queryset = Login.objects.all()
    serializer_class = Loginserializer

@api_view(['POST'])
def user_login(api_request):
    email = api_request.data.get('email')
    password = api_request.data.get('password')

    if not email or not password:
        return Response({"message": "Email and password are required."}, status=400)

    User = get_user_model()

    django_user = User.objects.filter(email=email).first()
    if not django_user:
        django_user = User.objects.filter(username=email).first()

    if django_user and django_user.check_password(password):
        if django_user.is_superuser or django_user.is_staff:
            return Response({
                "message": "Login successful",
                "role": "SUPER_ADMIN",
                "user": {
                    "id": django_user.id,
                    "name": getattr(django_user, 'name', None) or django_user.get_full_name() or django_user.username,
                    "email": django_user.email or django_user.username,
                    "role": "SUPER_ADMIN"
                }
            }, status=200)

    user = HospitalAdmin.objects.filter(email=email, password=password).first()
    role = "HOSPITAL_ADMIN" if user else None

    if not user:
        user = Doctor.objects.filter(email=email, password=password).first()
        role = "DOCTOR" if user else None

    if not user:
        user = Nurse.objects.filter(email=email, password=password).first()
        role = "NURSE" if user else None

    if not user:
        user = Receptionist.objects.filter(email=email, password=password).first()
        role = "RECEPTIONIST" if user else None

    if user:
        if not getattr(user, 'is_active', True):
            if role == "HOSPITAL_ADMIN":
                message = "Account is deactivated. Contact Super Admin."
            else:
                message = "Account is deactivated. Contact your Branch Administrator."


            return Response(
                {'message': message}
            )





        return Response({
            "message": "Login successful",
            "role": role,
            "user": {
                "id": user.id,
                "name": getattr(user, 'name', 'User'),
                "email": user.email,
                "role": role,
                "hospital": getattr(user, 'hospital_id', getattr(user, 'hospitals', None))
            }
        }, status=200)
    
    return Response({"message": "Invalid email or password."}, status=401)