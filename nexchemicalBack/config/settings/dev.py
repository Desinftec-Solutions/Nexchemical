from decouple import Csv

from .base import *
from .base import config

DEBUG = True

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv()
)

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
