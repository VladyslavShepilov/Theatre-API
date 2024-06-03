from rest_framework import routers

from theatre_service.views import (
    ActorViewSet,
    GenreViewSet,
    PlayViewSet,
    TheatreHallViewSet,
    PerformanceViewSet,
    ReservationViewSet,
)

app_name = "theatre-api"

router = routers.DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)
router.register("theatre_halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservation", ReservationViewSet)

urlpatterns = router.urls
