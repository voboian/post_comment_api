from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    auto_reply_enabled = models.BooleanField(
        default=False
    )  # Чи увімкнена авт. відповідь
    auto_reply_delay = models.PositiveIntegerField(default=5)

    def formatted_date(self):
        return self.created_at.strftime("%m/%d/%Y, %H:%M:%S")


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    blocked = models.BooleanField(default=False)  # Для блокування коментарів з образами
