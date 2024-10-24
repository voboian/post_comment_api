import time
from threading import Thread
from .models import Post, Comment
from .schemas import PostOutSchema, PostCreateSchema, CommentCreateSchema, CommentOutSchema
from .models import User
from django.shortcuts import get_object_or_404

from .services import check_for_toxicity, generate_reply


def list_posts(request):
    # Отримуємо всі пости з бази даних
    posts = Post.objects.all().prefetch_related("author")  # Якщо author є ForeignKey

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
    # Перевірка на токсичність
    if check_for_toxicity(data.title) or check_for_toxicity(data.content):
        return {"message": "Post is blocked due to inappropriate content."}

    # Отримуємо об'єкт User за ID
    author = get_object_or_404(User, id=data.author)

    # Створюємо пост
    post = Post.objects.create(
        title=data.title,
        content=data.content,
        author=author,
        auto_reply_enabled=data.auto_reply_enabled,
        auto_reply_delay=data.auto_reply_delay,
    )

    # Повертаємо успішну відповідь
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


def create_comment(request, data: CommentCreateSchema, comment_content: str):
    post = get_object_or_404(Post, id=data.post_id)
    author = get_object_or_404(User, id=data.author_id)

    # Перевіряємо на токсичність
    if check_for_toxicity(comment_content):
        # Створюємо заблокований коментар
        Comment.objects.create(
            post=post,
            content=comment_content,
            author=author,
            blocked=True  # Блокуємо коментар
        )
        return {"message": "Comment is blocked due to inappropriate content."}

    # Створюємо коментар
    Comment.objects.create(
        post_id=data.post_id,
        content=comment_content,
        author=request.user,
    )

    # Перевіряємо, чи увімкнена автоматична відповідь для поста
    if post.auto_reply_enabled:
        def thread_target(post_content, comment_content):
            time.sleep(post.auto_reply_delay)
            auto_reply = generate_reply(post_content, comment_content)
            # Зберігаємо автоматичну відповідь як новий коментар
            Comment.objects.create(
                post=post,
                content=auto_reply,
                author=post.author,  # або вкажіть автора відповіді, якщо потрібно
                blocked=False  # Автоматичні відповіді не блокуються
            )

        # Використовуємо затримку з поста
        Thread(target=thread_target, args=(post.content, comment_content)).start()

    return {"message": "Comment created successfully and auto-reply generated if enabled."}

def list_comments(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(blocked=False).select_related("author")

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
