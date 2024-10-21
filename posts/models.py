from django.db import models
from django.contrib.auth.models import User  # Для прив'язки постів та коментарів до користувачів

# Модель Post для збереження постів користувачів
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Модель Comment для збереження коментарів до постів
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)  # Чи був коментар заблокований модерацією

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"