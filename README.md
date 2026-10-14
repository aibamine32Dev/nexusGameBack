# Nexus Games - Backend (Django REST)

## Lancer en local

```bash
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac : source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver     # en local, definir DEBUG=true si besoin
```

API : http://127.0.0.1:8000/api/

## Comptes clients

| Methode | URL                   | Corps / en-tete                | Reponse                          |
|---------|-----------------------|--------------------------------|----------------------------------|
| POST    | `/api/auth/register/` | `name, email, phone, password` | `201 { token, user }`            |
| POST    | `/api/auth/login/`    | `email, password`              | `200 { token, user }`            |
| GET     | `/api/auth/me/`       | `Authorization: Token <token>` | `200 { id, name, email, phone }` |
| POST    | `/api/auth/logout/`   | `Authorization: Token <token>` | `204`                            |

- Mot de passe hache par Django et valide (8 caracteres min., pas trop courant, pas 100 % numerique).
- Email (insensible a la casse) et telephone uniques.
- Les comptes sont visibles dans `/admin/` > **Client profiles**.
- Les administrateurs Django ne peuvent pas se connecter comme clients.
- Les reservations restent possibles **sans compte**.

## Tests

```bash
python manage.py test
```
