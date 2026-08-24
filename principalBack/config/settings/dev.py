from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "169.58.161.115"]

STATIC_URL = 'static/'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
