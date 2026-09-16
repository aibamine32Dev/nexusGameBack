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



class Player(models.Model):
    name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=30,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} - {self.phone}"


class Reservation(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    reservation_number = models.CharField(
        max_length=30,
        unique=True
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.PROTECT,
        related_name="reservations"
    )

    platform = models.CharField(
        max_length=20
    )

    date = models.DateField()

    time = models.TimeField()

    duration = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.reservation_number