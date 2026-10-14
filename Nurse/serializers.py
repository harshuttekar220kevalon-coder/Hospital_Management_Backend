from rest_framework import serializers
from .models import Nurse, Notification
from Hospital_Management_App.serializers import NotificationSerializerBase


class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = "__all__"


class NotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = Notification
        fields = "__all__"
