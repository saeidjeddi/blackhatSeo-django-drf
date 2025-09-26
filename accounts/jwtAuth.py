import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

SECRET_KEY = "django-insecure-nuzd_n&+g_@uk$t$#t(26=uf-27b14a2nl+015q(hun%cgt$#v"

class AuthenticatedUser:
    def __init__(self, username, email, superuser, active):
        self.username = username
        self.email = email
        self.active = active
        self.superuser = superuser
        self.is_authenticated = True

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("username")
            email = payload.get("email")
            active = payload.get("active", False)
            superuser = payload.get("superuser", False)

            if not username or not email:
                raise AuthenticationFailed("User information incomplete in token", code=401)

            if not (active or superuser):
                raise AuthenticationFailed("User does not have support access", code=403)

            user = AuthenticatedUser(username=username, email=email, active=active, superuser=superuser)
            return (user, None)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired", code=401)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token", code=401)