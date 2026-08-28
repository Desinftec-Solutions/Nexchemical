from decouple import Csv

from .base import *
from .base import config

DEBUG = True

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,169.58.161.115,dev.nexchemical.az",
    cast=Csv(),
)

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", default="https://dev.nexchemical.az", cast=Csv()
)

# gunicorn sits behind nginx; trust its X-Forwarded-Proto so request.is_secure()
# (and CSRF origin checks) work over HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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
