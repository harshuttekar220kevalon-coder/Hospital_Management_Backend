from rest_framework import serializers
from Super_Admin.models import Hospitals
from .models import Doctor, Notification
from Hospital_Management_App.serializers import NotificationSerializerBase


class DoctorSerializer(serializers.ModelSerializer):
    hospitals = serializers.PrimaryKeyRelatedField(many=True, queryset=Hospitals.objects.all(), required=False)
    hospital_names = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = "__all__"

    def get_hospital_names(self, obj):
        return [{"id": h.id, "name": h.Name, "branch_code": h.Branch_Code} for h in obj.hospitals.all()]


class NotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = Notification
        fields = "__all__"
