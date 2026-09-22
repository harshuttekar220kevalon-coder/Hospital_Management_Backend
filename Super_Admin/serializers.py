from rest_framework import serializers

from Super_Admin.models import Doctor, HospitalAdmin, Hospitals, Nurse, Patient, Receptionist






class Hospitalsserializer(serializers.ModelSerializer):
    class Meta:
        model = Hospitals
        fields = '__all__'
        read_only_fields = ['Branch_Code', 'created_at']

class HospitalAdminserializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAdmin
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    hospitals = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Hospitals.objects.all(), required=False)
    hospital_names = serializers.SerializerMethodField()
    class Meta:
        model = Doctor
        fields = '__all__'
    def get_hospital_names(self, obj):
        return [{"id": h.id, "name": h.Name, "branch_code": h.Branch_Code} for h in obj.hospitals.all()]


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