from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import Nurse, NurseNotification, Notification, NurseChat
from .serializers import NurseSerializer, NotificationSerializer, NurseNotificationSerializer, NurseChatSerializer
from Super_Admin.models import Hospitals
from Admin.models import HospitalAdmin, AdminNotification, AdminChat
from Doctor.models import Doctor, DoctorChat
from Receptionist.models import Receptionist, ReceptionistChat


class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer


class NurseNotificationViewSet(viewsets.ModelViewSet):
    """
    Receive-only ViewSet for Nurse notifications.
    Nurses only receive notifications from Admin / Super Admin.
    Sending and direct edits are disabled.
    """
    queryset = NurseNotification.objects.all()
    serializer_class = NurseNotificationSerializer

    def get_queryset(self):
        queryset = NurseNotification.objects.all()
        email = (
            self.request.query_params.get('recipient_email')
            or self.request.query_params.get('current_email')
            or self.request.query_params.get('email')
            or ''
        ).strip().lower()

        # Nurse only receives incoming notifications addressed to their email or role
        if email:
            queryset = queryset.filter(
                Q(recipient_email__iexact=email) |
                Q(recipient_role__iexact='NURSES') |
                Q(recipient_role__iexact='NURSE')
            )
        else:
            role = (self.request.query_params.get('recipient_role') or '').strip().upper()
            if role in ('NURSE', 'NURSES'):
                queryset = queryset.filter(Q(recipient_role__iexact='NURSES') | Q(recipient_role__iexact='NURSE'))
            else:
                queryset = NurseNotification.objects.none()

        if self.request.query_params.get('important', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_important=True)
        if self.request.query_params.get('unread_only', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_read=False)
        return queryset

    # Block sending notifications - Nurse is receive-only
    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Nurses can only receive notifications. Sending notifications is not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # Block direct modifications
    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Direct notification modification is not permitted.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Direct notification modification is not permitted.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        now = timezone.now()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = now
            notification.save(update_fields=['is_read', 'read_at'])

            # Sync read status to AdminNotification so Admin sees that Nurse has read it
            if notification.sender_role in ('ADMIN', 'SUPER_ADMIN'):
                try:
                    AdminNotification.objects.filter(
                        Q(recipient_email__iexact=notification.recipient_email) | Q(recipient_role__iexact='NURSES') | Q(recipient_role__iexact='NURSE'),
                        title=notification.title,
                        message=notification.message,
                    ).update(is_read=True, read_at=now)
                except Exception:
                    pass

        return Response(self.get_serializer(notification).data)

    @action(detail=True, methods=['post', 'get'])
    def mark_read(self, request, pk=None):
        return self.retrieve(request, pk=pk)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        now = timezone.now()
        updated = self.get_queryset().filter(is_read=False).update(is_read=True, read_at=now)
        return Response({'updated': updated})


NotificationViewSet = NurseNotificationViewSet


class NurseChatViewSet(viewsets.ModelViewSet):
    queryset = NurseChat.objects.all()
    serializer_class = NurseChatSerializer

    def _resolve_hospital(self, email, hospital_id=None):
        clean_email = (email or '').strip().lower()
        if hospital_id:
            try:
                h = Hospitals.objects.filter(id=int(hospital_id)).first()
                if h:
                    return h
            except (ValueError, TypeError):
                pass
        nurse = Nurse.objects.filter(email__iexact=clean_email).first()
        if nurse and nurse.hospital:
            return nurse.hospital
        admin = HospitalAdmin.objects.filter(email__iexact=clean_email).first()
        if admin and admin.hospital:
            return admin.hospital
        doc = Doctor.objects.filter(email__iexact=clean_email).first()
        if doc and doc.hospitals.exists():
            return doc.hospitals.first()
        rec = Receptionist.objects.filter(email__iexact=clean_email).first()
        if rec and rec.hospital:
            return rec.hospital
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
            return NurseChat.objects.none()

        qs = NurseChat.objects.filter(hospital=hospital)
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

        is_broadcast = (recipient_email.upper() == 'ALL' or recipient_role == 'ALL')
        if is_broadcast:
            return Response({'detail': 'Only Hospital Admins are allowed to broadcast messages to All staff.'}, status=status.HTTP_400_BAD_REQUEST)

        hospital = self._resolve_hospital(sender_email, hospital_id)
        if not hospital:
            return Response({'detail': 'Your account is not linked to any hospital branch.'}, status=status.HTTP_400_BAD_REQUEST)

        shared = {
            'sender_name': sender_name or sender_email.split('@')[0],
            'sender_email': sender_email,
            'sender_role': 'NURSES',
            'message': message_text,
            'is_broadcast': False,
            'hospital': hospital,
            'hospital_name': hospital.Name,
            'is_read': False,
            'read_at': None,
        }

        with transaction.atomic():
            created_record = NurseChat.objects.create(
                recipient_name=recipient_name or recipient_email.split('@')[0],
                recipient_email=recipient_email.lower(),
                recipient_role=recipient_role or 'STAFF',
                **shared
            )
            rec_r = recipient_role.upper()
            if 'ADMIN' in rec_r:
                AdminChat.objects.create(
                    recipient_name=recipient_name or recipient_email.split('@')[0],
                    recipient_email=recipient_email.lower(),
                    recipient_role=recipient_role or 'ADMIN',
                    **shared
                )
            elif 'DOCTOR' in rec_r:
                DoctorChat.objects.create(
                    recipient_name=recipient_name or recipient_email.split('@')[0],
                    recipient_email=recipient_email.lower(),
                    recipient_role=recipient_role or 'DOCTOR',
                    **shared
                )
            elif 'NURSE' in rec_r:
                NurseChat.objects.create(
                    recipient_name=recipient_name or recipient_email.split('@')[0],
                    recipient_email=recipient_email.lower(),
                    recipient_role=recipient_role or 'NURSES',
                    **shared
                )
            elif 'RECEPTION' in rec_r:
                ReceptionistChat.objects.create(
                    recipient_name=recipient_name or recipient_email.split('@')[0],
                    recipient_email=recipient_email.lower(),
                    recipient_role=recipient_role or 'RECEPTIONISTS',
                    **shared
                )

        return Response(NurseChatSerializer(created_record).data, status=status.HTTP_201_CREATED)

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

        direct_unread = NurseChat.objects.filter(
            hospital=hospital,
            recipient_email__iexact=email,
            is_read=False,
            is_broadcast=False
        ).count()
        broadcast_unread = NurseChat.objects.filter(
            hospital=hospital,
            is_broadcast=True,
            is_read=False
        ).count()
        return Response({
            'unread_count': direct_unread,
            'broadcast_unread': broadcast_unread,
            'total': direct_unread + broadcast_unread
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
            if with_email == 'all':
                updated = NurseChat.objects.filter(
                    hospital=hospital,
                    is_broadcast=True,
                    is_read=False,
                ).update(is_read=True, read_at=now)
            else:
                updated = NurseChat.objects.filter(
                    hospital=hospital,
                    sender_email__iexact=with_email,
                    recipient_email__iexact=user_email,
                    is_read=False,
                ).update(is_read=True, read_at=now)

                for model in (AdminChat, DoctorChat, NurseChat, ReceptionistChat):
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
            return Response({'hospital': None, 'admin': None, 'contacts': [], 'can_broadcast': False, 'unread_counts': {}, 'broadcast_unread': 0})

        admin_list = []
        for a in HospitalAdmin.objects.filter(hospital=hospital).exclude(email__isnull=True).exclude(email__exact=''):
            admin_list.append({
                'id': a.pk,
                'name': a.name or 'Hospital Admin',
                'email': a.email.strip(),
                'role': 'ADMIN',
                'designation': getattr(a, 'designation', '') or 'Hospital Administrator',
                'hospital_id': hospital.id,
                'hospital_name': hospital.Name,
            })
        primary_admin = admin_list[0] if admin_list else {
            'id': 0,
            'name': f"{hospital.Name} Admin",
            'email': f"admin_{hospital.id}@hospital.com",
            'role': 'ADMIN',
            'designation': 'Hospital Administrator',
            'hospital_id': hospital.id,
            'hospital_name': hospital.Name,
        }

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
        for a in admin_list:
            if a['email'].lower() != email:
                contacts.append(a)

        unread_map = {}
        for u in NurseChat.objects.filter(hospital=hospital, recipient_email__iexact=email, is_read=False, is_broadcast=False):
            s_email = u.sender_email.lower()
            unread_map[s_email] = unread_map.get(s_email, 0) + 1

        broadcast_unread = NurseChat.objects.filter(
            hospital=hospital,
            is_broadcast=True,
            is_read=False,
        ).count()

        contacts.sort(key=lambda x: (x['role'], x['name'].lower()))
        return Response({
            'hospital': {'id': hospital.id, 'name': hospital.Name, 'branch_code': getattr(hospital, 'Branch_Code', '')},
            'admin': primary_admin,
            'contacts': contacts,
            'can_broadcast': False,
            'unread_counts': unread_map,
            'broadcast_unread': broadcast_unread,
        })

