"""
ASGI config for translator_project.

Used for async servers (e.g. uvicorn/daphne). Not required for the
basic gunicorn deployment described in this project's README, but
included so the project can be extended later.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translator_project.settings")

application = get_asgi_application()
