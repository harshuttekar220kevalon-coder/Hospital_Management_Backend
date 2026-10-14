from rest_framework.routers import DefaultRouter
from .views import HospitalAdminViewSet, NotificationViewSet

router = DefaultRouter()
router.register("hospital-admins", HospitalAdminViewSet, basename="hospital-admin")
router.register("notifications", NotificationViewSet, basename="admin-notification")
urlpatterns = router.urls
