from django.apps import apps
from rest_framework import serializers
from .models import Appointment, Patient, PatientNotification, Notification


class NotificationSerializerBase(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        email = attrs.get('recipient_email', getattr(self.instance, 'recipient_email', None))
        role = attrs.get('recipient_role', getattr(self.instance, 'recipient_role', None))
        if not email and not role:
            raise serializers.ValidationError('Provide recipient_email, recipient_role, or both.')
        return attrs


class PatientNotificationSerializer(NotificationSerializerBase):
    class Meta:
        model = PatientNotification
        fields = "__all__"


NotificationSerializer = PatientNotificationSerializer


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'phone' in data and ('contact' not in data or not data['contact']):
            data['contact'] = data['phone']
        return super().to_internal_value(data)

    def validate_contact(self, value):
        import re
        if not value:
            return value
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return clean

    def validate_email(self, value):
        if not value or not str(value).strip().lower().endswith('@gmail.com'):
            raise serializers.ValidationError("Email must end with @gmail.com.")
        return str(value).strip().lower()


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_Name', read_only=True)
    nurse_name = serializers.CharField(source='nurse.name', read_only=True, default='')
    nurse_email = serializers.CharField(source='nurse.email', read_only=True, default='')
    doctor_name = serializers.CharField(source='doctor.name', read_only=True, default='')
    doctor_id = serializers.CharField(source='doctor.doctor_id', read_only=True, default='')
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True, default='')
    hospital_name = serializers.CharField(source='hospital.Name', read_only=True, default='')
    health_care = serializers.CharField(source='Health_Care', required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        extra_kwargs = {'Appoment_id': {'read_only': True}}

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'patient_name' in data and 'patient_Name' not in data:
            data['patient_Name'] = data['patient_name']
        elif 'name' in data and 'patient_Name' not in data:
            data['patient_Name'] = data['name']
        if 'health_care' in data and 'Health_Care' not in data:
            data['Health_Care'] = data['health_care']
        elif 'Health_Care' in data and 'health_care' not in data:
            data['health_care'] = data['Health_Care']
        if 'gender' in data and 'Gender' not in data:
            data['Gender'] = data['gender']
        if 'phone' in data and ('contact' not in data or not data['contact']):
            data['contact'] = data['phone']
        if 'applied_at' in data and 'Applied_at' not in data:
            data['Applied_at'] = data['applied_at']
        if 'Payment_Status' in data and 'payment_status' not in data:
            data['payment_status'] = data['Payment_Status']
        if 'Payment_Method' in data and 'payment_method' not in data:
            data['payment_method'] = data['Payment_Method']
        if 'hospital_charges' in data and 'hospitals_charges' not in data:
            data['hospitals_charges'] = data['hospital_charges']
        elif 'Hospitals_Chargies' in data and 'hospitals_charges' not in data:
            data['hospitals_charges'] = data['Hospitals_Chargies']
        if 'Amount_Paid' in data and 'amount_paid' not in data:
            data['amount_paid'] = data['Amount_Paid']
        if 'discharge_datetime' in data and 'Discharge_DateTime' not in data:
            data['Discharge_DateTime'] = data['discharge_datetime']
        elif 'discharge_date' in data and 'Discharge_DateTime' not in data:
            data['Discharge_DateTime'] = data['discharge_date']
        elif 'Discharge_Date' in data and 'Discharge_DateTime' not in data:
            data['Discharge_DateTime'] = data['Discharge_Date']

        if isinstance(data.get('doctor'), dict):
            data['doctor'] = data['doctor'].get('id')
        if isinstance(data.get('nurse'), dict):
            data['nurse'] = data['nurse'].get('id')
        if isinstance(data.get('hospital'), dict):
            data['hospital'] = data['hospital'].get('id')

        # Safely convert empty string representations to None for nullable FKs and numbers
        for fk_key in ('doctor', 'nurse', 'hospital', 'bed_number'):
            if fk_key in data and data[fk_key] in ('', 'null', 'None', 0, '0', None):
                data[fk_key] = None

        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['name'] = instance.patient_Name
        ret['patient_name'] = instance.patient_Name
        ret['payment_status'] = instance.payment_status or 'Pending'
        ret['Payment_Status'] = instance.payment_status or 'Pending'
        ret['hospitals_charges'] = str(instance.hospitals_charges or 0)
        ret['hospital_charges'] = str(instance.hospitals_charges or 0)
        ret['amount_paid'] = str(instance.amount_paid or 0)
        if instance.doctor:
            ret['doctor_name'] = instance.doctor.name or ''
            ret['doctor_id'] = instance.doctor.doctor_id or (str(instance.doctor.id) if instance.doctor.id else '')
        else:
            ret['doctor_name'] = ''
            ret['doctor_id'] = ''
        vdt = instance.visit_date_time
        if vdt:
            ret['appointment_date'] = vdt.strftime('%Y-%m-%d')
            ret['visit_date'] = vdt.strftime('%Y-%m-%d')
            ret['appointment_time'] = vdt.strftime('%I:%M %p')
            ret['visit_time'] = vdt.strftime('%I:%M %p')
        else:
            ret['appointment_date'] = ''
            ret['visit_date'] = ''
            ret['appointment_time'] = ''
            ret['visit_time'] = ''
        return ret

    def validate_contact(self, value):
        import re
        if not value:
            return value
        clean = re.sub(r'\D', '', str(value or ''))
        if len(clean) >= 10:
            return clean[-10:]
        return clean

    def validate_email(self, value):
        if not value:
            return value
        if not str(value).strip().lower().endswith('@gmail.com'):
            raise serializers.ValidationError("Email must end with @gmail.com.")
        return str(value).strip().lower()
