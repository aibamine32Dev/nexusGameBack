from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import ClientProfile, Game, Player, Station


User = get_user_model()

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
ME_URL = "/api/auth/me/"
LOGOUT_URL = "/api/auth/logout/"


def valid_payload(**changes):
    data = {
        "name": "Sami Benali",
        "email": "Sami@Example.com",
        "phone": "0550 12 34 56",
        "password": "Str0ng-Pass-2026",
    }
    data.update(changes)
    return data


class RegisterTests(APITestCase):

    def test_register_creates_account_and_returns_token(self):
        response = self.client.post(
            REGISTER_URL, valid_payload(), format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["token"])

        # email is lower-cased, phone is cleaned
        self.assertEqual(
            response.data["user"]["email"], "sami@example.com"
        )
        self.assertEqual(response.data["user"]["phone"], "0550123456")
        self.assertEqual(response.data["user"]["name"], "Sami Benali")

        self.assertEqual(ClientProfile.objects.count(), 1)

    def test_password_is_hashed(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")

        user = User.objects.get(username="sami@example.com")
        self.assertNotEqual(user.password, "Str0ng-Pass-2026")
        self.assertTrue(user.check_password("Str0ng-Pass-2026"))

    def test_duplicate_email_rejected_any_case(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")

        response = self.client.post(
            REGISTER_URL,
            valid_payload(
                email="SAMI@example.com", phone="0661000000"
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_duplicate_phone_rejected(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")

        response = self.client.post(
            REGISTER_URL,
            valid_payload(
                email="other@example.com", phone="0550-12-34-56"
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)

    def test_invalid_data_rejected(self):
        for field, value in [
            ("email", "not-an-email"),
            ("phone", "abc"),
            ("phone", "123"),
            ("name", " "),
            ("password", "short"),
            ("password", "password"),
            ("password", "12345678"),
        ]:
            with self.subTest(field=field, value=value):
                response = self.client.post(
                    REGISTER_URL,
                    valid_payload(**{field: value}),
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

        self.assertEqual(User.objects.count(), 0)


class LoginTests(APITestCase):

    def setUp(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")

    def test_login_ok_any_email_case(self):
        response = self.client.post(
            LOGIN_URL,
            {
                "email": " SAMI@example.com ",
                "password": "Str0ng-Pass-2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["token"])
        self.assertEqual(response.data["user"]["phone"], "0550123456")

    def test_wrong_password_and_unknown_email_same_error(self):
        wrong = self.client.post(
            LOGIN_URL,
            {"email": "sami@example.com", "password": "nope-nope"},
            format="json",
        )
        unknown = self.client.post(
            LOGIN_URL,
            {"email": "ghost@example.com", "password": "nope-nope"},
            format="json",
        )

        self.assertEqual(wrong.status_code, 400)
        self.assertEqual(unknown.status_code, 400)
        self.assertEqual(wrong.data, unknown.data)

    def test_django_admin_user_cannot_login_as_client(self):
        User.objects.create_superuser(
            "boss", "boss@example.com", "Adm1n-Pass-2026"
        )

        response = self.client.post(
            LOGIN_URL,
            {"email": "boss", "password": "Adm1n-Pass-2026"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)


class SessionTests(APITestCase):

    def setUp(self):
        response = self.client.post(
            REGISTER_URL, valid_payload(), format="json"
        )
        self.token = response.data["token"]

    def test_me_requires_token(self):
        self.assertEqual(self.client.get(ME_URL).status_code, 401)

        self.client.credentials(HTTP_AUTHORIZATION="Token wrong")
        self.assertEqual(self.client.get(ME_URL).status_code, 401)

    def test_me_returns_client(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token}"
        )
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "sami@example.com")

    def test_logout_deletes_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token}"
        )

        self.assertEqual(
            self.client.post(LOGOUT_URL).status_code, 204
        )
        self.assertFalse(Token.objects.exists())
        self.assertEqual(self.client.get(ME_URL).status_code, 401)


class ExistingFeaturesStillWorkTests(APITestCase):
    """Accounts must not change anything for guests."""

    def test_guest_can_still_use_public_endpoints(self):
        Station.objects.create(number=1, name="PC-01")
        Game.objects.create(
            name="FIFA", category="Sport", platform="PS5", price=500
        )

        self.assertEqual(self.client.get("/api/games/").status_code, 200)
        self.assertEqual(self.client.get("/api/stations/").status_code, 200)
        self.assertEqual(
            self.client.get(
                "/api/reservations/availability/"
                "?date=2030-01-01&time=18:00&duration=2"
            ).status_code,
            200,
        )

    def test_guest_reservation_without_account(self):
        station = Station.objects.create(number=1, name="PC-01")
        player = Player.objects.create(name="Guest", phone="0770000000")

        response = self.client.post(
            "/api/reservations/",
            {
                "player": player.id,
                "station": station.id,
                "date": "2030-01-01",
                "time": "18:00",
                "duration": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_bad_token_does_not_break_public_endpoints(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token stale")

        self.assertEqual(self.client.get("/api/games/").status_code, 200)
