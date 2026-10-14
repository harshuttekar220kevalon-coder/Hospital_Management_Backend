from rest_framework import serializers
from .models import HospitalAdmin, Notification
from Hospital_Management_App.serializers import NotificationSerializerBase


class HospitalAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAdmin
        fields = "__all__"


class NotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = Notification
        fields = "__all__"
