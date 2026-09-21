from rest_framework import serializers

from Super_Admin.models import Department, Doctor, HospitalAdmin, Hospitals, Nurse, Patient, Receptionist






class Hospitalsserializer(serializers.ModelSerializer):
    class Meta:
        model = Hospitals
        fields = '__all__'
        read_only_fields = ['Branch_Code', 'created_at']




class Departmentserializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'



class HospitalAdminserializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAdmin
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = '__all__'

class ReceptionistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptionist
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'