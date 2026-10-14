from rest_framework import viewsets
from .models import Doctor, Notification, NotificationReceipt
from .serializers import DoctorSerializer, NotificationSerializer
from Hospital_Management_App.views import NotificationViewSetBase


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class NotificationViewSet(NotificationViewSetBase):
    notification_role = "DOCTOR"
    queryset = Notification.objects.all()
    receipt_model = NotificationReceipt
    serializer_class = NotificationSerializer
