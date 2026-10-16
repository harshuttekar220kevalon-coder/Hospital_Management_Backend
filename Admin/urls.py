from rest_framework.routers import DefaultRouter
from .views import HospitalAdminViewSet, NotificationViewSet, AdminChatViewSet

router = DefaultRouter()
router.register("hospital-admins", HospitalAdminViewSet, basename="hospital-admin")
router.register("notifications", NotificationViewSet, basename="admin-notification")
router.register("chats", AdminChatViewSet, basename="admin-chat")
urlpatterns = router.urls
