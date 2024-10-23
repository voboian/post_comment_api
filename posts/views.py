from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .schemas import PostOutSchema, PostCreateSchema, CommentCreateSchema, CommentOutSchema, RegisterUserSchema
from .models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.db.models import Count, Q
from ninja.errors import HttpError



def list_posts(request):
    # Отримуємо всі пости з бази даних
    posts = Post.objects.all().prefetch_related('author')  # Якщо author є ForeignKey

    # Використовуємо PostOutSchema для серіалізації даних
    return [
        PostOutSchema(
            id=post.id,
            title=post.title,
            content=post.content,
            author={"id": post.author.id, "username": post.author.username}, # Витягуємо інформацію про автора
            created_at=post.created_at,
            auto_reply_enabled=post.auto_reply_enabled
        )
        for post in posts
    ]

def create_post(request, data: PostCreateSchema):
    author = get_object_or_404(User, id=data.author)  # Отримуємо об'єкт User за ID
    post = Post.objects.create(title=data.title, content=data.content, author=author)
    return {"message": "Post created successfully", "post": post.id}

def retrieve_post(request, post_id: int) -> PostOutSchema:
    post = get_object_or_404(Post, id=post_id)
    return PostOutSchema(
        id=post.id,
        title=post.title,
        content=post.content,
        author={"id": post.author.id, "username": post.author.username},  # Витягуємо username автора
        created_at=post.created_at,
        auto_reply_enabled=post.auto_reply_enabled
    )

def update_post(request, post_id: int, data: PostCreateSchema):
    post = get_object_or_404(Post, id=post_id)
    for attr, value in data.model_dump().items():
        if attr == "author":  # Якщо атрибут - автор
            post.author = get_object_or_404(User, id=value)  # Отримуємо об'єкт User за ID
        else:
            setattr(post, attr, value)  # Оновлюємо інші атрибути
    post.save()
    return {"message": "Post updated successfully"}

def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return {"message": "Post deleted successfully"}


def create_comment(request, data: CommentCreateSchema):
    post = get_object_or_404(Post, id=data.post_id)
    author = get_object_or_404(User, id=data.author_id)

    comment = Comment.objects.create(
        post=post,
        content=data.content,
        author=author
    )
    return {"message": "Comment created successfully", "comment_id": comment.id}


def list_comments(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related('author')

    return [
        CommentOutSchema(
            id=comment.id,
            content=comment.content,
            author=comment.author.username,
            created_at=comment.created_at
        )
        for comment in comments
    ]


def update_comment(request, comment_id: int, data: CommentCreateSchema):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.content = data.content
    comment.save()
    return {"message": "Comment updated successfully"}


def delete_comment(request, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return {"message": "Comment deleted successfully"}

def register_user(request, data: RegisterUserSchema):
    if User.objects.filter(username=data.username).exists():
        return {"error": "Username already exists"}
    if User.objects.filter(email=data.email).exists():
        return {"error": "Email already exists"}

    user = User.objects.create(
        username=data.username,
        email=data.email,
        password=make_password(data.password)  # Хешуємо пароль перед збереженням
    )
    return {"message": "User registered successfully", "user_id": user.id}

def comments_daily_breakdown(request, date_from: str, date_to: str):
    try:
        # Конвертуємо рядкові параметри в дати
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        raise HttpError(400, "Invalid date format. Use 'YYYY-MM-DD'.")

    if date_from > date_to:
        raise HttpError(400, "'date_from' must be earlier than 'date_to'.")

    # Фільтруємо коментарі за датою
    comments = Comment.objects.filter(
        created_at__date__range=(date_from, date_to)
    )

    # Агрегуємо коментарі по днях
    daily_stats = comments.values("created_at__date").annotate(
        total_comments=Count('id'),
        blocked_comments=Count('id', filter=Q(blocked=True))
    )

    # Форматуємо результати
    result = []
    current_date = date_from
    while current_date <= date_to:
        # Перевіряємо, чи є дані за поточний день
        day_stats = next((d for d in daily_stats if d["created_at__date"] == current_date.date()), None)
        if day_stats:
            result.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "total_comments": day_stats["total_comments"],
                "blocked_comments": day_stats["blocked_comments"],
            })
        else:
            # Якщо немає даних, додаємо нулі
            result.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "total_comments": 0,
                "blocked_comments": 0,
            })
        current_date += timedelta(days=1)

    return result