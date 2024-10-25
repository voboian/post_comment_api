from ninja import Schema
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from pydantic import EmailStr


class UserOutSchema(Schema):
    id: int
    username: str


class PostOutSchema(Schema):
    id: int
    title: str
    content: str
    author: UserOutSchema
    created_at: datetime
    auto_reply_enabled: bool


class PostCreateSchema(Schema):
    title: str
    content: str
    author: int
    auto_reply_enabled: bool
    auto_reply_delay: int

    @classmethod
    def validate_author(cls, author_id: int):
        try:
            User.objects.get(id=author_id)
        except ObjectDoesNotExist:
            raise ValueError(f"User with id {author_id} does not exist.")
        return author_id


class CommentCreateSchema(Schema):
    post_id: int
    content: str
    author_id: int


class CommentOutSchema(Schema):
    id: int
    content: str
    author: str
    created_at: datetime


class RegisterUserSchema(Schema):
    username: str
    password: str
    email: EmailStr
