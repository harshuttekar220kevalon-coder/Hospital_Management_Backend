from rest_framework.routers import DefaultRouter
from .views import NurseViewSet, NotificationViewSet, NurseChatViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="nurse-notification")
router.register("chats", NurseChatViewSet, basename="nurse-chat")
router.register("", NurseViewSet, basename="nurse")
urlpatterns = router.urls
