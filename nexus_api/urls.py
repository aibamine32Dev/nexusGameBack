from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .auth_views import (
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
)
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

    # Client accounts
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),

    path("", include(router.urls)),
]