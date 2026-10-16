from rest_framework import serializers
from .models import HospitalAdmin, AdminNotification, Notification, AdminChat
from Hospital_Management_App.serializers import NotificationSerializerBase


class HospitalAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAdmin
        fields = "__all__"
        extra_kwargs = {
            'designation': {'required': False, 'allow_blank': True, 'allow_null': True},
            'hospital': {'required': False, 'allow_null': True},
            'employee_id': {'required': False, 'allow_blank': True},
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


class AdminNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = AdminNotification
        fields = "__all__"


NotificationSerializer = AdminNotificationSerializer


class AdminChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminChat
        fields = "__all__"
