from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .schemas import PostOutSchema, PostCreateSchema, CommentCreateSchema, CommentOutSchema, RegisterUserSchema
from .models import User
from django.contrib.auth.hashers import make_password



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
