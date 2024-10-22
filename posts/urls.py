from ninja import Router
from .views import (
    list_posts, create_post, retrieve_post, update_post, delete_post,
    list_comments, create_comment, update_comment, delete_comment, register_user
)

post_router = Router()
comment_router = Router()
user_router = Router()

# Маршрути для постів
post_router.add_api_operation("/", methods=["GET"], view_func=list_posts)
post_router.add_api_operation("/create/", methods=["POST"], view_func=create_post)
post_router.add_api_operation("/{post_id}/", methods=["GET"], view_func=retrieve_post)
post_router.add_api_operation("/{post_id}/", methods=["PUT"], view_func=update_post)
post_router.add_api_operation("/{post_id}/", methods=["DELETE"], view_func=delete_post)

# Маршрути для коментарів
post_router.add_api_operation("/{post_id}/comments", methods=["GET"], view_func=list_comments)
comment_router.add_api_operation("/create", methods=["POST"], view_func=create_comment)
comment_router.add_api_operation("/{comment_id}/", methods=["PUT"], view_func=update_comment)
comment_router.add_api_operation("/{comment_id}/", methods=["DELETE"], view_func=delete_comment)

user_router.add_api_operation("/", methods=["POST"], view_func=register_user)