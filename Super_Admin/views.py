from django.shortcuts import render
from rest_framework import viewsets

from Super_Admin.models import Hospitals
from Super_Admin.serializers import Hospitalsserializer






class Hospitalsviewset(viewsets.ModelViewSet):
    queryset = Hospitals.objects.all()
    serializer_class = Hospitalsserializer