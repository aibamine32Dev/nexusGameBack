from django.contrib import admin

from .models import (
    Game,
    Player,
    Reservation,
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
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        "reservation_number",
        "player",
        "game",
        "platform",
        "date",
        "time",
        "duration",
        "status",
    )

    list_filter = (
        "status",
        "platform",
        "date",
    )

    search_fields = (
        "reservation_number",
        "player__name",
        "player__phone",
        "game__name",
    )

    readonly_fields = (
        "reservation_number",
        "created_at",
    )