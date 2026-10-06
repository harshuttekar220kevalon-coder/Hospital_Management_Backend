from rest_framework import serializers
from Hospital_Management_App.models import Signup

class RegisterSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(write_only=True, source='first_name')
    lastName = serializers.CharField(write_only=True, source='last_name')
    role = serializers.CharField(write_only=True, source='Select_User')
    confirm_password = serializers.CharField(write_only=True)  
    
    class Meta:
        model = Signup
        fields = ['id', 'firstName', 'lastName', 'role', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if Signup.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered. Please login instead.")
        return value

    def validate_role(self, value):
        allowed_roles = ['DOCTOR', 'NURSES', 'RECEPTIONISTS', 'PATIENTS', 'ADMIN', 'SUPER_ADMIN']
        
        if value not in allowed_roles:
            raise serializers.ValidationError("Invalid role selected.")
        return value

    def validate(self, data):
        if data.get('password') != data.pop('confirm_password', None):
            raise serializers.ValidationError({"confirm_password": "Password and Confirm Password must be same."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        
        user = Signup(**validated_data, password=password)
        user.save()
        return user


# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=100, write_only=True, required=True)