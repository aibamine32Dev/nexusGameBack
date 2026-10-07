from django.db import models


# =========================================================
# GAME
# =========================================================

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


# =========================================================
# PLAYER
# =========================================================

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


# =========================================================
# STATION
# =========================================================

class Station(models.Model):

    number = models.PositiveIntegerField(
        unique=True
    )

    name = models.CharField(
        max_length=50,
        unique=True
    )

    available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# =========================================================
# RESERVATION
# =========================================================

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

    reservation_group = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_index=True
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name="reservations"
    )

    date = models.DateField()

    time = models.TimeField()

    duration = models.PositiveIntegerField(
        default=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.reservation_number
# ============================================================
# MATCH
# ============================================================

class Match(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("READY", "Ready"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    match_number = models.CharField(
        max_length=30,
        unique=True
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.PROTECT,
        related_name="matches"
    )

    platform = models.CharField(
        max_length=20
    )

    date = models.DateField()

    time = models.TimeField()

    players_needed = models.PositiveIntegerField(
        default=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.match_number

    @property
    def players_joined(self):
        return self.players.count()

    def update_status(self):
        """
        Automatically changes PENDING -> READY
        when all required players have joined.

        The admin can later change READY -> CONFIRMED.
        """

        if self.status in [
            "CANCELLED",
            "CONFIRMED",
            "COMPLETED",
        ]:
            return

        if self.players.count() >= self.players_needed:
            self.status = "READY"
        else:
            self.status = "PENDING"

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


# ============================================================
# MATCH PLAYER
# ============================================================

class MatchPlayer(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="players"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="match_players"
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "match",
                    "player",
                ],
                name="unique_player_per_match"
            )
        ]

    def __str__(self):
        return (
            f"{self.player.name} - "
            f"{self.match.match_number}"
        )