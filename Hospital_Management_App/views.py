import uuid

from django.apps import apps
from django.contrib.auth.models import User
from django.core import signing
from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Appointment, Notification, NotificationReceipt, Patient
from .serializers import AppointmentSerializer, NotificationSerializer, PatientSerializer
from Admin.models import HospitalAdmin
from Doctor.models import Doctor
from Nurse.models import Nurse
from Receptionist.models import Receptionist


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


def get_role_account(role, email):
    app_label, model_name = ROLE_ACCOUNTS[role]
    model = apps.get_model(app_label, model_name)
    accounts = model.objects.filter(email__iexact=email)
    if role == 'SUPER_ADMIN':
        accounts = accounts.filter(is_superuser=True, is_active=True)
    elif hasattr(model, 'is_active'):
        accounts = accounts.filter(is_active=True)
    return accounts.first()


def get_role_name(account):
    if hasattr(account, 'name'):
        return account.name
    return f'{account.first_name} {account.last_name}'.strip() or account.username


def notification_identity(request):
    authorization = request.META.get('HTTP_AUTHORIZATION', '')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None
    try:
        identity = signing.loads(token, salt='hospital-notification-identity', max_age=60 * 60 * 24 * 30)
    except signing.BadSignature:
        return None
    role = normalize_role(identity.get('role'))
    email = str(identity.get('email') or '').strip()
    if not role or not email or not get_role_account(role, email):
        return None
    return {'role': role, 'email': email}


def require_notification_identity(request):
    identity = notification_identity(request)
    if not identity:
        return None, Response({'detail': 'Sign in again to use notifications.'}, status=status.HTTP_401_UNAUTHORIZED)
    return identity, None


class NotificationViewSetBase(viewsets.ModelViewSet):
    notification_role = None
    receipt_model = None

    def _require_recipient(self):
        identity, error = require_notification_identity(self.request)
        if error:
            return None, error
        if self.notification_role and identity['role'] != self.notification_role:
            return None, Response({'detail': 'This notification inbox belongs to another user role.'}, status=status.HTTP_403_FORBIDDEN)
        return identity['email'], None

    def list(self, request, *args, **kwargs):
        _, error = self._require_recipient()
        return error or super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        email, error = self._require_recipient()
        if error:
            return error
        notification = self.get_object()
        self.receipt_model.objects.get_or_create(notification=notification, recipient_email=email)
        return Response(self.get_serializer(notification).data)

    def perform_create(self, serializer):
        raise PermissionDenied('Use the notification message endpoint to send messages.')

    def perform_update(self, serializer):
        raise PermissionDenied('Notifications cannot be edited.')

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Notifications cannot be deleted.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        queryset = super().get_queryset()
        identity, _ = require_notification_identity(self.request)
        if not identity or (self.notification_role and identity['role'] != self.notification_role):
            return queryset.none()
        email, role = identity['email'], identity['role']
        participant_filter = Q(recipient_email__iexact=email) | Q(sender_email__iexact=email)
        participant_filter |= Q(recipient_email__isnull=True, recipient_role__iexact=role)
        queryset = queryset.filter(participant_filter)
        thread_id = self.request.query_params.get('thread_id')
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        direction = self.request.query_params.get('direction', '').lower()
        if direction == 'inbox':
            queryset = queryset.filter(Q(recipient_email__iexact=email) | Q(recipient_email__isnull=True, recipient_role__iexact=role))
        elif direction == 'sent':
            queryset = queryset.filter(sender_email__iexact=email)
        if self.request.query_params.get('important', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(is_important=True)
        if self.request.query_params.get('unread_only', '').lower() in {'1', 'true', 'yes'}:
            queryset = queryset.filter(Q(recipient_email__iexact=email) | Q(recipient_email__isnull=True, recipient_role__iexact=role))
            queryset = queryset.exclude(receipts__recipient_email__iexact=email)
        return queryset

    def _inbox_queryset(self, email):
        role = self.request.query_params.get('recipient_role', '').strip()
        incoming = Q(recipient_email__iexact=email)
        if role:
            incoming |= Q(recipient_email__isnull=True, recipient_role__iexact=role)
        return self.get_queryset().filter(incoming)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        email, error = self._require_recipient()
        if error:
            return error
        notification = self.get_object()
        if (notification.recipient_email or '').lower() != email.lower() and not (
            notification.recipient_email is None and notification.recipient_role == self.notification_role
        ):
            return Response({'detail': 'Only the recipient can mark this notification read.'}, status=status.HTTP_403_FORBIDDEN)
        self.receipt_model.objects.get_or_create(notification=notification, recipient_email=email)
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        email, error = self._require_recipient()
        if error:
            return error
        notification_ids = list(self._inbox_queryset(email).exclude(receipts__recipient_email__iexact=email).values_list('pk', flat=True).distinct())
        self.receipt_model.objects.bulk_create(
            [self.receipt_model(notification_id=notification_id, recipient_email=email) for notification_id in notification_ids],
            ignore_conflicts=True,
        )
        return Response({'updated': len(notification_ids)})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        email, error = self._require_recipient()
        if error:
            return error
        unread_count = self._inbox_queryset(email).exclude(receipts__recipient_email__iexact=email).distinct().count()
        return Response({'unread_count': unread_count})


@api_view(['GET'])
def notification_recipients(request):
    identity, error = require_notification_identity(request)
    if error:
        return error
    current_email = identity['email']
    search = request.query_params.get('search', '').strip().lower()
    results = []
    for role, (app_label, model_name) in ROLE_ACCOUNTS.items():
        model = apps.get_model(app_label, model_name)
        accounts = model.objects.exclude(email__isnull=True).exclude(email__exact='')
        if role == 'SUPER_ADMIN':
            accounts = accounts.filter(is_superuser=True, is_active=True)
        elif hasattr(model, 'is_active'):
            accounts = accounts.filter(is_active=True)
        for account in accounts.only('id', 'email'):
            email = account.email.strip()
            if email.lower() == current_email.lower():
                continue
            name = get_role_name(account)
            if search and search not in name.lower() and search not in email.lower():
                continue
            results.append({'id': account.pk, 'name': name, 'email': email, 'role': role})
    results.sort(key=lambda item: (item['name'].lower(), item['role']))
    return Response(results)


@api_view(['POST'])
def send_notification_message(request):
    identity, error = require_notification_identity(request)
    if error:
        return error
    sender_email = identity['email']
    recipient_email = str(request.data.get('recipient_email') or '').strip()
    sender_role = identity['role']
    recipient_role = normalize_role(request.data.get('recipient_role'))
    title = str(request.data.get('title') or '').strip()
    message = str(request.data.get('message') or '').strip()
    if not all((sender_email, recipient_email, sender_role, recipient_role, title, message)):
        return Response({'detail': 'Sender, recipient, roles, title, and message are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if sender_email.lower() == recipient_email.lower():
        return Response({'detail': 'You cannot send a message to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    sender_account = get_role_account(sender_role, sender_email)
    recipient_account = get_role_account(recipient_role, recipient_email)
    if not sender_account:
        return Response({'detail': 'Sender account was not found or is inactive.'}, status=status.HTTP_404_NOT_FOUND)
    if not recipient_account:
        return Response({'detail': 'Recipient account was not found or is inactive.'}, status=status.HTTP_404_NOT_FOUND)

    thread_id = request.data.get('thread_id')
    reply_to = request.data.get('reply_to')
    if reply_to:
        try:
            reply_to = uuid.UUID(str(reply_to))
            thread_id = uuid.UUID(str(thread_id))
        except (TypeError, ValueError, AttributeError):
            return Response({'detail': 'Invalid reply thread reference.'}, status=status.HTTP_400_BAD_REQUEST)
        sender_model = apps.get_model(ROLE_NOTIFICATION_APPS[sender_role], 'Notification')
        sender_message = sender_model.objects.filter(thread_id=thread_id, message_id=reply_to).filter(
            Q(sender_email__iexact=sender_email) | Q(recipient_email__iexact=sender_email)
        ).first()
        if not sender_message:
            return Response({'detail': 'The message being replied to was not found in your conversation.'}, status=status.HTTP_404_NOT_FOUND)
        if (sender_message.sender_email or '').lower() == sender_email.lower():
            expected_email, expected_role = sender_message.recipient_email, sender_message.recipient_role
        else:
            expected_email, expected_role = sender_message.sender_email, sender_message.sender_role
        if expected_email and expected_email.lower() != recipient_email.lower():
            return Response({'detail': 'Replies must be sent to the other participant in the conversation.'}, status=status.HTTP_400_BAD_REQUEST)
        if expected_role and normalize_role(expected_role) != recipient_role:
            return Response({'detail': 'Recipient role does not match the conversation.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        thread_id, reply_to = uuid.uuid4(), None

    shared_fields = {
        'recipient_email': recipient_email, 'recipient_role': recipient_role,
        'sender_email': sender_email, 'sender_name': get_role_name(sender_account),
        'sender_role': sender_role, 'category': 'GENERAL', 'title': title,
        'message': message, 'thread_id': thread_id, 'reply_to': reply_to,
        'is_important': str(request.data.get('is_important', 'false')).lower() in {'1', 'true', 'yes', 'on'},
    }
    message_id = uuid.uuid4()
    sender_notification_model = apps.get_model(ROLE_NOTIFICATION_APPS[sender_role], 'Notification')
    recipient_notification_model = apps.get_model(ROLE_NOTIFICATION_APPS[recipient_role], 'Notification')
    with transaction.atomic():
        recipient_message = recipient_notification_model.objects.create(message_id=message_id, **shared_fields)
        sender_message = recipient_message if sender_notification_model is recipient_notification_model else sender_notification_model.objects.create(message_id=message_id, **shared_fields)
    return Response({
        'message': 'Notification message sent.', 'message_id': str(message_id), 'thread_id': str(thread_id),
        'data': {
            'id': sender_message.pk, 'message_id': str(message_id), 'thread_id': str(thread_id),
            **shared_fields,
        },
    }, status=status.HTTP_201_CREATED)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('hospital', 'doctor', 'nurse').all()
    serializer_class = AppointmentSerializer


class NotificationViewSet(NotificationViewSetBase):
    notification_role = "PATIENTS"
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    receipt_model = NotificationReceipt


@api_view(['POST'])
def create_appointment(request):
    serializer = AppointmentSerializer(data=request.data)
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
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")
    if not email or not password:
        return Response({"message": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    account = User.objects.filter(email__iexact=email).first()
    if account is None:
        account = User.objects.filter(username__iexact=email).first()
    if account and account.check_password(password):
        role = "SUPER ADMIN" if account.is_superuser else "ADMIN"
        name = f"{account.first_name} {account.last_name}".strip() or account.username
        return Response({"message": "Login successful", "role": role,
                         "user": {"id": account.pk, "name": name, "email": account.email, "role": role,
                                  "notification_token": _notification_identity(account.email, role)}})

    role_models = (
        (HospitalAdmin, "ADMIN"), (Doctor, "DOCTOR"), (Nurse, "NURSES"),
        (Receptionist, "RECEPTIONISTS"), (Patient, "PATIENTS"),
    )
    for model, role in role_models:
        user = model.objects.filter(email__iexact=email, password=password).first()
        if user:
            return Response({"message": "Login successful", "role": role,
                             "user": {"id": user.pk, "name": user.name, "email": user.email, "role": role,
                                      "notification_token": _notification_identity(user.email, role)}})
    return Response({"message": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def user_reset_password(request):
    email = request.data.get("email", "").strip()
    password = request.data.get("new_password", "")
    if not email or not password:
        return Response({"message": "Email and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
    account = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
    if account:
        account.set_password(password)
        account.save(update_fields=["password"])
        return Response({"message": "Password updated successfully."})
    for model in (HospitalAdmin, Doctor, Nurse, Receptionist, Patient):
        user = model.objects.filter(email__iexact=email).first()
        if user:
            user.password = password
            user.save(update_fields=["password"])
            return Response({"message": "Password updated successfully."})
    return Response({"message": "Email not found in records."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def user_signup(request):
    """Create patient accounts through the public signup form."""
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
    if Patient.objects.filter(email__iexact=email).exists():
        return Response({"email": ["An account with this email already exists."]}, status=status.HTTP_400_BAD_REQUEST)
    try:
        with transaction.atomic():
            patient = Patient.objects.create(name=name, email=email, password=password, contact=contact)
    except IntegrityError:
        return Response({"email": ["An account with this email already exists."]}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Patient account created successfully.", "user": {
        "id": patient.pk, "name": patient.name, "email": patient.email, "role": "PATIENTS"
    }, "data": PatientSerializer(patient).data}, status=status.HTTP_201_CREATED)
