from rest_framework import serializers
from .models import Nurse, NurseNotification, Notification, NurseChat
from Hospital_Management_App.serializers import NotificationSerializerBase


class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = "__all__"
        extra_kwargs = {
            'role': {'required': False, 'allow_blank': True, 'allow_null': True},
            'ward': {'required': False, 'allow_blank': True, 'allow_null': True},
            'shift': {'required': False, 'allow_blank': True, 'allow_null': True},
            'qualification': {'required': False, 'allow_blank': True, 'allow_null': True},
            'experience': {'required': False, 'allow_blank': True, 'allow_null': True},
            'status': {'required': False, 'allow_blank': True, 'allow_null': True},
            'hospital': {'required': False, 'allow_null': True},
            'nurse_id': {'required': False, 'allow_blank': True},
            'max_patient_capacity': {'required': False, 'allow_null': True},
            'assigned_floor': {'required': False, 'allow_null': True},
        }

    def validate_contact(self, value):
        import re
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return clean

    def validate_email(self, value):
        if not value or not str(value).strip().lower().endswith('@gmail.com'):
            raise serializers.ValidationError("Email must end with @gmail.com.")
        return str(value).strip().lower()


class NurseNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = NurseNotification
        fields = "__all__"


NotificationSerializer = NurseNotificationSerializer


class NurseChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseChat
        fields = "__all__"

