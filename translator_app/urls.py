from django.urls import path
from . import views

app_name = "translator_app"

urlpatterns = [
    # Frontend page
    path("", views.index, name="index"),

    # REST API endpoints
    path("api/translate/", views.translate_view, name="api_translate"),
    path("api/speak/", views.speak_view, name="api_speak"),
    path("api/history/", views.history_view, name="api_history"),
    path("api/languages/", views.languages_view, name="api_languages"),
]
