from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, ReceptionistViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="receptionist-notification")
router.register("", ReceptionistViewSet, basename="receptionist")
urlpatterns = router.urls
