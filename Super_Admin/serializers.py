from rest_framework import serializers
from Super_Admin.models import Hospitals, Notification
from Hospital_Management_App.serializers import NotificationSerializerBase


class Hospitalsserializer(serializers.ModelSerializer):
    class Meta:
        model = Hospitals
        fields = '__all__'
        read_only_fields = ['Branch_Code', 'created_at']


class NotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = Notification
        fields = "__all__"


