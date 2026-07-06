"""
Root URL configuration.

Routes:
    /            -> the translator app (frontend page + API)
    /admin/      -> Django admin panel
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("translator_app.urls")),
]

# Serve user-uploaded / generated media files (e.g. TTS audio) during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
