from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import Comment
from .schemas import RegisterUserSchema
from .models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Q
from transformers import pipeline
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken, Token


classifier = pipeline("text-classification", model="unitary/toxic-bert")
text_generator = pipeline("text-generation", model="gpt2")


def generate_reply(post_content, comment_content):
    prompt = f"Post: {post_content}\nComment: {comment_content}\nReply:"

    # Зменшено max_length до 30 для коротших відповідей
    result = text_generator(
        prompt,
        max_length=30,  # Обмежуємо максимальну довжину відповіді
        num_return_sequences=1,  # Повертаємо тільки одну відповідь
        do_sample=True,  # Включаємо випадкову вибірку
        top_k=50,  # Обмежуємо кількість розглянутого набору
        top_p=0.95,  # Вибираємо з ймовірності
        truncation=True,  # Включаємо обрізання
    )

    generated_text = result[0]["generated_text"].strip()

    # Шукаємо, де починається відповідь
    reply_start = generated_text.find("Reply:") + len("Reply:")

    # Якщо "Reply:" не знайдено, беремо весь текст
    if reply_start == -1:
        reply_text = generated_text
    else:
        reply_text = generated_text[reply_start:].strip()

    # Обрізаємо зайві частини тексту
    reply_text = reply_text.split("Comment:")[
        0
    ].strip()  # Витягуємо тільки текст до наступного коментаря
    reply_text = reply_text.split("Reply:")[
        0
    ].strip()  # Витягуємо тільки текст до наступної відповіді

    # Перевірка на наявність осмисленості
    if len(reply_text) == 0:
        return (
            "I'm sorry, I didn't understand your question. Can you please rephrase it?"
        )

    return reply_text[:100]  # Обмеження довжини відповіді до 100 символів


def check_for_toxicity(comment):
    result = classifier(comment)
    toxicity_score = result[0]["score"]

    # Вважаємо коментар токсичним, якщо ймовірність вище 0.5
    if toxicity_score > 0.5:
        return True  # Токсичний коментар
    return False  # Нормальний коментар


def register_user(request, data: RegisterUserSchema):
    if User.objects.filter(username=data.username).exists():
        return {"error": "Username already exists"}
    if User.objects.filter(email=data.email).exists():
        return {"error": "Email already exists"}

    user = User.objects.create(
        username=data.username,
        email=data.email,
        password=make_password(data.password),  # Хешуємо пароль перед збереженням
    )
    return {"message": "User registered successfully", "user_id": user.id}


class JWTBearer(HttpBearer):
    def authenticate(self, request, token: Token):
        try:
            # Декодуємо токен і отримуємо користувача
            AccessToken(token)
            return token  # Повертаємо токен, якщо все успішно
        except Exception:
            return None  # Якщо токен невалідний


def comments_daily_breakdown(request, date_from: str, date_to: str):
    try:
        # Конвертуємо рядкові параметри в дати
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        return JsonResponse(
            {"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=400
        )

    if date_from > date_to:
        return JsonResponse(
            {"error": "'date_from' must be earlier than 'date_to'."}, status=400
        )

    # Фільтруємо коментарі за датою
    comments = Comment.objects.filter(
        created_at__date__range=(date_from.date(), date_to.date())
    )

    # Агрегуємо коментарі по днях
    daily_stats = comments.values("created_at__date").annotate(
        total_comments=Count("id"), blocked_comments=Count("id", filter=Q(blocked=True))
    )

    # Форматуємо результати
    result = []
    current_date = date_from.date()
    while current_date <= date_to.date():
        day_stats = next(
            (d for d in daily_stats if d["created_at__date"] == current_date), None
        )
        if day_stats:
            result.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "total_comments": day_stats["total_comments"],
                    "blocked_comments": day_stats["blocked_comments"],
                }
            )
        else:
            result.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "total_comments": 0,
                    "blocked_comments": 0,
                }
            )
        current_date += timedelta(days=1)

    return JsonResponse({"daily_comments": result}, status=200)
