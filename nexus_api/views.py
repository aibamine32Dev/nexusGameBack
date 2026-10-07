from datetime import datetime, timedelta

from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Game,
    Player,
    Station,
    Reservation,
    Match,
    MatchPlayer,
)

from .serializers import (
    GameSerializer,
    PlayerSerializer,
    StationSerializer,
    ReservationSerializer,
    MatchSerializer,
    MatchCreateSerializer,
    MatchPlayerSerializer,
)


# =========================================================
# GAME
# =========================================================

class GameViewSet(viewsets.ModelViewSet):

    queryset = Game.objects.all().order_by("name")
    serializer_class = GameSerializer


# =========================================================
# PLAYER
# =========================================================

class PlayerViewSet(viewsets.ModelViewSet):

    queryset = Player.objects.all().order_by("-created_at")
    serializer_class = PlayerSerializer


# =========================================================
# STATION
# =========================================================

class StationViewSet(viewsets.ModelViewSet):

    queryset = Station.objects.all().order_by("number")
    serializer_class = StationSerializer


# =========================================================
# RESERVATION
# =========================================================

class ReservationViewSet(viewsets.ModelViewSet):

    queryset = (
        Reservation.objects
        .select_related(
            "player",
            "station"
        )
        .all()
        .order_by("-created_at")
    )

    serializer_class = ReservationSerializer

    # =====================================================
    # AVAILABILITY
    # =====================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="availability"
    )
    def availability(self, request):

        date_value = request.query_params.get("date")
        time_value = request.query_params.get("time")
        duration_value = request.query_params.get("duration")

        if not date_value or not time_value:

            return Response(
                {
                    "detail": (
                        "date et time sont obligatoires."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            date = datetime.strptime(
                date_value,
                "%Y-%m-%d"
            ).date()

            time = datetime.strptime(
                time_value,
                "%H:%M"
            ).time()

            duration = int(
                duration_value or 2
            )

        except ValueError:

            return Response(
                {
                    "detail": (
                        "Format invalide. "
                        "date=YYYY-MM-DD, "
                        "time=HH:MM, "
                        "duration=nombre."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if duration < 2:

            return Response(
                {
                    "detail": (
                        "La durée minimale est de 2 heures."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        start = datetime.combine(
            date,
            time
        )

        end = start + timedelta(
            hours=duration
        )

        stations = (
            Station.objects
            .filter(available=True)
            .order_by("number")
        )

        reserved_station_ids = []

        reservations = (
            Reservation.objects
            .filter(date=date)
            .exclude(status="CANCELLED")
            .select_related("station")
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

                reserved_station_ids.append(
                    reservation.station.id
                )

        reserved_station_ids = list(
            set(reserved_station_ids)
        )

        available_stations = stations.exclude(
            id__in=reserved_station_ids
        )

        return Response(
            {
                "reserved_stations": (
                    reserved_station_ids
                ),

                "available_stations": [
                    {
                        "id": station.id,
                        "number": station.number,
                        "name": station.name,
                    }

                    for station in available_stations
                ],
            }
        )


# =========================================================
# MATCH PLAYER
# =========================================================

class MatchPlayerViewSet(
    viewsets.ModelViewSet
):

    queryset = (
        MatchPlayer.objects
        .select_related(
            "player",
            "match"
        )
        .all()
        .order_by("-joined_at")
    )

    serializer_class = MatchPlayerSerializer


# =========================================================
# MATCH
# =========================================================

class MatchViewSet(
    viewsets.ModelViewSet
):

    queryset = (
        Match.objects
        .select_related("game")
        .prefetch_related(
            "players__player"
        )
        .all()
        .order_by("-created_at")
    )

    serializer_class = MatchSerializer

    # =====================================================
    # CREATE MATCH
    # =====================================================

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = MatchCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        match = serializer.save()

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_201_CREATED
        )

    # =====================================================
    # JOIN MATCH
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="join"
    )
    @transaction.atomic
    def join(
        self,
        request,
        pk=None
    ):

        match = (
            Match.objects
            .select_for_update()
            .select_related("game")
            .get(pk=pk)
        )

        if match.status != "PENDING":

            return Response(
                {
                    "detail": (
                        "This match is no longer "
                        "accepting players."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        name = request.data.get("name")
        phone = request.data.get("phone")

        if not name or not phone:

            return Response(
                {
                    "detail": (
                        "Name and phone are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        platform = request.data.get("platform")

        if (
            platform
            and platform != match.platform
        ):

            return Response(
                {
                    "detail": (
                        "The platform does not "
                        "match this match."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        current_players = (
            MatchPlayer.objects
            .filter(match=match)
            .count()
        )

        if current_players >= match.players_needed:

            return Response(
                {
                    "detail": (
                        "This match is already full."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        player, created = (
            Player.objects.get_or_create(
                phone=phone,
                defaults={
                    "name": name
                }
            )
        )

        if not created and player.name != name:

            player.name = name

            player.save(
                update_fields=["name"]
            )

        already_joined = (
            MatchPlayer.objects
            .filter(
                match=match,
                player=player
            )
            .exists()
        )

        if already_joined:

            return Response(
                {
                    "detail": (
                        "You have already joined "
                        "this match."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        MatchPlayer.objects.create(
            match=match,
            player=player
        )

        current_players = (
            MatchPlayer.objects
            .filter(match=match)
            .count()
        )

        if current_players >= match.players_needed:

            match.status = "READY"

            match.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        match.refresh_from_db()

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_200_OK
        )

    # =====================================================
    # OPEN MATCHES
    # =====================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="open"
    )
    def open_matches(
        self,
        request
    ):

        matches = (
            Match.objects
            .filter(status="PENDING")
            .select_related("game")
            .prefetch_related(
                "players__player"
            )
            .order_by("-created_at")
        )

        return Response(
            MatchSerializer(
                matches,
                many=True
            ).data
        )

    # =====================================================
    # CONFIRM MATCH
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="confirm"
    )
    def confirm(
        self,
        request,
        pk=None
    ):

        match = self.get_object()

        if match.status != "READY":

            return Response(
                {
                    "detail": (
                        "The match must be full "
                        "before confirmation."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        match.status = "CONFIRMED"

        match.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            MatchSerializer(match).data
        )

    # =====================================================
    # CANCEL MATCH
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel"
    )
    def cancel(
        self,
        request,
        pk=None
    ):

        match = self.get_object()

        if match.status == "COMPLETED":

            return Response(
                {
                    "detail": (
                        "A completed match "
                        "cannot be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        match.status = "CANCELLED"

        match.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            MatchSerializer(match).data
        )

    # =====================================================
    # COMPLETE MATCH
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="complete"
    )
    def complete(
        self,
        request,
        pk=None
    ):

        match = self.get_object()

        if match.status != "CONFIRMED":

            return Response(
                {
                    "detail": (
                        "Only a confirmed match "
                        "can be completed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        match.status = "COMPLETED"

        match.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            MatchSerializer(match).data
        )