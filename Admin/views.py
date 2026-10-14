from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import HospitalAdmin, Notification, NotificationReceipt
from .serializers import HospitalAdminSerializer, NotificationSerializer
from Hospital_Management_App.views import NotificationViewSetBase


class HospitalAdminViewSet(viewsets.ModelViewSet):
    queryset = HospitalAdmin.objects.all()
    serializer_class = HospitalAdminSerializer

    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        if not email or not new_password:
            return Response({"error": "Email and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
        user = HospitalAdmin.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"error": "Hospital Admin with this email not found."}, status=status.HTTP_404_NOT_FOUND)
        user.password = new_password
        user.save(update_fields=["password"])
        return Response({"message": "Hospital Admin password reset successfully."})


class NotificationViewSet(NotificationViewSetBase):
    notification_role = "ADMIN"
    queryset = Notification.objects.all()
    receipt_model = NotificationReceipt
    serializer_class = NotificationSerializer


