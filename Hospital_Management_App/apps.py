from django.apps import AppConfig


class HospitalManagementAppConfig(AppConfig):
    name = 'Hospital_Management_App'

    def ready(self):
        from django.apps import apps
        from django.db.models.signals import post_save, pre_save

        Patient = apps.get_model('Hospital_Management_App', 'Patient')
        Appointment = apps.get_model('Hospital_Management_App', 'Appointment')
        staff_roles = {
            'Doctor.Doctor': 'DOCTOR',
            'Nurse.Nurse': 'NURSES',
            'Receptionist.Receptionist': 'RECEPTIONISTS',
            'Admin.HospitalAdmin': 'ADMIN',
        }

        def create_role_notification(role, *, title, message, category, recipient_email=None, data=None):
            notification_apps = {
                'PATIENTS': 'Hospital_Management_App',
                'DOCTOR': 'Doctor',
                'NURSES': 'Nurse',
                'RECEPTIONISTS': 'Receptionist',
                'ADMIN': 'Admin',
                'SUPER_ADMIN': 'Super_Admin',
            }
            notification_model = apps.get_model(notification_apps[role], 'Notification')
            return notification_model.objects.create(
                recipient_email=recipient_email,
                recipient_role=None if recipient_email else role,
                category=category,
                title=title,
                message=message,
                data=data or {},
            )

        def notify_new_patient(sender, instance, created, **kwargs):
            if not created:
                return
            details = {'patient_id': instance.pk, 'patient_code': instance.patient_id}
            if instance.email:
                create_role_notification(
                    'PATIENTS', recipient_email=instance.email, category='ACCOUNT',
                    title='Welcome to the hospital portal',
                    message='Your patient account has been created successfully.', data=details,
                )
            for role in ('ADMIN', 'SUPER_ADMIN'):
                create_role_notification(
                    role, category='ACCOUNT', title='Patient registered',
                    message=f'{instance.name} has registered as a patient.', data=details,
                )

        def notify_new_staff(sender, instance, created, **kwargs):
            if not created or not instance.email:
                return
            role = staff_roles[f'{sender._meta.app_label}.{sender.__name__}']
            details = {'account_id': instance.pk, 'role': role}
            create_role_notification(
                role, recipient_email=instance.email, category='ACCOUNT',
                title='Welcome to the hospital team',
                message='Your staff account has been created successfully.', data=details,
            )
            if role != 'ADMIN':
                create_role_notification(
                    'ADMIN', category='ACCOUNT', title='Staff account created',
                    message=f'A new {role.lower()} staff account was created.', data=details,
                )
            create_role_notification(
                'SUPER_ADMIN', category='ACCOUNT', title='Staff account created',
                message=f'A new {role.lower()} staff account was created.', data=details,
            )

        def remember_appointment_status(sender, instance, **kwargs):
            if instance.pk:
                previous = sender.objects.filter(pk=instance.pk).values(
                    'status', 'doctor_id', 'nurse_id', 'payment_status'
                ).first()
                instance._previous_notification_state = previous or {}
            else:
                instance._previous_notification_state = {}

        def notify_appointment_changes(sender, instance, created, **kwargs):
            appointment_code = instance.Appoment_id or str(instance.pk)
            details = {
                'appointment_id': instance.pk,
                'appointment_code': appointment_code,
                'status': instance.status,
            }
            if created:
                if instance.email:
                    create_role_notification(
                        'PATIENTS', recipient_email=instance.email, category='APPOINTMENT',
                        title='Appointment booked',
                        message=f'Appointment {appointment_code} has been booked successfully.', data=details,
                    )
                for role in ('RECEPTIONISTS', 'ADMIN', 'SUPER_ADMIN'):
                    create_role_notification(
                        role, category='APPOINTMENT', title='New appointment booked',
                        message=f'A new appointment ({appointment_code}) is waiting for review.', data=details,
                    )
                if instance.doctor_id and instance.doctor and instance.doctor.email:
                    create_role_notification(
                        'DOCTOR', recipient_email=instance.doctor.email, category='APPOINTMENT',
                        title='Appointment assigned',
                        message=f'Appointment {appointment_code} has been assigned to you.', data=details,
                    )
                if instance.nurse_id and instance.nurse and instance.nurse.email:
                    create_role_notification(
                        'NURSES', recipient_email=instance.nurse.email, category='APPOINTMENT',
                        title='Patient assigned',
                        message=f'Appointment {appointment_code} has been assigned to you.', data=details,
                    )
                return

            previous = getattr(instance, '_previous_notification_state', {})
            if previous.get('status') != instance.status:
                if instance.email:
                    create_role_notification(
                        'PATIENTS', recipient_email=instance.email, category='APPOINTMENT',
                        title='Appointment status updated',
                        message=f'Appointment {appointment_code} status is now {instance.status or "updated"}.',
                        data=details,
                    )
                for role in ('ADMIN', 'SUPER_ADMIN'):
                    create_role_notification(
                        role, category='APPOINTMENT', title='Appointment status updated',
                        message=f'Appointment {appointment_code} status changed to {instance.status or "updated"}.',
                        data=details,
                    )
            if previous.get('doctor_id') != instance.doctor_id and instance.doctor_id and instance.doctor and instance.doctor.email:
                create_role_notification(
                    'DOCTOR', recipient_email=instance.doctor.email, category='APPOINTMENT',
                    title='Appointment assigned',
                    message=f'Appointment {appointment_code} has been assigned to you.', data=details,
                )
            if previous.get('nurse_id') != instance.nurse_id and instance.nurse_id and instance.nurse and instance.nurse.email:
                create_role_notification(
                    'NURSES', recipient_email=instance.nurse.email, category='APPOINTMENT',
                    title='Patient assigned',
                    message=f'Appointment {appointment_code} has been assigned to you.', data=details,
                )
            if previous.get('payment_status') != instance.payment_status and instance.payment_status and instance.email:
                create_role_notification(
                    'PATIENTS', recipient_email=instance.email, category='BILLING',
                    title='Payment status updated',
                    message=f'Appointment {appointment_code} payment status is {instance.payment_status}.',
                    data=details | {'payment_status': instance.payment_status},
                )

        post_save.connect(notify_new_patient, sender=Patient, dispatch_uid='notify_new_patient')
        for model_label in staff_roles:
            app_label, model_name = model_label.split('.')
            post_save.connect(
                notify_new_staff,
                sender=apps.get_model(app_label, model_name),
                dispatch_uid=f'notify_new_staff_{model_label}',
            )
        pre_save.connect(remember_appointment_status, sender=Appointment, dispatch_uid='remember_appointment_status')
        post_save.connect(notify_appointment_changes, sender=Appointment, dispatch_uid='notify_appointment_changes')
