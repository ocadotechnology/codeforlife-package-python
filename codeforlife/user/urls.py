from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClassViewSet, UserViewSet

router = DefaultRouter()
router.register("classes", ClassViewSet, basename="class")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
