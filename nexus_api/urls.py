from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    GameViewSet,
    PlayerViewSet,
    ReservationViewSet,
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
    r"reservations",
    ReservationViewSet,
    basename="reservation"
)


urlpatterns = [
    path(
        "",
        include(router.urls)
    ),
]