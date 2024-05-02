from django.urls import path, include
from rest_framework import routers

from theatre_service.views import (
    ActorViewSet,
    GenreViewSet,
    PlayViewSet,
)

app_name = "theatre-api"

router = routers.DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)


urlpatterns = [path("", include(router.urls))]
