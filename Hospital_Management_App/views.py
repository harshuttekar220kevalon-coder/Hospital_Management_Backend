from Hospital_Management_App.models import Signup
from Hospital_Management_App.serializers import LoginSerializer, RegisterSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def user_signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "Registration successful!",
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.Select_User
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = Signup.objects.filter(email__iexact=email).first()
    if not user:
        user = Signup.objects.filter(username__iexact=email).first()

    if user and user.check_password(password):
        
        if not user.is_active:
            if user.Select_User == 'ADMIN':
                message = "Your account is deactivated. Please contact Super Admin."
            else:
                message = "Your account is deactivated. Contact your Admin."
                
            return Response({"message": message}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "message": "Login successful",
            "role": user.Select_User,
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "email": user.email,
                "role": user.Select_User
            }
        }, status=status.HTTP_200_OK)


    return Response({"message": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)