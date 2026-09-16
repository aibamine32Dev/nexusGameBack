from rest_framework import viewsets

from .models import (
    Game,
    Player,
    Reservation,
)

from .serializers import (
    GameSerializer,
    PlayerSerializer,
    ReservationSerializer,
)


class GameViewSet(viewsets.ModelViewSet):

    queryset = Game.objects.all().order_by("-created_at")

    serializer_class = GameSerializer


class PlayerViewSet(viewsets.ModelViewSet):

    queryset = Player.objects.all().order_by("-created_at")

    serializer_class = PlayerSerializer


class ReservationViewSet(viewsets.ModelViewSet):

    queryset = Reservation.objects.all().order_by("-created_at")

    serializer_class = ReservationSerializer