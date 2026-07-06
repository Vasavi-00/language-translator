"""
WSGI config for translator_project.

Used by gunicorn / traditional WSGI servers in production.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translator_project.settings")

application = get_wsgi_application()
