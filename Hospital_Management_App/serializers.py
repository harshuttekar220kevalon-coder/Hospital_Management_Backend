from rest_framework import serializers
from Hospital_Management_App.models import Login


from rest_framework import serializers
from Hospital_Management_App.models import Login

class Loginserializer(serializers.ModelSerializer):
    firstName = serializers.CharField(write_only=True, source='first_name')
    lastName = serializers.CharField(write_only=True, source='last_name')
    role = serializers.CharField(write_only=True, source='Select_User')

    class Meta:
        model = Login
        fields = ['id', 'firstName', 'lastName', 'role', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if Login.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered. Please login instead.")
        return value

    def validate_role(self, value):
        # Website/Frontend se koi bhi Admin ya Super Admin register nahi kar sakta
        if value in ['ADMIN', 'SUPER_ADMIN']:
            raise serializers.ValidationError("Admins can only be created By Super Admin")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        first_name = validated_data.get('first_name')
        
        user = Login(**validated_data)
        user.username = first_name  
        user.set_password(password)
        user.save()
        return user