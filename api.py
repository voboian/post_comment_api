from ninja import NinjaAPI
from posts.urls import post_router, comment_router, user_router, analytics_router
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken


class JWTBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Декодуємо токен і отримуємо користувача
            AccessToken(token)
            return token  # Повертаємо токен, якщо все успішно
        except Exception:
            return None  # Якщо токен невалідний

api = NinjaAPI()

# Додаємо маршрути
api.add_router("/posts/", post_router, auth=JWTBearer())
api.add_router("/comments/", comment_router, auth=JWTBearer())
api.add_router("/register/", user_router)
api.add_router("/analytics/", analytics_router)
