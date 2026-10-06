from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Super_Admin.models import Doctor, Nurse, Receptionist, Patient

@api_view(['POST'])
def user_signup(request):
    data = request.data
    first_name = data.get('firstName') or data.get('first_name', '')
    last_name = data.get('lastName') or data.get('last_name', '')
    email = data.get('email')
    password = data.get('password')
    role = str(data.get('role') or data.get('Select_User', '')).upper().strip()
    
    full_name = f"{first_name} {last_name}".strip()

    if not email or not password or not role:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if role in ['SUPER ADMIN', 'SUPER_ADMIN', 'ADMIN']:
        return Response({
            "error": "Super Admin and Admin accounts cannot be registered via public signup."
        }, status=status.HTTP_403_FORBIDDEN)

    # 1. DOCTOR
    if role in ['DOCTOR', 'DOCTORS']:
        if Doctor.objects.filter(email=email).exists():
            return Response({"error": "Email already registered as Doctor."}, status=status.HTTP_400_BAD_REQUEST)
        user = Doctor.objects.create(name=full_name, email=email, password=password)

    # 2. NURSE
    elif role in ['NURSE', 'NURSES']:
        if Nurse.objects.filter(email=email).exists():
            return Response({"error": "Email already registered as Nurse."}, status=status.HTTP_400_BAD_REQUEST)
        user = Nurse.objects.create(name=full_name, email=email, password=password)

    # 3. RECEPTIONIST
    elif role in ['RECEPTIONIST', 'RECEPTIONISTS']:
        if Receptionist.objects.filter(email=email).exists():
            return Response({"error": "Email already registered as Receptionist."}, status=status.HTTP_400_BAD_REQUEST)
        user = Receptionist.objects.create(name=full_name, email=email, password=password)

    # 4. PATIENT
    elif role in ['PATIENT', 'PATIENTS']:
        if Patient.objects.filter(email=email).exists():
            return Response({"error": "Email already registered as Patient."}, status=status.HTTP_400_BAD_REQUEST)
        user = Patient.objects.create(name=full_name, email=email, password=password)

    else:
        return Response({"error": "Invalid role selected."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Registration successful!",
        "user": {
            "id": user.id,
            "name": full_name,
            "email": email,
            "role": role
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    print(f"\n--- LOGIN ATTEMPT ---")
    print(f"Email entered: {email}")
    print(f"Password entered: {password}")

    if not email or not password:
        return Response({"message": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = None
    role = None
    user_name = ""
    user_id = None

    auth_user = User.objects.filter(email__iexact=email).first()
    if not auth_user:
        auth_user = User.objects.filter(username__iexact=email).first()

    if auth_user:
        print(f"Found in Django User table: {auth_user.username}")
        if auth_user.check_password(password):
            print("Password matched for Admin/Super Admin!")
            user_id = auth_user.id
            user_name = f"{auth_user.first_name} {auth_user.last_name}".strip() or auth_user.username
            role = 'SUPER ADMIN' if auth_user.is_superuser else 'ADMIN'
        else:
            print("Password MISMATCH for Admin/Super Admin!")
    else:
        print("Not found in Django User table, checking role tables...")
        
        # 2. Check Doctor
        doc = Doctor.objects.filter(email__iexact=email, password=password).first()
        if doc:
            print("Matched in Doctor table!")
            user = doc
            role = 'DOCTOR'
        else:
            # 3. Check Nurse
            nurse = Nurse.objects.filter(email__iexact=email, password=password).first()
            if nurse:
                print("Matched in Nurse table!")
                user = nurse
                role = 'NURSES'
            else:
                # 4. Check Receptionist
                rec = Receptionist.objects.filter(email__iexact=email, password=password).first()
                if rec:
                    print("Matched in Receptionist table!")
                    user = rec
                    role = 'RECEPTIONISTS'
                else:
                    # 5. Check Patient
                    pat = Patient.objects.filter(email__iexact=email, password=password).first()
                    if pat:
                        print("Matched in Patient table!")
                        user = pat
                        role = 'PATIENTS'
                    else:
                        print("Email not found in ANY table!")

        if user:
            user_id = user.id
            user_name = user.name

    if role:
        print(f"Login SUCCESS as {role}\n")
        return Response({
            "message": "Login successful",
            "role": role,
            "user": {
                "id": user_id,
                "name": user_name,
                "email": email,
                "role": role
            }
        }, status=status.HTTP_200_OK)

    print("Login FAILED: Invalid credentials\n")
    return Response({"message": "You Have To Ragister Frist If You Dont Have A Account"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def user_reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({"message": "Email and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

    auth_user = User.objects.filter(email__iexact=email).first()
    if not auth_user:
        auth_user = User.objects.filter(username__iexact=email).first()

    if auth_user:
        auth_user.set_password(new_password) 
        auth_user.save()
        return Response({"message": "Password updated successfully for Admin/Super Admin!"}, status=status.HTTP_200_OK)

    user = Doctor.objects.filter(email__iexact=email).first()
    if not user:
        user = Nurse.objects.filter(email__iexact=email).first()
    if not user:
        user = Receptionist.objects.filter(email__iexact=email).first()
    if not user:
        user = Patient.objects.filter(email__iexact=email).first()

    if user:
        user.password = new_password
        user.save()
        return Response({"message": "Password updated successfully!"}, status=status.HTTP_200_OK)

    return Response({"message": "Email not found in records."}, status=status.HTTP_404_NOT_FOUND)