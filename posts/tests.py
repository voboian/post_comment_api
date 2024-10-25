from datetime import datetime, timedelta
from django.test import TestCase
from ninja.testing import TestClient
from rest_framework_simplejwt.tokens import RefreshToken
from .urls import post_router, analytics_router
from .models import User, Post, Comment


class PostCreateTest(TestCase):
    def setUp(self):
        self.client = TestClient(post_router)
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.auth_headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_create_post(self):
        post_data = {
            "title": "Test Post",
            "content": "This is a test post content.",
            "author": self.user.id,
            "auto_reply_enabled": True,
            "auto_reply_delay": 10,
        }
        response = self.client.post(
            "/create/", json=post_data, headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 200)


class CommentsAnalyticsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(
            title="Test Post",
            content="Test Content",
            author=self.user,
            auto_reply_enabled=False,
            auto_reply_delay=5,
            created_at=datetime.now() - timedelta(days=1),
        )
        Comment.objects.create(
            post=self.post,
            content="Test Comment 1",
            author=self.user,
            created_at=datetime.now() - timedelta(days=1),
            blocked=False,
        )
        Comment.objects.create(
            post=self.post,
            content="Test Comment 2",
            author=self.user,
            created_at=datetime.now(),
            blocked=True,
        )

    def test_comments_daily_breakdown(self):
        client = TestClient(analytics_router)
        date_from = (datetime.now() - timedelta(days=1)).date()  # Вчора
        date_to = datetime.now().date()
        response = client.get(
            f"/comments-daily-breakdown?date_from={date_from.isoformat()}&date_to={date_to.isoformat()}"
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn("daily_comments", response_json)
        self.assertIsInstance(response_json["daily_comments"], list)
        daily_comments = response_json["daily_comments"]
        self.assertEqual(len(daily_comments), 2)

        for comment in daily_comments:
            self.assertIn("date", comment)
            self.assertIn("total_comments", comment)
            self.assertIn("blocked_comments", comment)

        self.assertEqual(daily_comments[0]["date"], date_from.isoformat())
        self.assertEqual(daily_comments[0]["total_comments"], 1)
        self.assertEqual(daily_comments[0]["blocked_comments"], 0)

        self.assertEqual(daily_comments[1]["date"], date_to.isoformat())
        self.assertEqual(daily_comments[1]["total_comments"], 1)
        self.assertEqual(daily_comments[1]["blocked_comments"], 1)
