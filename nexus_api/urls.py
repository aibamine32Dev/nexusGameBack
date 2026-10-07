from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GameViewSet,
    PlayerViewSet,
    StationViewSet,
    ReservationViewSet,
    MatchViewSet,
    MatchPlayerViewSet,
)


router = DefaultRouter()

router.register(
    r"games",
    GameViewSet,
    basename="game"
)

router.register(
    r"players",
    PlayerViewSet,
    basename="player"
)

router.register(
    r"stations",
    StationViewSet,
    basename="station"
)

router.register(
    r"reservations",
    ReservationViewSet,
    basename="reservation"
)

router.register(
    r"matches",
    MatchViewSet,
    basename="match"
)

router.register(
    r"match-players",
    MatchPlayerViewSet,
    basename="match-player"
)


urlpatterns = [
    path("", include(router.urls)),
]