from rest_framework import serializers
from .models import Nurse, NurseNotification, Notification, NurseChat


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


class NurseNotificationSerializer(serializers.ModelSerializer):
    """
    Receive-only serializer for Nurse incoming notifications.
    Provides complete notification details including sender, message, timestamps, and read status.
    """
    class Meta:
        model = NurseNotification
        fields = [
            'id',
            'title',
            'message',
            'sender_name',
            'sender_email',
            'sender_role',
            'recipient_name',
            'recipient_email',
            'recipient_role',
            'is_important',
            'is_read',
            'read_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


NotificationSerializer = NurseNotificationSerializer


class NurseChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseChat
        fields = "__all__"

