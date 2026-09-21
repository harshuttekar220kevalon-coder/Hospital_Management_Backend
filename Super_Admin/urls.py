from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Super_Admin.views import Hospitalsviewset


router = DefaultRouter()
router.register(r'Hospital',Hospitalsviewset)

urlpatterns =[
    path('',include(router.urls)),
]