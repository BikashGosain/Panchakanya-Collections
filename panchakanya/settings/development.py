"""
Development settings for Panchakanya Collections.
"""

import dj_database_url
from decouple import config

from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]


# Development database
#
# If DEV_DATABASE_URL is set in .env, use PostgreSQL.
# Otherwise fall back to SQLite, so the project still runs without it.
DEV_DATABASE_URL = config("DEV_DATABASE_URL", default="")

if DEV_DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DEV_DATABASE_URL,
            conn_max_age=0,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
