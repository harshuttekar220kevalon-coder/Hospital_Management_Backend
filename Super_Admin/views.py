from rest_framework import viewsets
from .models import Hospitals, Notification, NotificationReceipt
from .serializers import Hospitalsserializer, NotificationSerializer
from Hospital_Management_App.views import NotificationViewSetBase


class Hospitalsviewset(viewsets.ModelViewSet):
    queryset = Hospitals.objects.all()
    serializer_class = Hospitalsserializer


class NotificationViewSet(NotificationViewSetBase):
    notification_role = "SUPER_ADMIN"
    queryset = Notification.objects.all()
    receipt_model = NotificationReceipt
    serializer_class = NotificationSerializer
