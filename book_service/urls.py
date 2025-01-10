from django.urls import include, path
from rest_framework import routers

from book_service.views import BookViewSet

router = routers.DefaultRouter()
router.register("", BookViewSet, basename="books")

urlpatterns = [path("", include(router.urls))]

app_name = "book_service"
