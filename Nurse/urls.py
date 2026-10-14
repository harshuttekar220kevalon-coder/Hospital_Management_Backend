from rest_framework.routers import DefaultRouter
from .views import NurseViewSet, NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="nurse-notification")
router.register("", NurseViewSet, basename="nurse")
urlpatterns = router.urls
