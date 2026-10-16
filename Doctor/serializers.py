from rest_framework import serializers
from Super_Admin.models import Hospitals
from .models import Doctor, DoctorNotification, Notification, DoctorChat
from Hospital_Management_App.serializers import NotificationSerializerBase


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
            'doctor_id': {'required': False, 'allow_blank': True},
        }

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


class DoctorNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = DoctorNotification
        fields = "__all__"


NotificationSerializer = DoctorNotificationSerializer


class DoctorChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorChat
        fields = "__all__"

