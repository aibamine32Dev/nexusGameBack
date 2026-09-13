

# Register your models here.
from django.contrib import admin
from .models import Game


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