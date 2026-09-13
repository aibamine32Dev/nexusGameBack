from django.db import models


class Game(models.Model):
    PLATFORM_CHOICES = [
        ("PC", "PC"),
        ("PS5", "PS5"),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    image = models.URLField(
        max_length=500,
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    tags = models.JSONField(
        default=list,
        blank=True
    )
    available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name