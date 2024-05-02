from django.urls import path, include
from rest_framework import routers

from theatre_service.views import (
    ActorViewSet,
    GenreViewSet,
    PlayViewSet,
    TheatreHallViewSet,
)

app_name = "theatre-api"

router = routers.DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)
router.register("theatre_halls", TheatreHallViewSet)


urlpatterns = [path("", include(router.urls))]
