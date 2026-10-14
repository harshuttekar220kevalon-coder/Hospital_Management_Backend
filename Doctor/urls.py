from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="doctor-notification")
router.register("", DoctorViewSet, basename="doctor")
urlpatterns = router.urls
