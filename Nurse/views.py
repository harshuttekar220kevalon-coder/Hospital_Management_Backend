from rest_framework import viewsets
from .models import Nurse, Notification, NotificationReceipt
from .serializers import NurseSerializer, NotificationSerializer
from Hospital_Management_App.views import NotificationViewSetBase


class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer


class NotificationViewSet(NotificationViewSetBase):
    notification_role = "NURSES"
    queryset = Notification.objects.all()
    receipt_model = NotificationReceipt
    serializer_class = NotificationSerializer
