from rest_framework import serializers
from .models import Receptionist, ReceptionistNotification, Notification, ReceptionistChat
from Hospital_Management_App.serializers import NotificationSerializerBase


class ReceptionistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptionist
        fields = "__all__"
        extra_kwargs = {
            'role': {'required': False, 'allow_blank': True, 'allow_null': True},
            'shift': {'required': False, 'allow_blank': True, 'allow_null': True},
            'languages': {'required': False, 'allow_blank': True, 'allow_null': True},
            'status': {'required': False, 'allow_blank': True, 'allow_null': True},
            'hospital': {'required': False, 'allow_null': True},
            'receptionist_id': {'required': False, 'allow_blank': True},
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


class ReceptionistNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = ReceptionistNotification
        fields = "__all__"


NotificationSerializer = ReceptionistNotificationSerializer


class ReceptionistChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionistChat
        fields = "__all__"

