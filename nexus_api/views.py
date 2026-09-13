from rest_framework import viewsets

from .models import Game
from .serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by("-created_at")
    serializer_class = GameSerializer