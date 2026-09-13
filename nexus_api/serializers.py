from rest_framework import serializers
from .models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "category",
            "platform",
            "price",
            "image",
            "description",
            "tags",
            "available",
            "created_at",
            "updated_at",
        ]