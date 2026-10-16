from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Hospitals, SuperAdminNotification, SuperAdminNotificationReceipt, Notification, NotificationReceipt
from .serializers import Hospitalsserializer, NotificationSerializer, SuperAdminNotificationSerializer


from rest_framework.renderers import JSONRenderer


class Hospitalsviewset(viewsets.ModelViewSet):
    queryset = Hospitals.objects.all()
    serializer_class = Hospitalsserializer
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            if hasattr(data, 'dict'):
                data = data.dict()
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            if instance.established_year:
                data['established_year'] = instance.established_year
            serializer = self.get_serializer(instance, data=data, partial=partial)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class SuperAdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = SuperAdminNotification.objects.all()
    serializer_class = SuperAdminNotificationSerializer

    def get_queryset(self):
        queryset = SuperAdminNotification.objects.all()
        direction = self.request.query_params.get('direction', '').lower()
        email = (
            self.request.query_params.get('sender_email')
            or self.request.query_params.get('current_email')
            or self.request.query_params.get('recipient_email')
            or ''
        ).strip().lower()

        # 1. 'sent': ONLY notifications where Super Admin is the SENDER
        if direction == 'sent':
            sent_filter = Q(sender_role__icontains='SUPER')
            if email:
                sent_filter |= Q(sender_email__iexact=email) | Q(sender_email__icontains='super')
            queryset = queryset.filter(sent_filter).exclude(recipient_role__icontains='SUPER')
            if email:
                queryset = queryset.exclude(recipient_email__iexact=email)

        # 2. 'inbox': ONLY notifications where Super Admin is the RECEIVER (exclude sent by Super Admin)
        elif direction == 'inbox':
            inbox_filter = Q(recipient_role__icontains='SUPER')
            if email:
                inbox_filter |= Q(recipient_email__iexact=email) | Q(recipient_email__icontains='super')
            queryset = queryset.filter(inbox_filter).exclude(sender_role__icontains='SUPER')
            if email:
                queryset = queryset.exclude(sender_email__iexact=email)

        if self.request.query_params.get('important', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_important=True)
        if self.request.query_params.get('unread_only', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_read=False)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        now = timezone.now()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = now
            notification.save(update_fields=['is_read', 'read_at'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        now = timezone.now()
        updated = self.get_queryset().filter(is_read=False).update(is_read=True, read_at=now)
        return Response({'updated': updated})


NotificationViewSet = SuperAdminNotificationViewSet

