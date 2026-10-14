from rest_framework import viewsets
from .models import Notification, NotificationReceipt, Receptionist
from .serializers import NotificationSerializer, ReceptionistSerializer
from Hospital_Management_App.views import NotificationViewSetBase


class ReceptionistViewSet(viewsets.ModelViewSet):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistSerializer


class NotificationViewSet(NotificationViewSetBase):
    notification_role = "RECEPTIONISTS"
    queryset = Notification.objects.all()
    receipt_model = NotificationReceipt
    serializer_class = NotificationSerializer
