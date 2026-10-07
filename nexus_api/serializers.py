import uuid

from django.db import transaction
from rest_framework import serializers



from .models import (
    Game,
    Player,
    Station,
    Reservation,
    Match,
    MatchPlayer,
)


# =========================================================
# GAME
# =========================================================

class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = "__all__"


# =========================================================
# PLAYER
# =========================================================

class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = "__all__"

    def create(self, validated_data):

        phone = validated_data.get("phone")

        player, created = Player.objects.get_or_create(
            phone=phone,
            defaults={
                "name": validated_data.get("name")
            }
        )

        if not created:
            player.name = validated_data.get(
                "name",
                player.name
            )
            player.save()

        return player


# =========================================================
# STATION
# =========================================================

class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = "__all__"


# =========================================================
# RESERVATION
# =========================================================

class ReservationSerializer(serializers.ModelSerializer):

    player_name = serializers.CharField(
        source="player.name",
        read_only=True
    )

    player_phone = serializers.CharField(
        source="player.phone",
        read_only=True
    )

    station_name = serializers.CharField(
        source="station.name",
        read_only=True
    )

    station_number = serializers.IntegerField(
        source="station.number",
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

            "station",
            "station_name",
            "station_number",

            "date",
            "time",
            "duration",
            "status",

            "created_at",
            "updated_at",
            "reservation_group",
        ]

        read_only_fields = [
            "id",
            "reservation_number",
            "player_name",
            "player_phone",
            "station_name",
            "station_number",
            "created_at",
            "updated_at",
        ]

    def validate_duration(self, value):

        if value < 2:
            raise serializers.ValidationError(
                "La durée minimale d'une réservation est de 2 heures."
            )

        return value

    def validate(self, attrs):

        station = attrs.get("station")
        date = attrs.get("date")
        time = attrs.get("time")
        duration = attrs.get("duration")

        if not all([
            station,
            date,
            time,
            duration
        ]):
            return attrs

        if not station.available:
            raise serializers.ValidationError({
                "station": "Cette station n'est pas disponible."
            })

        from datetime import datetime, timedelta

        start = datetime.combine(
            date,
            time
        )

        end = start + timedelta(
            hours=duration
        )

        reservations = Reservation.objects.filter(
            station=station,
            date=date
        ).exclude(
            status="CANCELLED"
        )

        # Si on modifie une réservation existante,
        # on l'exclut.
        if self.instance:
            reservations = reservations.exclude(
                id=self.instance.id
            )

        for reservation in reservations:

            existing_start = datetime.combine(
                reservation.date,
                reservation.time
            )

            existing_end = (
                existing_start
                + timedelta(
                    hours=reservation.duration
                )
            )

            # Vérification du chevauchement
            if (
                existing_start < end
                and existing_end > start
            ):
                raise serializers.ValidationError({
                    "station": (
                        "Cette station est déjà réservée "
                        "pendant cette période."
                    )
                })

        return attrs

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


# =========================================================
# MATCH PLAYER
# =========================================================

class MatchPlayerSerializer(serializers.ModelSerializer):

    player_name = serializers.CharField(
        source="player.name",
        read_only=True
    )

    player_phone = serializers.CharField(
        source="player.phone",
        read_only=True
    )

    class Meta:
        model = MatchPlayer

        fields = [
            "id",
            "match",
            "player",
            "player_name",
            "player_phone",
            "joined_at",
        ]

        read_only_fields = [
            "id",
            "player_name",
            "player_phone",
            "joined_at",
        ]


# =========================================================
# MATCH
# =========================================================

class MatchSerializer(serializers.ModelSerializer):

    game_name = serializers.CharField(
        source="game.name",
        read_only=True
    )

    players_joined = serializers.IntegerField(
        read_only=True
    )

    players = MatchPlayerSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Match

        fields = [
            "id",
            "match_number",

            "game",
            "game_name",

            "platform",

            "date",
            "time",

            "players_needed",
            "players_joined",

            "status",

            "players",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "match_number",
            "game_name",
            "players_joined",
            "players",
            "created_at",
            "updated_at",
        ]


# =========================================================
# MATCH CREATE
# =========================================================

class MatchCreateSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=150
    )

    phone = serializers.CharField(
        max_length=30
    )

    game = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all()
    )

    platform = serializers.CharField(
        max_length=20
    )

    date = serializers.DateField()

    time = serializers.TimeField()

    players_needed = serializers.IntegerField(
        min_value=2,
        max_value=10
    )

    def validate(self, attrs):

        game = attrs["game"]
        platform = attrs["platform"]

        if game.platform != platform:
            raise serializers.ValidationError({
                "game": (
                    "Ce jeu n'est pas disponible "
                    "sur cette plateforme."
                )
            })

        if not game.available:
            raise serializers.ValidationError({
                "game": "Ce jeu n'est pas disponible."
            })

        return attrs
# ============================================================
# MATCH PLAYER
# ============================================================

class MatchPlayerSerializer(
    serializers.ModelSerializer
):

    player_name = serializers.CharField(
        source="player.name",
        read_only=True
    )

    player_phone = serializers.CharField(
        source="player.phone",
        read_only=True
    )

    class Meta:
        model = MatchPlayer

        fields = [
            "id",
            "match",
            "player",
            "player_name",
            "player_phone",
            "joined_at",
        ]

        read_only_fields = [
            "id",
            "player_name",
            "player_phone",
            "joined_at",
        ]


# ============================================================
# MATCH
# ============================================================

class MatchSerializer(
    serializers.ModelSerializer
):

    game_name = serializers.CharField(
        source="game.name",
        read_only=True
    )

    players_joined = serializers.IntegerField(
        read_only=True
    )

    players = MatchPlayerSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Match

        fields = [
            "id",
            "match_number",
            "game",
            "game_name",
            "platform",
            "date",
            "time",
            "players_needed",
            "players_joined",
            "status",
            "players",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "match_number",
            "game_name",
            "players_joined",
            "players",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):

        match_number = (
            f"NGM-{uuid.uuid4().hex[:8].upper()}"
        )

        validated_data[
            "match_number"
        ] = match_number

        validated_data[
            "status"
        ] = "PENDING"

        return Match.objects.create(
            **validated_data
        )


# ============================================================
# CREATE MATCH + FIRST PLAYER
# ============================================================

class MatchCreateSerializer(
    serializers.Serializer
):

    name = serializers.CharField(
        max_length=150
    )

    phone = serializers.CharField(
        max_length=30
    )

    game = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all()
    )

    platform = serializers.CharField(
        max_length=20
    )

    date = serializers.DateField()

    time = serializers.TimeField()

    players_needed = serializers.IntegerField(
        min_value=2
    )

    def validate(self, attrs):

        game = attrs["game"]

        if game.platform != attrs["platform"]:
            raise serializers.ValidationError(
                {
                    "platform":
                    "The selected platform does not match the selected game."
                }
            )

        if not game.available:
            raise serializers.ValidationError(
                {
                    "game":
                    "This game is currently unavailable."
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        name = validated_data.pop(
            "name"
        )

        phone = validated_data.pop(
            "phone"
        )

        player, created = (
            Player.objects.get_or_create(
                phone=phone,
                defaults={
                    "name": name
                }
            )
        )

        # Update player's name if necessary
        if not created and player.name != name:
            player.name = name
            player.save(
                update_fields=["name"]
            )

        match_number = (
            f"NGM-{uuid.uuid4().hex[:8].upper()}"
        )

        match = Match.objects.create(
            match_number=match_number,
            status="PENDING",
            **validated_data
        )

        MatchPlayer.objects.create(
            match=match,
            player=player
        )

        return match