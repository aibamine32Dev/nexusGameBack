from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth_serializers import (
    LoginSerializer,
    RegisterSerializer,
    client_payload,
    normalize_email,
)
from .models import ClientProfile


def session_response(user, http_status=status.HTTP_200_OK):
    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token": token.key,
            "user": client_payload(user),
        },
        status=http_status,
    )


# =========================================================
# REGISTER   POST /api/auth/register/
# =========================================================

class RegisterView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return session_response(
            user,
            status.HTTP_201_CREATED,
        )


# =========================================================
# LOGIN   POST /api/auth/login/
# =========================================================

class LoginView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=normalize_email(
                serializer.validated_data["email"]
            ),
            password=serializer.validated_data["password"],
        )

        # Same message for every failure on purpose
        # (do not reveal which emails have an account).
        # Only real clients can log in here: the admin
        # users of Django have no ClientProfile.
        if (
            user is None
            or not ClientProfile.objects.filter(
                user=user
            ).exists()
        ):
            return Response(
                {"detail": "Wrong email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return session_response(user)


# =========================================================
# CURRENT CLIENT   GET /api/auth/me/
# =========================================================

class MeView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not hasattr(request.user, "client_profile"):
            return Response(
                {"detail": "This is not a client account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(client_payload(request.user))


# =========================================================
# LOGOUT   POST /api/auth/logout/
# =========================================================

class LogoutView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        Token.objects.filter(user=request.user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
