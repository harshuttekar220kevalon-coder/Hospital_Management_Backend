from rest_framework import serializers
from Super_Admin.models import Hospitals
from .models import Doctor, DoctorNotification, Notification, DoctorChat


class DoctorSerializer(serializers.ModelSerializer):
    hospitals = serializers.PrimaryKeyRelatedField(many=True, queryset=Hospitals.objects.all(), required=False)
    hospital_names = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = "__all__"
        extra_kwargs = {
            'specialization': {'required': False, 'allow_blank': True, 'allow_null': True},
            'department': {'required': False, 'allow_blank': True, 'allow_null': True},
            'qualification': {'required': False, 'allow_blank': True, 'allow_null': True},
            'experience': {'required': False, 'allow_blank': True, 'allow_null': True},
            'Shifts': {'required': False, 'allow_blank': True, 'allow_null': True},
            'phone': {'required': False, 'allow_blank': True, 'allow_null': True},
            'status': {'required': False, 'allow_blank': True, 'allow_null': True},
            'consultation_fee': {'required': False, 'allow_null': True},
        }

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'contact' in data and ('phone' not in data or not data['phone']):
            data['phone'] = data['contact']
        if 'hospital' in data and ('hospitals' not in data or not data['hospitals']):
            hosp = data['hospital']
            if isinstance(hosp, dict) and 'id' in hosp:
                data['hospitals'] = [hosp['id']]
            elif hosp:
                data['hospitals'] = [hosp]
            else:
                data['hospitals'] = []
        elif 'hospitals' in data and isinstance(data['hospitals'], list):
            data['hospitals'] = [
                h['id'] if isinstance(h, dict) and 'id' in h else h
                for h in data['hospitals']
                if h is not None
            ]
        return super().to_internal_value(data)

    def get_hospital_names(self, obj):
        return [{"id": h.id, "name": h.Name, "branch_code": h.Branch_Code} for h in obj.hospitals.all()]

    def validate_phone(self, value):
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


class DoctorNotificationSerializer(serializers.ModelSerializer):
    """
    Receive-only serializer for Doctor incoming notifications.
    Provides complete notification details including sender, message, timestamps, and read status.
    """
    class Meta:
        model = DoctorNotification
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


NotificationSerializer = DoctorNotificationSerializer


class DoctorChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorChat
        fields = "__all__"

