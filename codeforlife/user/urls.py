from rest_framework.routers import DefaultRouter

from .views import ClassViewSet, SchoolViewSet, UserViewSet

router = DefaultRouter()
router.register("classes", ClassViewSet, basename="class")
router.register("users", UserViewSet, basename="user")
router.register("schools", SchoolViewSet, basename="school")

urlpatterns = router.urls
