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
            # Disabled auto notifications
            return

        def notify_new_staff(sender, instance, created, **kwargs):
            # Disabled auto message for staff account creation
            return

        # Clean up legacy auto-notifications and test messages across all models
        try:
            from django.db.models import Q
            for app_name in ('Admin', 'Super_Admin', 'Doctor', 'Nurse', 'Receptionist', 'Hospital_Management_App'):
                try:
                    n_model = apps.get_model(app_name, 'Notification')
                    n_model.objects.filter(
                        Q(title__icontains='Staff account created') |
                        Q(title__icontains='Patient registered') |
                        Q(title__icontains='appointment') |
                        Q(title__icontains='Welcome to the hospital') |
                        Q(title__icontains='loda') |
                        Q(sender_email__isnull=True) |
                        Q(sender_email='')
                    ).delete()
                except Exception:
                    pass
        except Exception:
            pass

        # Auto-ensure Health_Care column exists in Super_Admin_appointment
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(Super_Admin_appointment)")
                columns = [row[1] for row in cursor.fetchall()]
                if columns and 'Health_Care' not in columns:
                    cursor.execute("ALTER TABLE Super_Admin_appointment ADD COLUMN Health_Care varchar(50) DEFAULT 'Not Done'")
        except Exception:
            pass

        # Restore patient account data if inadvertently changed by appointment edits
        try:
            from django.db.models import Q
            p2 = Patient.objects.filter(Q(patient_id='PAT-0002') | Q(email__iexact='p2@gmail.com')).first()
            if p2 and p2.name != 'Patient 2':
                p2.name = 'Patient 2'
                p2.save()
        except Exception:
            pass

        def remember_appointment_status(sender, instance, **kwargs):
            return

        def notify_appointment_changes(sender, instance, created, **kwargs):
            # Disabled auto notifications
            return

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
