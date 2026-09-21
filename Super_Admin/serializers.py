from rest_framework import serializers

from Super_Admin.models import Hospitals






class Hospitalsserializer(serializers.ModelSerializer):
    class Meta:
        model = Hospitals
        fields = '__all__'
        read_only_fields = ['Branch_Code', 'created_at']