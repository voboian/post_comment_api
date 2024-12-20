# post_comment_api

This project is a simple API built with Django Ninja to manage posts and comments. It includes features such as automatic reply generation using GPT-2, content moderation with `unitary/toxic-bert`, and analytics for comments.

## Features
- **Post and Comment Management**: Create, update, delete posts and comments.
- **Automatic Comment Reply**: GPT-2 powered automatic reply for posts with a delay option.
- **Content Moderation**: Check for toxic comments using `unitary/toxic-bert`.
- **Comment Analytics**: Daily breakdown of total and blocked comments.

## Installation

* Clone the repository:
   ```bash
   git clone https://github.com/voboian/post_comment_api.git
   cd post_comment_api
* Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    For Windows: .venv\Scripts\activate
* Install dependencies:
    ```bash
    pip install -r requirements.txt
* Apply migrations:
    ```bash
    python manage.py migrate
* Create a superuser:
    ```bash
    python manage.py createsuperuser
* Run the development server:
    ```bash
  python manage.py runserver
## Authentication
This API uses JWT for authentication. You can obtain and refresh your token using the following endpoints:

- **Obtain Token**: 
  - `POST /api/token/`: Obtain a new access and refresh token by providing your username and password.

- **Refresh Token**: 
  - `POST /api/token/refresh/`: Refresh your access token using the refresh token.
# API Endpoints
- **Post Endpoints:**
- `GET /api/posts/:` Retrieve all posts.
- `POST /api/posts/create/:` Create a new post.
- `GET /api/posts/{post_id}/:` Retrieve a specific post by ID.
- `PUT /api/posts/{post_id}/:` Update a specific post.
- `DELETE /api/posts/{post_id}/:` Delete a specific post.
- **Comment Endpoints:**
- `GET /api/posts/{post_id}/comments:` Retrieve all comments for a post.
- `POST /api/comments/create:` Create a comment.
- `PUT /api/comments/{comment_id}/:` Update a specific comment.
- `DELETE /api/comments/{comment_id}/:` Delete a specific comment.
- **User Registration:**
- `POST /api/register/:` Register a new user.
- **Comment Analytics:**
- `GET /api/analytics/comments-daily-breakdown?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD:` Retrieve a daily breakdown of total and blocked comments between the provided dates.
* To run tests, use the following command:
    ```bash
    python manage.py test