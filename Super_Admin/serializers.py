from rest_framework import serializers
from Super_Admin.models import Hospitals, SuperAdminNotification, Notification
from Hospital_Management_App.serializers import NotificationSerializerBase


class Hospitalsserializer(serializers.ModelSerializer):
    Branch_Code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Hospitals
        fields = '__all__'
        read_only_fields = ['created_at']
        extra_kwargs = {
            'emergency_contact': {'required': False, 'allow_blank': True, 'allow_null': True},
            'established_year': {'required': False, 'allow_blank': True, 'allow_null': True},
            'departments': {'required': False, 'allow_blank': True, 'allow_null': True},
            'nicu_beds': {'required': False},
            'restroom_for_relatives': {'required': False},
        }

    def validate_contact(self, value):
        import re
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return clean

    def validate_emergency_contact(self, value):
        import re
        if not value:
            return value
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) < 10 or len(clean) > 12:
            raise serializers.ValidationError("Emergency contact number must be between 10 and 12 digits.")
        return clean

    def validate_Branch_Code(self, value):
        if not value or not str(value).strip():
            return ""
        code = str(value).strip()
        instance = getattr(self, 'instance', None)
        qs = Hospitals.objects.filter(Branch_Code__iexact=code)
        if instance:
            qs = qs.exclude(id=instance.id)
        if qs.exists():
            raise serializers.ValidationError("A hospital with this Branch Code already exists.")
        return code

    def create(self, validated_data):
        if not validated_data.get('Branch_Code'):
            validated_data.pop('Branch_Code', None)
        return super().create(validated_data)

    def validate_email(self, value):
        if not value or not str(value).strip().lower().endswith('@gmail.com'):
            raise serializers.ValidationError("Email must end with @gmail.com.")
        return str(value).strip().lower()



class SuperAdminNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = SuperAdminNotification
        fields = "__all__"


NotificationSerializer = SuperAdminNotificationSerializer



