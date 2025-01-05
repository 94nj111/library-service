from django.urls import path, include
from rest_framework import routers

from book_service.views import BookViewSet

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="books")

urlpatterns = [path("", include(router.urls))]

app_name = "book_service"
