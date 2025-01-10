from django.urls import include, path
from rest_framework.routers import DefaultRouter

from borrowings_service.views import BorrowingViewSet

app_name = "borrowings_service"

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
