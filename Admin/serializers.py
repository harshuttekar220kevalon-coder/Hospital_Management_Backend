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

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'phone' in data and ('contact' not in data or not data['contact']):
            data['contact'] = data['phone']
        if 'hospital' in data and isinstance(data['hospital'], dict) and 'id' in data['hospital']:
            data['hospital'] = data['hospital']['id']
        return super().to_internal_value(data)

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
