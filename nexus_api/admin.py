from django.contrib import admin

from .models import (
    ClientProfile,
    Game,
    Player,
    Station,
    Reservation,
    Match,
    MatchPlayer,
)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "platform",
        "price",
        "available",
    )

    list_filter = (
        "category",
        "platform",
        "available",
    )

    search_fields = (
        "name",
        "category",
    )


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "phone",
        "points",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
    )


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):

    list_display = (
        "number",
        "name",
        "available",
        "created_at",
    )

    list_filter = (
        "available",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "number",
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        "reservation_number",
        "player",
        "station",
        "date",
        "time",
        "duration",
        "status",
    )

    list_filter = (
        "status",
        "station",
        "date",
    )

    search_fields = (
        "reservation_number",
        "player__name",
        "player__phone",
        "station__name",
    )

    readonly_fields = (
        "reservation_number",
        "created_at",
        "updated_at",
    )


class MatchPlayerInline(admin.TabularInline):

    model = MatchPlayer

    extra = 0

    readonly_fields = (
        "joined_at",
    )


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):

    list_display = (
        "match_number",
        "game",
        "platform",
        "date",
        "time",
        "players_count",
        "players_needed",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "platform",
        "date",
        "game",
    )

    search_fields = (
        "match_number",
        "game__name",
        "players__player__name",
        "players__player__phone",
    )

    readonly_fields = (
        "match_number",
        "created_at",
        "updated_at",
        "players_count",
    )

    inlines = [
        MatchPlayerInline
    ]

    def players_count(self, obj):
        return obj.players.count()

    players_count.short_description = "Players"


@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):

    list_display = (
        "match",
        "player",
        "joined_at",
    )

    search_fields = (
        "match__match_number",
        "player__name",
        "player__phone",
    )


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):

    list_display = (
        "client_name",
        "client_email",
        "phone",
        "points",
        "created_at",
    )

    search_fields = (
        "user__first_name",
        "user__email",
        "phone",
        "points",
    )

    readonly_fields = (
        "created_at",
    )

    def client_name(self, obj):
        return obj.user.first_name

    client_name.short_description = "Name"

    def client_email(self, obj):
        return obj.user.email

    client_email.short_description = "Email"

    def cleint_points(self , obj):
        return obj.user.points
    
    cleint_points.short_description = "points"

