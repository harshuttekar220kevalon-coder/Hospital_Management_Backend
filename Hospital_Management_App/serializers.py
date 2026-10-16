from django.apps import apps
from rest_framework import serializers
from .models import Appointment, Patient, PatientNotification, Notification


class NotificationSerializerBase(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        email = attrs.get('recipient_email', getattr(self.instance, 'recipient_email', None))
        role = attrs.get('recipient_role', getattr(self.instance, 'recipient_role', None))
        if not email and not role:
            raise serializers.ValidationError('Provide recipient_email, recipient_role, or both.')
        return attrs


class PatientNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = PatientNotification
        fields = "__all__"


NotificationSerializer = PatientNotificationSerializer


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"

    def validate_contact(self, value):
        import re
        if not value:
            return value
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return clean

    def validate_email(self, value):
        if not value or not str(value).strip().lower().endswith('@gmail.com'):
            raise serializers.ValidationError("Email must end with @gmail.com.")
        return str(value).strip().lower()


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_Name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        extra_kwargs = {'Appoment_id': {'read_only': True}}

    def validate_contact(self, value):
        import re
        if not value:
            return value
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return clean

    def validate_email(self, value):
        if not value or not str(value).strip().lower().endswith('@gmail.com'):
            raise serializers.ValidationError("Email must end with @gmail.com.")
        return str(value).strip().lower()
