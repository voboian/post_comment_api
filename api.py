from ninja import NinjaAPI
from posts.services import JWTBearer
from posts.urls import post_router, comment_router, user_router, analytics_router

api = NinjaAPI()

api.add_router("/posts/", post_router, auth=JWTBearer())
api.add_router("/comments/", comment_router, auth=JWTBearer())
api.add_router("/register/", user_router)
api.add_router("/analytics/", analytics_router)
