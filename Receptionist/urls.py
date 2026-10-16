from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, ReceptionistViewSet, ReceptionistChatViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="receptionist-notification")
router.register("chats", ReceptionistChatViewSet, basename="receptionist-chat")
router.register("", ReceptionistViewSet, basename="receptionist")
urlpatterns = router.urls
