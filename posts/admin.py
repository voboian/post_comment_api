from django.contrib import admin
from .models import Post, Comment

# Реєстрація моделей у адмінці
admin.site.register(Post)
admin.site.register(Comment)