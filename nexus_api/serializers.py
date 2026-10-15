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
            defaults={"name": validated_data.get("name")}
        )
        if not created:
            player.name = validated_data.get("name", player.name)
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

    player_name = serializers.CharField(source="player.name", read_only=True)
    player_phone = serializers.CharField(source="player.phone", read_only=True)
    station_name = serializers.CharField(source="station.name", read_only=True)
    station_number = serializers.IntegerField(source="station.number", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id", "reservation_number",
            "player", "player_name", "player_phone",
            "station", "station_name", "station_number",
            "date", "time", "duration", "status",
            "created_at", "updated_at", "reservation_group",
        ]
        read_only_fields = [
            "id", "reservation_number",
            "player_name", "player_phone",
            "station_name", "station_number",
            "created_at", "updated_at",
        ]

    def validate_duration(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "La durée minimale d'une réservation est de une heure."
            )
        return value

    def validate(self, attrs):
        from datetime import datetime, timedelta

        station = attrs.get("station")
        date = attrs.get("date")
        time = attrs.get("time")
        duration = attrs.get("duration")

        if not all([station, date, time, duration]):
            return attrs

        if not station.available:
            raise serializers.ValidationError({"station": "Cette station n'est pas disponible."})

        start = datetime.combine(date, time)
        end = start + timedelta(hours=duration)

        reservations = Reservation.objects.filter(station=station, date=date).exclude(status="CANCELLED")
        if self.instance:
            reservations = reservations.exclude(id=self.instance.id)

        for reservation in reservations:
            existing_start = datetime.combine(reservation.date, reservation.time)
            existing_end = existing_start + timedelta(hours=reservation.duration)
            if existing_start < end and existing_end > start:
                raise serializers.ValidationError({"station": "Cette station est déjà réservée pendant cette période."})

        return attrs

    def create(self, validated_data):
        reservation_number = f"NG-{uuid.uuid4().hex[:8].upper()}"
        validated_data["reservation_number"] = reservation_number
        return Reservation.objects.create(**validated_data)


# =========================================================
# MATCH PLAYER
# =========================================================

class MatchPlayerSerializer(serializers.ModelSerializer):

    player_name = serializers.CharField(source="player.name", read_only=True)
    player_phone = serializers.CharField(source="player.phone", read_only=True)

    class Meta:
        model = MatchPlayer
        fields = ["id", "match", "player", "player_name", "player_phone", "joined_at"]
        read_only_fields = ["id", "player_name", "player_phone", "joined_at"]


# =========================================================
# MATCH
# =========================================================

class MatchSerializer(serializers.ModelSerializer):

    game_name = serializers.CharField(source="game.name", read_only=True)
    players_joined = serializers.IntegerField(read_only=True)
    remaining_slots = serializers.IntegerField(read_only=True)
    players = MatchPlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            "id", "match_number",
            "game", "game_name",
            "platform",
            "date", "time",
            "players_needed",
            "accompanying_players",
            "creator_name",
            "creator_phone",
            "players_joined",
            "remaining_slots",
            "status",
            "players",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "match_number",
            "game_name",
            "players_joined",
            "remaining_slots",
            "players",
            "created_at", "updated_at",
        ]


# =========================================================
# MATCH CREATE SERIALIZER
# =========================================================

class MatchCreateSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30)
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    platform = serializers.CharField(max_length=20)
    date = serializers.DateField()
    time = serializers.TimeField()

    # Total players for the match (8 to 10)
    players_needed = serializers.IntegerField(min_value=8, max_value=10)

    # Players accompanying the creator (creator NOT counted here)
    # creator (1) + accompanying_players must be < players_needed
    accompanying_players = serializers.IntegerField(min_value=0, default=0)

    def validate(self, attrs):
        game = attrs["game"]
        platform = attrs["platform"]

        if game.platform != platform:
            raise serializers.ValidationError({
                "platform": "The selected platform does not match the selected game."
            })

        if not game.available:
            raise serializers.ValidationError({"game": "This game is currently unavailable."})

        players_needed = attrs["players_needed"]
        accompanying = attrs.get("accompanying_players", 0)

        # creator (1) + accompanying must be <= players_needed
        creator_group = 1 + accompanying
        if creator_group > players_needed:
            raise serializers.ValidationError({
                "accompanying_players": (
                    f"Creator group ({creator_group}) exceeds total players needed ({players_needed}). "
                    "Reduce the number of accompanying players."
                )
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        name = validated_data.pop("name")
        phone = validated_data.pop("phone")
        accompanying_players = validated_data.pop("accompanying_players", 0)

        player, created = Player.objects.get_or_create(
            phone=phone,
            defaults={"name": name}
        )
        if not created and player.name != name:
            player.name = name
            player.save(update_fields=["name"])

        match_number = f"NGM-{uuid.uuid4().hex[:8].upper()}"

        match = Match.objects.create(
            match_number=match_number,
            status="PENDING",
            accompanying_players=accompanying_players,
            creator_name=name,
            creator_phone=phone,
            **validated_data
        )

        # Register the creator as first player
        MatchPlayer.objects.create(match=match, player=player)

        # Register each accompanying player as a placeholder entry
        # using a generated phone so they occupy a slot
        for i in range(accompanying_players):
            companion_phone = f"COMP-{match.match_number}-{i+1}"
            companion_name = f"Companion {i+1} of {name}"
            companion, _ = Player.objects.get_or_create(
                phone=companion_phone,
                defaults={"name": companion_name}
            )
            MatchPlayer.objects.create(match=match, player=companion)

        match.refresh_from_db()
        return match
