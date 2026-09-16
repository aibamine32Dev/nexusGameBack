from rest_framework import serializers

from .models import (
    Game,
    Player,
    Reservation,
)


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


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player

        fields = [
            "id",
            "name",
            "phone",
            "created_at",
            "updated_at",
        ]


class ReservationSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(
        source="player.name",
        read_only=True
    )

    player_phone = serializers.CharField(
        source="player.phone",
        read_only=True
    )

    game_name = serializers.CharField(
        source="game.name",
        read_only=True
    )

    class Meta:
        model = Reservation

        fields = [
            "id",
            "reservation_number",

            "player",
            "player_name",
            "player_phone",

            "game",
            "game_name",

            "platform",
            "date",
            "time",
            "duration",

            "status",

            "created_at",
        ]

        read_only_fields = [
            "id",
            "reservation_number",
            "player_name",
            "player_phone",
            "game_name",
            "created_at",
        ]

    def create(self, validated_data):
        import uuid

        reservation_number = (
            f"NG-{uuid.uuid4().hex[:8].upper()}"
        )

        validated_data["reservation_number"] = (
            reservation_number
        )

        return Reservation.objects.create(
            **validated_data
        )