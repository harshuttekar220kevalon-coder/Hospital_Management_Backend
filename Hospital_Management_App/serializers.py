from django.apps import apps
from rest_framework import serializers
from .models import Appointment, Notification, Patient


class NotificationSerializerBase(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        for field in getattr(self.Meta, 'read_only_fields', ('id', 'created_at', 'updated_at')):
            extra_kwargs[field] = {**extra_kwargs.get(field, {}), 'read_only': True}
        return extra_kwargs

    def _recipient_email(self):
        request = self.context.get('request')
        if not request:
            return ''
        from .views import notification_identity
        identity = notification_identity(request)
        return identity['email'] if identity else ''

    def _receipt(self, obj):
        email = self._recipient_email()
        if not email:
            return None
        receipt_model = apps.get_model(self.Meta.model._meta.app_label, 'NotificationReceipt')
        return receipt_model.objects.filter(notification=obj, recipient_email__iexact=email).first()

    def get_is_read(self, obj):
        email = self._recipient_email().lower()
        if obj.sender_email and obj.sender_email.lower() == email and (obj.recipient_email or '').lower() != email:
            return True
        return self._receipt(obj) is not None

    def get_read_at(self, obj):
        receipt = self._receipt(obj)
        return receipt.read_at if receipt else None

    def validate(self, attrs):
        email = attrs.get('recipient_email', getattr(self.instance, 'recipient_email', None))
        role = attrs.get('recipient_role', getattr(self.instance, 'recipient_role', None))
        if not email and not role:
            raise serializers.ValidationError('Provide recipient_email, recipient_role, or both.')
        return attrs


class NotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = Notification
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_Name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        extra_kwargs = {'Appoment_id': {'read_only': True}}
