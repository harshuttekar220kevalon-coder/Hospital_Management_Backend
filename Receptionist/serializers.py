from rest_framework import serializers
from .models import Notification, Receptionist
from Hospital_Management_App.serializers import NotificationSerializerBase


class ReceptionistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptionist
        fields = "__all__"


class NotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = Notification
        fields = "__all__"
