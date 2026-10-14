import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers

# Assurez-vous d'importer le modèle Player s'il est dans le même dossier (.models)
from .models import ClientProfile, Player


User = get_user_model()

PHONE_REGEX = re.compile(r"^\+?[0-9]{8,15}$")


# =========================================================
# HELPERS
# =========================================================

def normalize_email(value):
    return (value or "").strip().lower()


def normalize_phone(value):
    """
    "0550 12-34.56" -> "0550123456"
    "+213 550 12 34 56" -> "+213550123456"
    """
    return re.sub(r"[\s.\-()]", "", value or "")


def client_payload(user):
    """Data sent to the React app for a logged-in client."""

    # Récupérer les points depuis la table Player en utilisant le téléphone du profil
    player_points = 0
    try:
        phone = user.client_profile.phone
        if phone:
            player = Player.objects.filter(phone=phone).first()
            if player:
                player_points = player.points
    except Exception:
        pass

    return {
        "id": user.id,
        "name": user.first_name,
        "email": user.email,
        "phone": getattr(user.client_profile, "phone", ""),
        "points": player_points, # Points récupérés dynamiquement depuis Player
    }


# =========================================================
# REGISTER
# =========================================================

class RegisterSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField(
        max_length=150
    )

    phone = serializers.CharField(
        max_length=30
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=128,
    )

    def validate_name(self, value):

        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Enter your full name."
            )

        return value

    def validate_email(self, value):

        value = normalize_email(value)

        if User.objects.filter(
            username__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_phone(self, value):

        value = normalize_phone(value)

        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError(
                "Enter a valid phone number (8 to 15 digits)."
            )

        if ClientProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists."
            )

        return value

    def validate_password(self, value):

        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                list(error.messages)
            )

        return value

    @transaction.atomic
    def create(self, validated_data):

        try:
            with transaction.atomic():

                # CORRIGÉ : Suppression de 'points' qui n'existe pas sur le modèle User
                user = User.objects.create_user(
                    username=validated_data["email"],
                    email=validated_data["email"],
                    password=validated_data["password"],
                    first_name=validated_data["name"],
                )

                # Optionnel : Vous pouvez aussi lier ou créer un Player associé ici si nécessaire
                ClientProfile.objects.create(
                    user=user,
                    phone=validated_data["phone"],
                )

        except IntegrityError:
            # two people registering at the exact same time
            raise serializers.ValidationError({
                "detail": (
                    "An account with this email or phone "
                    "number already exists."
                )
            })

        return user


# =========================================================
# LOGIN
# =========================================================

class LoginSerializer(serializers.Serializer):

    email = serializers.CharField()

    password = serializers.CharField(
        trim_whitespace=False
    )