from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    auto_reply_enabled = models.BooleanField(default=False)  # Чи увімкнена авт. відповідь

    def formatted_date(self):
        return self.created_at.strftime("%m/%d/%Y, %H:%M:%S")

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    blocked = models.BooleanField(default=False)  # Для блокування коментарів з образами