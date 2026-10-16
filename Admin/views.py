from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import HospitalAdmin, AdminNotification, AdminNotificationReceipt, Notification, NotificationReceipt, AdminChat
from .serializers import HospitalAdminSerializer, NotificationSerializer, AdminNotificationSerializer, AdminChatSerializer
from Super_Admin.models import Hospitals, SuperAdminNotification
from Doctor.models import Doctor, DoctorChat
from Nurse.models import Nurse, NurseChat
from Receptionist.models import Receptionist, ReceptionistChat


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


class AdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = AdminNotification.objects.all()
    serializer_class = AdminNotificationSerializer

    def get_queryset(self):
        queryset = AdminNotification.objects.all()
        direction = self.request.query_params.get('direction', '').lower()
        email = (
            self.request.query_params.get('recipient_email')
            or self.request.query_params.get('current_email')
            or self.request.query_params.get('sender_email')
            or self.request.query_params.get('email')
            or ''
        ).strip().lower()

        # Admin Flow:
        # 1. 'sent': ONLY notifications sent BY this Admin to staff (Admin is the SENDER)
        if direction == 'sent':
            sent_filter = Q(sender_role__icontains='ADMIN')
            if email:
                sent_filter |= Q(sender_email__iexact=email)
            queryset = queryset.filter(sent_filter).exclude(sender_role__icontains='SUPER').exclude(recipient_role__icontains='SUPER')
            if email:
                queryset = queryset.exclude(recipient_email__iexact=email)

        # 2. 'inbox': ONLY notifications received BY this Admin (e.g. from Super Admin) (Admin is the RECEIVER)
        elif direction == 'inbox':
            inbox_filter = Q(recipient_role__icontains='ADMIN') | Q(sender_role__icontains='SUPER')
            if email:
                inbox_filter |= Q(recipient_email__iexact=email) | Q(recipient_email__icontains=email)
            # Exclude messages sent by this Admin to staff
            queryset = queryset.filter(inbox_filter).exclude(sender_role__iexact='ADMIN')
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

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        email = (request.query_params.get('current_email') or request.query_params.get('recipient_email') or '').strip().lower()
        now = timezone.now()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = now
            notification.save(update_fields=['is_read', 'read_at'])

            # If sender was Super Admin, sync read status to SuperAdminNotification
            if notification.sender_role == 'SUPER_ADMIN':
                try:
                    SuperAdminNotification.objects.filter(
                        Q(recipient_email__iexact=notification.recipient_email) | Q(recipient_role__iexact='ADMIN'),
                        title=notification.title,
                        message=notification.message,
                    ).update(is_read=True, read_at=now)
                except Exception:
                    pass

            try:
                AdminNotificationReceipt.objects.get_or_create(
                    notification=notification,
                    recipient_email=notification.recipient_email or email or 'admin',
                    defaults={'read_at': now}
                )
            except Exception:
                pass

        return Response(self.get_serializer(notification).data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        return self.retrieve(request, pk=pk)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        email = (request.query_params.get('current_email') or request.query_params.get('recipient_email') or '').strip().lower()
        qs = self.get_queryset().filter(is_read=False)
        if email:
            qs = qs.filter(Q(recipient_email__iexact=email) | Q(recipient_role__iexact='ADMIN'))
        return Response({'unread_count': qs.count()})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        email = (request.query_params.get('current_email') or request.query_params.get('recipient_email') or '').strip().lower()
        now = timezone.now()
        qs = self.get_queryset().filter(is_read=False)
        if email:
            qs = qs.filter(Q(recipient_email__iexact=email) | Q(recipient_role__iexact='ADMIN'))
        updated = qs.update(is_read=True, read_at=now)
        return Response({'updated': updated})


NotificationViewSet = AdminNotificationViewSet


class AdminChatViewSet(viewsets.ModelViewSet):
    queryset = AdminChat.objects.all()
    serializer_class = AdminChatSerializer

    def _resolve_hospital(self, email, hospital_id=None):
        if hospital_id:
            h = Hospitals.objects.filter(id=hospital_id).first()
            if h:
                return h
        clean_email = (email or '').strip().lower()
        admin = HospitalAdmin.objects.filter(email__iexact=clean_email).first()
        if admin and admin.hospital:
            return admin.hospital
        return None

    def get_queryset(self):
        email = (
            self.request.query_params.get('current_email')
            or self.request.query_params.get('email')
            or self.request.query_params.get('sender_email')
            or ''
        ).strip().lower()

        hospital_id = self.request.query_params.get('hospital_id')
        hospital = self._resolve_hospital(email, hospital_id)
        if not hospital:
            return AdminChat.objects.none()

        qs = AdminChat.objects.filter(hospital=hospital)
        with_email = (self.request.query_params.get('with_email') or '').strip()

        if with_email:
            if with_email.upper() == 'ALL':
                qs = qs.filter(is_broadcast=True)
            else:
                qs = qs.filter(
                    (Q(sender_email__iexact=email) & Q(recipient_email__iexact=with_email))
                    | (Q(sender_email__iexact=with_email) & Q(recipient_email__iexact=email))
                )
        else:
            qs = qs.filter(
                Q(sender_email__iexact=email)
                | Q(recipient_email__iexact=email)
                | Q(is_broadcast=True)
            )

        return qs.order_by('created_at', 'id').distinct()

    def create(self, request, *args, **kwargs):
        data = request.data
        sender_email = str(data.get('sender_email') or '').strip().lower()
        sender_name = str(data.get('sender_name') or '').strip()
        recipient_email = str(data.get('recipient_email') or '').strip()
        recipient_role = str(data.get('recipient_role') or '').strip().upper()
        recipient_name = str(data.get('recipient_name') or '').strip()
        message_text = str(data.get('message') or '').strip()
        hospital_id = data.get('hospital_id')

        if not sender_email or not message_text:
            return Response({'detail': 'Sender email and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

        hospital = self._resolve_hospital(sender_email, hospital_id)
        if not hospital:
            return Response({'detail': 'Your admin account is not linked to any hospital branch.'}, status=status.HTTP_400_BAD_REQUEST)

        is_broadcast = (recipient_email.upper() == 'ALL' or recipient_role == 'ALL')
        shared = {
            'sender_name': sender_name or sender_email.split('@')[0],
            'sender_email': sender_email,
            'sender_role': 'ADMIN',
            'message': message_text,
            'is_broadcast': is_broadcast,
            'hospital': hospital,
            'hospital_name': hospital.Name,
            'is_read': False,
            'read_at': None,
        }

        with transaction.atomic():
            if is_broadcast:
                created_record = AdminChat.objects.create(
                    recipient_name='All Hospital Staff',
                    recipient_email='ALL',
                    recipient_role='ALL',
                    **shared
                )
                DoctorChat.objects.create(
                    recipient_name='All Hospital Staff',
                    recipient_email='ALL',
                    recipient_role='ALL',
                    **shared
                )
                NurseChat.objects.create(
                    recipient_name='All Hospital Staff',
                    recipient_email='ALL',
                    recipient_role='ALL',
                    **shared
                )
                ReceptionistChat.objects.create(
                    recipient_name='All Hospital Staff',
                    recipient_email='ALL',
                    recipient_role='ALL',
                    **shared
                )
            else:
                created_record = AdminChat.objects.create(
                    recipient_name=recipient_name or recipient_email.split('@')[0],
                    recipient_email=recipient_email.lower(),
                    recipient_role=recipient_role or 'STAFF',
                    **shared
                )
                rec_r = recipient_role.upper()
                if 'DOCTOR' in rec_r:
                    DoctorChat.objects.create(
                        recipient_name=recipient_name or recipient_email.split('@')[0],
                        recipient_email=recipient_email.lower(),
                        recipient_role=recipient_role or 'STAFF',
                        **shared
                    )
                elif 'NURSE' in rec_r:
                    NurseChat.objects.create(
                        recipient_name=recipient_name or recipient_email.split('@')[0],
                        recipient_email=recipient_email.lower(),
                        recipient_role=recipient_role or 'STAFF',
                        **shared
                    )
                elif 'RECEPTION' in rec_r:
                    ReceptionistChat.objects.create(
                        recipient_name=recipient_name or recipient_email.split('@')[0],
                        recipient_email=recipient_email.lower(),
                        recipient_role=recipient_role or 'STAFF',
                        **shared
                    )
                elif 'ADMIN' in rec_r:
                    AdminChat.objects.create(
                        recipient_name=recipient_name or recipient_email.split('@')[0],
                        recipient_email=recipient_email.lower(),
                        recipient_role=recipient_role or 'STAFF',
                        **shared
                    )

        return Response(AdminChatSerializer(created_record).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = None
        for model_cls in (AdminChat, DoctorChat, NurseChat, ReceptionistChat):
            instance = model_cls.objects.filter(pk=pk).first()
            if instance:
                break

        if not instance:
            return Response(status=status.HTTP_204_NO_CONTENT)

        hospital = instance.hospital
        sender_email = (instance.sender_email or '').strip().lower()
        recipient_email = (instance.recipient_email or '').strip().lower()
        msg_text = instance.message
        is_broadcast = instance.is_broadcast
        created_at = instance.created_at

        with transaction.atomic():
            instance.delete()
            for model_cls in (AdminChat, DoctorChat, NurseChat, ReceptionistChat):
                try:
                    qs = model_cls.objects.filter(
                        hospital=hospital,
                        sender_email__iexact=sender_email,
                        message=msg_text,
                    )
                    if is_broadcast:
                        qs = qs.filter(is_broadcast=True)
                    else:
                        qs = qs.filter(recipient_email__iexact=recipient_email)
                    if created_at:
                        qs = qs.filter(created_at__range=(
                            created_at - timezone.timedelta(seconds=60),
                            created_at + timezone.timedelta(seconds=60)
                        ))
                    qs.delete()
                except Exception:
                    pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        email = (request.query_params.get('current_email') or request.query_params.get('email') or '').strip().lower()
        hospital_id = request.query_params.get('hospital_id')
        hospital = self._resolve_hospital(email, hospital_id)
        if not hospital or not email:
            return Response({'unread_count': 0, 'broadcast_unread': 0, 'total': 0})

        direct_unread = AdminChat.objects.filter(
            hospital=hospital,
            recipient_email__iexact=email,
            is_read=False,
            is_broadcast=False
        ).count()
        return Response({
            'unread_count': direct_unread,
            'broadcast_unread': 0,
            'total': direct_unread
        })

    @action(detail=False, methods=['post'], url_path='mark-read')
    def mark_read(self, request):
        user_email = (request.data.get('user_email') or request.data.get('email') or '').strip().lower()
        with_email = (request.data.get('with_email') or '').strip().lower()
        hospital_id = request.data.get('hospital_id')
        hospital = self._resolve_hospital(user_email, hospital_id)
        if not hospital or not user_email or not with_email:
            return Response({'updated': 0})

        now = timezone.now()
        with transaction.atomic():
            updated = AdminChat.objects.filter(
                hospital=hospital,
                sender_email__iexact=with_email,
                recipient_email__iexact=user_email,
                is_read=False,
            ).update(is_read=True, read_at=now)

            for model in (DoctorChat, NurseChat, ReceptionistChat, AdminChat):
                model.objects.filter(
                    hospital=hospital,
                    sender_email__iexact=with_email,
                    recipient_email__iexact=user_email,
                    is_read=False,
                ).update(is_read=True, read_at=now)

        return Response({'message': 'Marked read', 'updated': updated})

    @action(detail=False, methods=['get'], url_path='contacts')
    def contacts(self, request):
        email = (request.query_params.get('email') or request.query_params.get('current_email') or '').strip().lower()
        hospital_id = request.query_params.get('hospital_id')
        hospital = self._resolve_hospital(email, hospital_id)

        if not hospital:
            return Response({'hospital': None, 'admin': None, 'contacts': [], 'can_broadcast': True, 'unread_counts': {}, 'broadcast_unread': 0})

        contacts = []
        for d in Doctor.objects.filter(hospitals=hospital).exclude(email__isnull=True).exclude(email__exact=''):
            if (d.email or '').strip().lower() != email:
                contacts.append({
                    'id': d.pk,
                    'name': d.name or 'Doctor',
                    'email': d.email.strip(),
                    'role': 'DOCTOR',
                    'designation': getattr(d, 'specialization', '') or getattr(d, 'department', '') or 'Doctor',
                    'hospital_id': hospital.id,
                    'hospital_name': hospital.Name,
                })
        for n in Nurse.objects.filter(hospital=hospital).exclude(email__isnull=True).exclude(email__exact=''):
            if (n.email or '').strip().lower() != email:
                contacts.append({
                    'id': n.pk,
                    'name': n.name or 'Nurse',
                    'email': n.email.strip(),
                    'role': 'NURSES',
                    'designation': getattr(n, 'role', '') or getattr(n, 'ward', '') or 'Nurse',
                    'hospital_id': hospital.id,
                    'hospital_name': hospital.Name,
                })
        for r in Receptionist.objects.filter(hospital=hospital).exclude(email__isnull=True).exclude(email__exact=''):
            if (r.email or '').strip().lower() != email:
                contacts.append({
                    'id': r.pk,
                    'name': r.name or 'Receptionist',
                    'email': r.email.strip(),
                    'role': 'RECEPTIONISTS',
                    'designation': getattr(r, 'role', '') or 'Receptionist',
                    'hospital_id': hospital.id,
                    'hospital_name': hospital.Name,
                })

        unread_map = {}
        for u in AdminChat.objects.filter(hospital=hospital, recipient_email__iexact=email, is_read=False, is_broadcast=False):
            s_email = u.sender_email.lower()
            unread_map[s_email] = unread_map.get(s_email, 0) + 1

        contacts.sort(key=lambda x: (x['role'], x['name'].lower()))
        return Response({
            'hospital': {'id': hospital.id, 'name': hospital.Name, 'branch_code': getattr(hospital, 'Branch_Code', '')},
            'admin': None,
            'contacts': contacts,
            'can_broadcast': True,
            'unread_counts': unread_map,
            'broadcast_unread': 0,
        })




