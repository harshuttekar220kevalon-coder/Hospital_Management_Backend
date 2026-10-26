from django.apps import apps
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core import signing
from django.db import IntegrityError, transaction, connection
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Appointment, Patient, PatientNotification, PatientNotificationReceipt
from .serializers import AppointmentSerializer, PatientSerializer, PatientNotificationSerializer
from Admin.models import HospitalAdmin
from Doctor.models import Doctor
from Nurse.models import Nurse
from Receptionist.models import Receptionist


def _model_set_password(self, raw_password):
    self.password = raw_password


def _model_check_password(self, raw_password):
    if not self.password:
        return False
    if self.password == raw_password:
        return True
    try:
        if check_password(raw_password, self.password):
            return True
    except Exception:
        pass
    return False


for _cls in (HospitalAdmin, Doctor, Nurse, Receptionist, Patient):
    if not hasattr(_cls, 'set_password'):
        _cls.set_password = _model_set_password
    if not hasattr(_cls, 'check_password'):
        _cls.check_password = _model_check_password


def _notification_identity(email, role):
    token = signing.dumps({"email": email, "role": role}, salt="hospital-notification-identity")
    return token


ROLE_ACCOUNTS = {
    'PATIENTS': ('Hospital_Management_App', 'Patient'),
    'DOCTOR': ('Doctor', 'Doctor'),
    'NURSES': ('Nurse', 'Nurse'),
    'RECEPTIONISTS': ('Receptionist', 'Receptionist'),
    'ADMIN': ('Admin', 'HospitalAdmin'),
    'SUPER_ADMIN': ('auth', 'User'),
}
ROLE_NOTIFICATION_APPS = {
    'PATIENTS': 'Hospital_Management_App',
    'DOCTOR': 'Doctor',
    'NURSES': 'Nurse',
    'RECEPTIONISTS': 'Receptionist',
    'ADMIN': 'Admin',
    'SUPER_ADMIN': 'Super_Admin',
}
ROLE_NOTIFICATION_MODELS = {
    'PATIENTS': ('Hospital_Management_App', 'PatientNotification'),
    'DOCTOR': ('Doctor', 'DoctorNotification'),
    'NURSES': ('Nurse', 'NurseNotification'),
    'RECEPTIONISTS': ('Receptionist', 'ReceptionistNotification'),
    'ADMIN': ('Admin', 'AdminNotification'),
    'SUPER_ADMIN': ('Super_Admin', 'SuperAdminNotification'),
}
ROLE_ALIASES = {
    'PATIENT': 'PATIENTS', 'PATIENTS': 'PATIENTS',
    'DOCTOR': 'DOCTOR', 'DOCTORS': 'DOCTOR',
    'NURSE': 'NURSES', 'NURSES': 'NURSES',
    'RECEPTIONIST': 'RECEPTIONISTS', 'RECEPTIONISTS': 'RECEPTIONISTS',
    'ADMIN': 'ADMIN', 'HOSPITAL ADMIN': 'ADMIN', 'HOSPITALADMIN': 'ADMIN',
    'SUPER ADMIN': 'SUPER_ADMIN', 'SUPER_ADMIN': 'SUPER_ADMIN', 'SUPERADMIN': 'SUPER_ADMIN',
}


def normalize_role(value):
    return ROLE_ALIASES.get(str(value or '').strip().upper())


_tables_ensured = False


def ensure_notification_tables():
    global _tables_ensured
    if _tables_ensured:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing = {row[0] for row in cursor.fetchall()}

            # Drop unnecessary receipt tables for receive-only roles (Doctor, Nurse, Receptionist)
            for drop_tbl in [
                "Doctor_doctornotificationreceipt", "Doctor_notificationreceipt",
                "Nurse_nursenotificationreceipt", "Nurse_notificationreceipt",
                "Receptionist_receptionistnotificationreceipt", "Receptionist_notificationreceipt"
            ]:
                cursor.execute(f'DROP TABLE IF EXISTS "{drop_tbl}";')

            tables = [
                ("Super_Admin_superadminnotification", "Super_Admin_notification", "Super_Admin_superadminnotificationreceipt", "Super_Admin_notificationreceipt"),
                ("Admin_adminnotification", "Admin_notification", "Admin_adminnotificationreceipt", "Admin_notificationreceipt"),
                ("Hospital_Management_App_patientnotification", "Hospital_Management_App_notification", "Hospital_Management_App_patientnotificationreceipt", "Hospital_Management_App_notificationreceipt"),
            ]

            # Notification-only tables for receive-only roles (No receipt tables)
            receive_only_tables = [
                ("Doctor_doctornotification", "Doctor_notification"),
                ("Nurse_nursenotification", "Nurse_notification"),
                ("Receptionist_receptionistnotification", "Receptionist_notification"),
            ]

            for notif_tbl, old_notif_tbl in receive_only_tables:
                if notif_tbl not in existing:
                    if old_notif_tbl in existing:
                        cursor.execute(f'ALTER TABLE "{old_notif_tbl}" RENAME TO "{notif_tbl}";')
                        existing.add(notif_tbl)
                    else:
                        cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS "{notif_tbl}" (
                                "id" integer PRIMARY KEY AUTOINCREMENT,
                                "sender_email" varchar(254),
                                "sender_name" varchar(150) NOT NULL DEFAULT '',
                                "sender_role" varchar(50) NOT NULL DEFAULT '',
                                "recipient_email" varchar(254),
                                "recipient_name" varchar(150) NOT NULL DEFAULT '',
                                "recipient_role" varchar(50),
                                "title" varchar(200) NOT NULL,
                                "message" text NOT NULL,
                                "is_important" bool NOT NULL DEFAULT 0,
                                "is_read" bool NOT NULL DEFAULT 0,
                                "read_at" datetime,
                                "created_at" datetime NOT NULL,
                                "updated_at" datetime NOT NULL
                            );
                        ''')
                        existing.add(notif_tbl)

            for notif_tbl, old_notif_tbl, rcpt_tbl, old_rcpt_tbl in tables:
                if notif_tbl not in existing:
                    if old_notif_tbl in existing:
                        cursor.execute(f'ALTER TABLE "{old_notif_tbl}" RENAME TO "{notif_tbl}";')
                        existing.add(notif_tbl)
                    else:
                        cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS "{notif_tbl}" (
                                "id" integer PRIMARY KEY AUTOINCREMENT,
                                "sender_email" varchar(254),
                                "sender_name" varchar(150) NOT NULL DEFAULT '',
                                "sender_role" varchar(50) NOT NULL DEFAULT '',
                                "recipient_email" varchar(254),
                                "recipient_name" varchar(150) NOT NULL DEFAULT '',
                                "recipient_role" varchar(50),
                                "title" varchar(200) NOT NULL,
                                "message" text NOT NULL,
                                "is_important" bool NOT NULL DEFAULT 0,
                                "is_read" bool NOT NULL DEFAULT 0,
                                "read_at" datetime,
                                "created_at" datetime NOT NULL,
                                "updated_at" datetime NOT NULL
                            );
                        ''')
                        existing.add(notif_tbl)

                if rcpt_tbl not in existing:
                    if old_rcpt_tbl in existing:
                        cursor.execute(f'ALTER TABLE "{old_rcpt_tbl}" RENAME TO "{rcpt_tbl}";')
                        existing.add(rcpt_tbl)
                    else:
                        cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS "{rcpt_tbl}" (
                                "id" integer PRIMARY KEY AUTOINCREMENT,
                                "recipient_email" varchar(254) NOT NULL,
                                "read_at" datetime NOT NULL,
                                "notification_id" bigint NOT NULL REFERENCES "{notif_tbl}" ("id") DEFERRABLE INITIALLY DEFERRED
                            );
                        ''')
                        existing.add(rcpt_tbl)
        _tables_ensured = True
    except Exception:
        pass


try:
    ensure_notification_tables()
except Exception:
    pass


def get_role_account(role, email):
    app_label, model_name = ROLE_ACCOUNTS.get(role, ('', ''))
    if not app_label:
        return None
    model = apps.get_model(app_label, model_name)
    if role == 'SUPER_ADMIN':
        account = model.objects.filter(email__iexact=email).first()
        if not account:
            account = model.objects.filter(username__iexact=email).first()
        if not account:
            account = model.objects.filter(is_superuser=True).first()
        return account
    account = model.objects.filter(email__iexact=email).first()
    if not account and hasattr(model, 'username'):
        account = model.objects.filter(username__iexact=email).first()
    return account


def get_role_name(account):
    if not account:
        return ''
    if hasattr(account, 'name') and account.name:
        return account.name
    first = getattr(account, 'first_name', '')
    last = getattr(account, 'last_name', '')
    full = f'{first} {last}'.strip()
    if full:
        return full
    return getattr(account, 'username', '') or getattr(account, 'email', '')


def notification_identity(request):
    authorization = request.META.get('HTTP_AUTHORIZATION', '')
    scheme, _, token = authorization.partition(' ')
    role = None
    email = None
    if scheme.lower() == 'bearer' and token:
        try:
            identity = signing.loads(token, salt='hospital-notification-identity', max_age=60 * 60 * 24 * 30)
            role = normalize_role(identity.get('role'))
            email = str(identity.get('email') or '').strip()
        except signing.BadSignature:
            role = None
            email = None
    if not role or not email:
        email = (
            request.query_params.get('current_email')
            or request.query_params.get('recipient_email')
            or request.query_params.get('sender_email')
            or request.query_params.get('email')
            or request.data.get('sender_email')
            or request.data.get('recipient_email')
            or request.data.get('email')
            or ''
        ).strip()
        role = normalize_role(
            request.query_params.get('current_role')
            or request.query_params.get('recipient_role')
            or request.query_params.get('sender_role')
            or request.query_params.get('role')
            or request.data.get('sender_role')
            or request.data.get('recipient_role')
            or request.data.get('role')
        )
    if not email:
        return None
    return {'role': role or '', 'email': email}


def require_notification_identity(request):
    identity = notification_identity(request)
    if not identity:
        email = (
            request.query_params.get('recipient_email')
            or request.query_params.get('current_email')
            or request.query_params.get('sender_email')
            or request.query_params.get('email')
            or request.data.get('sender_email')
            or request.data.get('recipient_email')
            or ''
        ).strip()
        if email:
            return {'role': '', 'email': email}, None
        return None, Response({'detail': 'Sign in again to use notifications.'}, status=status.HTTP_401_UNAUTHORIZED)
    return identity, None


class NotificationViewSetBase(viewsets.ModelViewSet):
    notification_role = None
    receipt_model = None

    def _require_recipient(self):
        email = (
            self.request.query_params.get('recipient_email')
            or self.request.query_params.get('current_email')
            or self.request.query_params.get('sender_email')
            or self.request.query_params.get('email')
            or ''
        ).strip()
        if email:
            return email, None
        identity, error = require_notification_identity(self.request)
        if error:
            return None, error
        return identity['email'], None

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def retrieve(self, request, *args, **kwargs):
        email, error = self._require_recipient()
        if error:
            return error
        notification = self.get_object()
        is_incoming = (notification.recipient_email or '').lower() == email.lower() or (
            notification.recipient_email is None and notification.recipient_role == self.notification_role
        )
        if is_incoming and not notification.is_read:
            now = timezone.now()
            notification.is_read = True
            notification.read_at = now
            notification.save(update_fields=['is_read', 'read_at'])

            # Sync read status to sender's copy
            sender_role = notification.sender_role
            if sender_role in ROLE_NOTIFICATION_MODELS:
                app_label, model_name = ROLE_NOTIFICATION_MODELS[sender_role]
                try:
                    s_model = apps.get_model(app_label, model_name)
                    s_model.objects.filter(
                        sender_email__iexact=notification.sender_email,
                        recipient_email__iexact=notification.recipient_email,
                        title=notification.title,
                        message=notification.message,
                    ).update(is_read=True, read_at=now)
                except Exception:
                    pass

        if self.receipt_model:
            try:
                self.receipt_model.objects.get_or_create(notification=notification, recipient_email=email)
            except Exception:
                pass
        return Response(self.get_serializer(notification).data)

    def perform_create(self, serializer):
        raise PermissionDenied('Use the notification message endpoint to send messages.')

    def perform_update(self, serializer):
        raise PermissionDenied('Notifications cannot be edited.')

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Notifications cannot be deleted.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        ensure_notification_tables()
        queryset = super().get_queryset()
        email = (
            self.request.query_params.get('recipient_email')
            or self.request.query_params.get('current_email')
            or self.request.query_params.get('sender_email')
            or self.request.query_params.get('email')
            or ''
        ).strip().lower()
        identity = notification_identity(self.request)
        if identity and not email:
            email = identity.get('email', '').strip().lower()

        direction = self.request.query_params.get('direction', '').lower()
        target_role = self.notification_role or self.request.query_params.get('recipient_role') or self.request.query_params.get('current_role') or ''

        if direction == 'sent':
            sender_email = (self.request.query_params.get('sender_email') or email).strip().lower()
            if sender_email:
                sent_filter = (
                    Q(sender_email__iexact=sender_email) |
                    Q(sender_email__icontains=sender_email)
                )
                if target_role == 'SUPER_ADMIN':
                    sent_filter |= Q(sender_role__iexact='SUPER_ADMIN')
                queryset = queryset.filter(sent_filter)
                if email:
                    queryset = queryset.exclude(recipient_email__iexact=email)
            elif target_role == 'SUPER_ADMIN':
                queryset = queryset.filter(Q(sender_role__iexact='SUPER_ADMIN'))
        elif direction == 'inbox':
            if email:
                inbox_filter = (
                    Q(recipient_email__iexact=email) |
                    Q(recipient_email__iexact=email.strip()) |
                    Q(recipient_email__iexact=email.lower()) |
                    Q(recipient_email__icontains=email) |
                    Q(recipient_email__isnull=True) |
                    Q(recipient_email='')
                )
                if target_role:
                    inbox_filter |= Q(recipient_role__iexact=target_role)
                queryset = queryset.filter(inbox_filter).exclude(sender_email__iexact=email)
            elif target_role:
                queryset = queryset.filter(Q(recipient_role__iexact=target_role) | Q(recipient_email__isnull=True) | Q(recipient_email=''))
        else:
            if email:
                participant_filter = (
                    Q(recipient_email__iexact=email) |
                    Q(recipient_email__iexact=email.strip()) |
                    Q(recipient_email__iexact=email.lower()) |
                    Q(recipient_email__icontains=email) |
                    Q(sender_email__iexact=email) |
                    Q(sender_email__iexact=email.strip()) |
                    Q(sender_email__iexact=email.lower()) |
                    Q(recipient_email__isnull=True) |
                    Q(recipient_email='')
                )
                if target_role:
                    participant_filter |= Q(recipient_role__iexact=target_role)
                queryset = queryset.filter(participant_filter)
            elif target_role:
                queryset = queryset.filter(Q(recipient_role__iexact=target_role) | Q(sender_role__iexact=target_role))

        if self.request.query_params.get('important', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_important=True)
        if self.request.query_params.get('unread_only', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_read=False)
        return queryset

    def _inbox_queryset(self, email):
        clean_email = (email or '').strip().lower()
        target_role = self.notification_role or ''
        incoming = (
            Q(recipient_email__iexact=clean_email) |
            Q(recipient_email__iexact=clean_email.strip()) |
            Q(recipient_email__icontains=clean_email) |
            Q(recipient_email__isnull=True) |
            Q(recipient_email='')
        )
        if target_role:
            incoming |= Q(recipient_role__iexact=target_role)
        return self.get_queryset().filter(incoming)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        email, error = self._require_recipient()
        if error:
            return error
        notification = self.get_object()
        now = timezone.now()
        notification.is_read = True
        notification.read_at = now
        notification.save(update_fields=['is_read', 'read_at'])

        # Sync read status to sender's copy
        sender_role = notification.sender_role
        if sender_role in ROLE_NOTIFICATION_MODELS:
            app_label, model_name = ROLE_NOTIFICATION_MODELS[sender_role]
            try:
                s_model = apps.get_model(app_label, model_name)
                s_model.objects.filter(
                    sender_email__iexact=notification.sender_email,
                    recipient_email__iexact=notification.recipient_email,
                    title=notification.title,
                    message=notification.message,
                ).update(is_read=True, read_at=now)
            except Exception:
                pass

        if self.receipt_model:
            try:
                self.receipt_model.objects.get_or_create(notification=notification, recipient_email=email)
            except Exception:
                pass
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        email, error = self._require_recipient()
        if error:
            return error
        now = timezone.now()
        count = self._inbox_queryset(email).filter(is_read=False).update(is_read=True, read_at=now)
        return Response({'updated': count})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        email, error = self._require_recipient()
        if error:
            return error
        unread_count = self._inbox_queryset(email).filter(is_read=False).count()
        return Response({'unread_count': unread_count})


@api_view(['GET'])
def notification_recipients(request):
    ensure_notification_tables()
    current_email = request.query_params.get('current_email', '').strip()
    sender_role = normalize_role(request.query_params.get('current_role') or request.query_params.get('role'))
    if sender_role == 'SUPER_ADMIN' and not current_email:
        current_email = 'superadmin@hospital.com'
    if not current_email or not sender_role:
        identity, error = require_notification_identity(request)
        if identity:
            current_email = current_email or identity.get('email', '')
            sender_role = sender_role or identity.get('role', '')
        elif not current_email and sender_role != 'SUPER_ADMIN':
            return error
    search = request.query_params.get('search', '').strip().lower()
    results = []

    # 1. Super Admin: Can ONLY send messages to Hospital Admins
    if sender_role == 'SUPER_ADMIN':
        admins = HospitalAdmin.objects.all().exclude(email__isnull=True).exclude(email__exact='')
        for admin in admins:
            email = (admin.email or '').strip()
            if not email:
                continue
            name = get_role_name(admin) or getattr(admin, 'name', '') or email.split('@')[0]
            hospital_name = admin.hospital.Name if (getattr(admin, 'hospital', None) and getattr(admin.hospital, 'Name', None)) else 'Hospital Branch'
            if search and search not in name.lower() and search not in email.lower() and search not in hospital_name.lower():
                continue
            results.append({
                'id': admin.pk,
                'name': f"{name} ({hospital_name})",
                'email': email,
                'role': 'ADMIN',
                'hospital_id': getattr(admin, 'hospital_id', None),
                'hospital_name': hospital_name,
            })

        # Also include any Admins registered in User table
        user_admins = User.objects.filter(is_superuser=False).exclude(email__isnull=True).exclude(email__exact='')
        for u in user_admins:
            u_email = (u.email or '').strip()
            if not u_email:
                continue
            if not any(r['email'].lower() == u_email.lower() for r in results):
                u_name = f"{u.first_name} {u.last_name}".strip() or u.username
                if search and search not in u_name.lower() and search not in u_email.lower():
                    continue
                results.append({
                    'id': u.pk,
                    'name': f"{u_name} (Admin)",
                    'email': u_email,
                    'role': 'ADMIN',
                    'hospital_id': None,
                    'hospital_name': 'Admin Staff',
                })

    # 2. Hospital Admin: Can ONLY send messages to staff in their assigned hospital branch
    elif sender_role == 'ADMIN':
        admin = HospitalAdmin.objects.filter(email__iexact=current_email).first()
        if not admin or not admin.hospital:
            return Response([])
        hospital = admin.hospital

        # Doctors in this branch
        doctors = Doctor.objects.filter(hospitals=hospital).exclude(email__isnull=True).exclude(email__exact='')
        for doc in doctors:
            email = (doc.email or '').strip()
            if not email:
                continue
            name = get_role_name(doc) or getattr(doc, 'name', '') or email.split('@')[0]
            if search and search not in name.lower() and search not in email.lower():
                continue
            results.append({
                'id': doc.pk,
                'name': f"{name} (Doctor)",
                'email': email,
                'role': 'DOCTOR',
                'hospital_id': hospital.id,
                'hospital_name': hospital.Name,
            })

        # Nurses in this branch
        nurses = Nurse.objects.filter(hospital=hospital).exclude(email__isnull=True).exclude(email__exact='')
        for nurse in nurses:
            email = (nurse.email or '').strip()
            if not email:
                continue
            name = get_role_name(nurse) or getattr(nurse, 'name', '') or email.split('@')[0]
            if search and search not in name.lower() and search not in email.lower():
                continue
            results.append({
                'id': nurse.pk,
                'name': f"{name} (Nurse)",
                'email': email,
                'role': 'NURSES',
                'hospital_id': hospital.id,
                'hospital_name': hospital.Name,
            })

        # Receptionists in this branch
        receptionists = Receptionist.objects.filter(hospital=hospital).exclude(email__isnull=True).exclude(email__exact='')
        for rec in receptionists:
            email = (rec.email or '').strip()
            if not email:
                continue
            name = get_role_name(rec) or getattr(rec, 'name', '') or email.split('@')[0]
            if search and search not in name.lower() and search not in email.lower():
                continue
            results.append({
                'id': rec.pk,
                'name': f"{name} (Receptionist)",
                'email': email,
                'role': 'RECEPTIONISTS',
                'hospital_id': hospital.id,
                'hospital_name': hospital.Name,
            })

    # 3. All other roles (Doctors, Nurses, Receptionists, Patients): Cannot send messages
    else:
        return Response([])

    results.sort(key=lambda item: (item['name'].lower(), item['role']))
    return Response(results)


@api_view(['POST'])
def send_notification_message(request):
    ensure_notification_tables()
    sender_role = normalize_role(request.data.get('sender_role'))
    if not sender_role and (request.data.get('is_superuser') or 'super' in str(request.data.get('sender_email') or '').lower()):
        sender_role = 'SUPER_ADMIN'

    sender_email = str(request.data.get('sender_email') or '').strip().lower()
    if sender_role == 'SUPER_ADMIN' and not sender_email:
        superuser = User.objects.filter(is_superuser=True).first()
        sender_email = (superuser.email if superuser and superuser.email else 'superadmin@hospital.com').strip().lower()

    if not sender_email or not sender_role:
        identity, error = require_notification_identity(request)
        if identity:
            sender_email = sender_email or identity.get('email', '')
            sender_role = sender_role or identity.get('role', '')
        elif error:
            return error

    recipient_email = str(request.data.get('recipient_email') or '').strip().lower()
    recipient_role = normalize_role(request.data.get('recipient_role'))
    if sender_role == 'SUPER_ADMIN' and not recipient_role:
        recipient_role = 'ADMIN'

    title = str(request.data.get('title') or '').strip()
    message = str(request.data.get('message') or '').strip()

    if not all((sender_email, recipient_email, sender_role, recipient_role, title, message)):
        return Response({'detail': 'Sender, recipient, roles, title, and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Permission check: Only Super Admin and Hospital Admins can send messages
    if sender_role not in ('SUPER_ADMIN', 'ADMIN'):
        return Response({'detail': 'Only Super Admin and Hospital Admins are allowed to send messages.'}, status=status.HTTP_403_FORBIDDEN)

    sender_account = get_role_account(sender_role, sender_email)

    # 1. Super Admin: Can ONLY message Hospital Admins
    if sender_role == 'SUPER_ADMIN':
        if recipient_role != 'ADMIN':
            return Response({'detail': 'Super Admin can only send messages to Hospital Admins.'}, status=status.HTTP_403_FORBIDDEN)
        recipient_account = (
            HospitalAdmin.objects.filter(email__iexact=recipient_email).first()
            or HospitalAdmin.objects.filter(email__iexact=recipient_email.strip()).first()
            or User.objects.filter(email__iexact=recipient_email).first()
            or User.objects.filter(username__iexact=recipient_email).first()
        )

    # 2. Hospital Admin: Can ONLY message staff in their assigned hospital branch
    elif sender_role == 'ADMIN':
        admin = HospitalAdmin.objects.filter(email__iexact=sender_email).first()
        if not admin or not admin.hospital:
            if sender_account and getattr(sender_account, 'hospital', None):
                admin = sender_account
        if not admin or not admin.hospital:
            return Response({'detail': 'You do not have an assigned hospital branch to send messages.'}, status=status.HTTP_403_FORBIDDEN)

        hospital = admin.hospital
        if recipient_role not in ('DOCTOR', 'NURSES', 'RECEPTIONISTS'):
            return Response({'detail': 'Hospital Admins can only send messages to staff members (Doctors, Nurses, Receptionists) in their assigned branch.'}, status=status.HTTP_403_FORBIDDEN)

        if recipient_role == 'DOCTOR':
            recipient_account = Doctor.objects.filter(email__iexact=recipient_email).first()
        elif recipient_role == 'NURSES':
            recipient_account = Nurse.objects.filter(email__iexact=recipient_email).first()
        elif recipient_role == 'RECEPTIONISTS':
            recipient_account = Receptionist.objects.filter(email__iexact=recipient_email).first()
        else:
            recipient_account = None

        if not recipient_account:
            return Response({'detail': f'Recipient staff member was not found in your assigned hospital branch ({hospital.Name}).'}, status=status.HTTP_403_FORBIDDEN)
    else:
        recipient_account = None

    sender_name = get_role_name(sender_account) or ('Super Administrator' if sender_role == 'SUPER_ADMIN' else 'Hospital Admin')
    recipient_name = get_role_name(recipient_account) or (getattr(recipient_account, 'name', '') if recipient_account else '')
    if not recipient_name:
        recipient_name = recipient_email.split('@')[0].capitalize()

    is_important = str(request.data.get('is_important', 'false')).lower() in {'1', 'true', 'yes', 'on'}

    shared_fields = {
        'recipient_email': recipient_email.strip(),
        'recipient_name': recipient_name,
        'recipient_role': recipient_role,
        'sender_email': sender_email.strip(),
        'sender_name': sender_name,
        'sender_role': sender_role,
        'title': title,
        'message': message,
        'is_important': is_important,
        'is_read': False,
        'read_at': None,
    }

    sender_app, sender_model_name = ROLE_NOTIFICATION_MODELS[sender_role]
    recipient_app, recipient_model_name = ROLE_NOTIFICATION_MODELS[recipient_role]

    sender_notification_model = apps.get_model(sender_app, sender_model_name)
    recipient_notification_model = apps.get_model(recipient_app, recipient_model_name)

    with transaction.atomic():
        recipient_message = recipient_notification_model.objects.create(**shared_fields)
        if sender_notification_model is recipient_notification_model:
            sender_message = recipient_message
        else:
            sender_message = sender_notification_model.objects.create(**shared_fields)

    created_at_val = getattr(sender_message, 'created_at', None)
    return Response({
        'message': 'Notification message sent.',
        'data': {
            'id': sender_message.pk,
            **shared_fields,
            'created_at': created_at_val.isoformat() if created_at_val else timezone.now().isoformat(),
        },
    }, status=status.HTTP_201_CREATED)



class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        try:
            Patient.objects.filter(Q(patient_id='PAT-0002') | Q(email__iexact='p2@gmail.com'), name__iexact='Raj').update(name='Patient 2')
        except Exception:
            pass
        return Patient.objects.all()


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_val = self.kwargs.get(lookup_url_kwarg)

        # 1. Primary lookup by numeric database PK (id)
        if str(lookup_val).isdigit():
            obj = queryset.filter(pk=int(lookup_val)).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        # 2. Lookup by Appoment_id string
        obj = queryset.filter(Appoment_id=str(lookup_val)).first()
        if obj:
            self.check_object_permissions(self.request, obj)
            return obj

        # 3. Lookup by APT- prefix stripped
        clean_val = str(lookup_val).replace('APT-', '').strip()
        if clean_val:
            if clean_val.isdigit():
                obj = queryset.filter(Q(pk=int(clean_val)) | Q(Appoment_id=clean_val)).first()
            else:
                obj = queryset.filter(Appoment_id=clean_val).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj

        return super().get_object()

    def create(self, request, *args, **kwargs):
        # Prevent creating duplicate appointments when assigning doctor or updating an existing appointment
        appt_id = request.data.get('id') or request.data.get('appointment_id') or request.data.get('appointment_pk')
        appoment_id = request.data.get('Appoment_id') or request.data.get('appoment_id')
        existing = None
        if appt_id and str(appt_id).isdigit():
            existing = Appointment.objects.filter(pk=int(appt_id)).first()
        if not existing and appoment_id:
            existing = Appointment.objects.filter(Appoment_id=str(appoment_id)).first()

        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Strictly enforce that new appointment submissions are locked to today's date
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        now_dt = timezone.now()
        data['Applied_at'] = now_dt
        data['applied_at'] = now_dt
        data['visit_date_time'] = now_dt

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        instance = serializer.instance
        raw_health_care = self.request.data.get('Health_Care') or self.request.data.get('health_care')
        if raw_health_care:
            instance.Health_Care = raw_health_care

        new_status = serializer.validated_data.get('status', instance.status)
        health_care = raw_health_care or serializer.validated_data.get('Health_Care', instance.Health_Care)
        if instance.status != 'Discharged' and new_status == 'Discharged' and str(health_care or '').strip().lower() != 'fully recovered':
            raise ValidationError({
                'detail': "Patient cannot be discharged until Nurse marks Health Care status as 'Fully Recovered'."
            })
        try:
            super().perform_update(serializer)
        except Exception as e:
            if hasattr(e, 'message_dict'):
                raise ValidationError(e.message_dict)
            elif hasattr(e, 'messages'):
                raise ValidationError({'detail': ' '.join(e.messages)})
            raise

    def get_queryset(self):
        queryset = Appointment.objects.select_related('hospital', 'doctor', 'nurse').all()

        # Filter by Nurse
        nurse_param = self.request.query_params.get('nurse') or self.request.query_params.get('nurse_id')
        nurse_email = self.request.query_params.get('nurse_email')
        nurse_name = self.request.query_params.get('nurse_name')

        if nurse_param:
            if str(nurse_param).isdigit():
                queryset = queryset.filter(nurse_id=int(nurse_param))
            else:
                queryset = queryset.filter(Q(nurse__name__icontains=nurse_param) | Q(nurse__email__iexact=nurse_param))
        elif nurse_email:
            queryset = queryset.filter(nurse__email__iexact=nurse_email)
        elif nurse_name:
            queryset = queryset.filter(nurse__name__icontains=nurse_name)

        # Filter by Patient
        patient_param = self.request.query_params.get('patient') or self.request.query_params.get('patient_id')
        patient_email = self.request.query_params.get('patient_email') or self.request.query_params.get('email')
        patient_contact = self.request.query_params.get('contact') or self.request.query_params.get('phone')

        if patient_param:
            if str(patient_param).isdigit():
                patient = Patient.objects.filter(pk=patient_param).first()
                if patient:
                    queryset = queryset.filter(
                        Q(email__iexact=patient.email) |
                        Q(contact=patient.contact) |
                        Q(patient_Name__iexact=patient.name)
                    )
                else:
                    queryset = queryset.filter(pk=patient_param)
            else:
                queryset = queryset.filter(
                    Q(email__iexact=patient_param) |
                    Q(patient_Name__icontains=patient_param)
                )
        elif patient_email:
            queryset = queryset.filter(email__iexact=patient_email)
        elif patient_contact:
            queryset = queryset.filter(contact__icontains=patient_contact)

        # Filter by Hospital
        hospital_id = self.request.query_params.get('hospital') or self.request.query_params.get('hospital_id')
        if hospital_id and str(hospital_id).isdigit():
            queryset = queryset.filter(hospital_id=int(hospital_id))

        return queryset


class PatientNotificationViewSet(NotificationViewSetBase):
    notification_role = "PATIENTS"
    serializer_class = PatientNotificationSerializer
    queryset = PatientNotification.objects.all()
    receipt_model = PatientNotificationReceipt


NotificationViewSet = PatientNotificationViewSet



@api_view(['POST'])
def create_appointment(request):
    appt_id = request.data.get('id') or request.data.get('appointment_id') or request.data.get('appointment_pk')
    appoment_id = request.data.get('Appoment_id') or request.data.get('appoment_id')
    existing = None
    if appt_id and str(appt_id).isdigit():
        existing = Appointment.objects.filter(pk=int(appt_id)).first()
    if not existing and appoment_id:
        existing = Appointment.objects.filter(Appoment_id=str(appoment_id)).first()

    if existing:
        serializer = AppointmentSerializer(existing, data=request.data, partial=True)
        if serializer.is_valid():
            appointment = serializer.save()
            return Response({
                'message': 'Appointment updated successfully!',
                'appointment_id': appointment.id,
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Strictly enforce that new appointment submissions are locked to today's date
    data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
    now_dt = timezone.now()
    data['Applied_at'] = now_dt
    data['applied_at'] = now_dt
    data['visit_date_time'] = now_dt

    serializer = AppointmentSerializer(data=data)
    if serializer.is_valid():
        appointment = serializer.save()
        return Response({
            'message': 'Appointment booked successfully!',
            'appointment_id': appointment.id,
            'data': serializer.data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_appointments(request):
    appointments = Appointment.objects.all()
    patient_id = request.query_params.get('patient')
    if patient_id:
        if patient_id.isdigit():
            patient = Patient.objects.filter(pk=patient_id).first()
            appointments = appointments.filter(email__iexact=patient.email) if patient and patient.email else appointments.none()
        else:
            appointments = appointments.filter(email__iexact=patient_id)
    return Response(AppointmentSerializer(appointments, many=True).data)


@api_view(["POST"])
def user_login(request):
    raw_identifier = (
        request.data.get("email")
        or request.data.get("username")
        or ""
    ).strip()
    password = request.data.get("password", "")
    if not raw_identifier or not password:
        return Response({"message": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    account = User.objects.filter(Q(email__iexact=raw_identifier) | Q(username__iexact=raw_identifier)).first()
    if account and (account.password == password or account.check_password(password)):
        role = "SUPER ADMIN" if account.is_superuser else "ADMIN"
        name = f"{account.first_name} {account.last_name}".strip() or account.username
        return Response({"message": "Login successful", "role": role,
                         "user": {"id": account.pk, "name": name, "email": account.email, "role": role,
                                  "notification_token": _notification_identity(account.email, role)}})

    role_models = (
        (HospitalAdmin, "ADMIN", "employee_id"),
        (Doctor, "DOCTOR", "doctor_id"),
        (Nurse, "NURSES", "nurse_id"),
        (Receptionist, "RECEPTIONISTS", "receptionist_id"),
        (Patient, "PATIENTS", "patient_id"),
    )
    for model, role, id_attr in role_models:
        query = Q(email__iexact=raw_identifier)
        if id_attr:
            query |= Q(**{f"{id_attr}__iexact": raw_identifier})
        user = model.objects.filter(query).first()
        if user and (user.password == password or user.check_password(password)):
            return Response({"message": "Login successful", "role": role,
                             "user": {"id": user.pk, "name": user.name, "email": user.email, "role": role,
                                      "notification_token": _notification_identity(user.email, role)}})
    return Response({"message": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def user_reset_password(request):
    raw_identifier = (
        request.data.get("email")
        or request.data.get("username")
        or request.data.get("user")
        or ""
    ).strip()
    password = (
        request.data.get("new_password")
        or request.data.get("password")
        or request.data.get("newPassword")
        or ""
    ).strip()
    if not raw_identifier or not password:
        return Response({"message": "Email/Username and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({"message": "Password must be at least 6 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    updated = False

    # 1. Super Admin / Django auth User
    super_user = User.objects.filter(Q(email__iexact=raw_identifier) | Q(username__iexact=raw_identifier)).first()
    if super_user:
        super_user.password = password
        super_user.save(update_fields=["password"])
        updated = True

    # 2. Check Role Models (HospitalAdmin, Doctor, Nurse, Receptionist, Patient)
    role_models = (
        (HospitalAdmin, "employee_id"),
        (Doctor, "doctor_id"),
        (Nurse, "nurse_id"),
        (Receptionist, "receptionist_id"),
        (Patient, "patient_id"),
    )
    for model, id_attr in role_models:
        query = Q(email__iexact=raw_identifier)
        if id_attr:
            query |= Q(**{f"{id_attr}__iexact": raw_identifier})
        user = model.objects.filter(query).first()
        if user:
            user.password = password
            user.save(update_fields=["password"])
            updated = True
            break

    if updated:
        return Response({"message": "Password updated successfully."})
    return Response({"message": f"Account with '{raw_identifier}' not found in records."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def user_signup(request):
    """Create patient accounts through the public signup form."""
    import re
    data = request.data
    role = str(data.get("role") or data.get("Select_User") or "PATIENTS").upper()
    if role not in {"PATIENT", "PATIENTS"}:
        return Response({"message": "Only patient registration is available through public signup."}, status=status.HTTP_400_BAD_REQUEST)

    email = str(data.get("email") or "").strip()
    password = str(data.get("password") or "")
    name = str(data.get("name") or f"{data.get('first_name', '')} {data.get('last_name', '')}").strip()
    contact = str(data.get("contact") or data.get("phone") or "").strip()
    if not email or not password or not name:
        return Response({"message": "Name, email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    if not email.lower().endswith("@gmail.com"):
        return Response({"email": ["Email must end with @gmail.com."]}, status=status.HTTP_400_BAD_REQUEST)
    clean_contact = re.sub(r'\D', '', contact)
    if contact and len(clean_contact) != 10:
        return Response({"contact": ["Phone number must be exactly 10 digits."]}, status=status.HTTP_400_BAD_REQUEST)
    if Patient.objects.filter(email__iexact=email).exists():
        return Response({"email": ["An account with this email already exists."]}, status=status.HTTP_400_BAD_REQUEST)
    try:
        with transaction.atomic():
            patient = Patient.objects.create(name=name, email=email, password=password, contact=clean_contact if contact else contact)
    except IntegrityError:
        return Response({"email": ["An account with this email already exists."]}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Patient account created successfully.", "user": {
        "id": patient.pk, "name": patient.name, "email": patient.email, "role": "PATIENTS"
    }, "data": PatientSerializer(patient).data}, status=status.HTTP_201_CREATED)
