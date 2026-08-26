#!/usr/bin/env bash
set -o errexit

uv sync --frozen

uv run python manage.py migrate --settings=panchakanya.settings.production

uv run python manage.py collectstatic --noinput --settings=panchakanya.settings.production

uv run python manage.py create_superuser --settings=panchakanya.settings.production
