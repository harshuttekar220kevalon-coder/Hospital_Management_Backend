from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, NotificationViewSet, DoctorChatViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="doctor-notification")
router.register("chats", DoctorChatViewSet, basename="doctor-chat")
router.register("", DoctorViewSet, basename="doctor")
urlpatterns = router.urls
