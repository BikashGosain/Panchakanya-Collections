"""
Production settings for Panchakanya Collections.
"""

import dj_database_url
from decouple import config

from .base import *

DEBUG = config("DEBUG", default=False, cast=bool)

# ============================================================
# STATIC FILES
# ============================================================

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# SECURITY
# ============================================================

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# ============================================================
# ALLOWED HOSTS
# ============================================================

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="panchakanya-collections.onrender.com,panchakanya.com,www.panchakanya.com",
).split(",")


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ============================================================
# CLOUDINARY
# ============================================================

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
}


# ============================================================
# STORAGE
# ============================================================

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
