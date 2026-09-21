from django.shortcuts import render
from rest_framework import viewsets, status
from Hospital_Management_App.models import Login
from Hospital_Management_App.serializers import Loginserializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate




class Loginviewset(viewsets.ModelViewSet):
    queryset = Login.objects.all()
    serializer_class = Loginserializer






@api_view(['POST'])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'message': 'Email and password are required!'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Email case-insensitive search (small/capital letters ka issue khatam)
        user_obj = Login.objects.get(email__iexact=email)
        
        # Django ke check_password se password verify karna
        if user_obj.check_password(password):
            return Response({
                'message': 'Login successful!',
                'firstName': user_obj.first_name,
                'role': user_obj.Select_User
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid email or password!'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Login.DoesNotExist:
        return Response({'message': 'Account not found! Please sign up first.'}, status=status.HTTP_404_NOT_FOUND)
