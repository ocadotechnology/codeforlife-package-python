"""
© Ocado Group
Created on 12/04/2024 at 16:49:33(+01:00).
"""

from rest_framework.routers import DefaultRouter

from .views import ClassViewSet, SchoolViewSet, UserViewSet

router = DefaultRouter()
router.register("classes", ClassViewSet, basename="class")
router.register("users", UserViewSet, basename="user")
router.register("schools", SchoolViewSet, basename="school")

urlpatterns = router.urls
