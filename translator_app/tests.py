"""
Unit and API tests for the translator app.

Run with:
    python manage.py test
"""
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import TranslationHistory
from .services import translate_text, TranslationError, get_supported_languages


class ServiceLayerTests(TestCase):
    """Tests for translator_app/services.py business logic."""

    def test_empty_text_raises_error(self):
        with self.assertRaises(TranslationError):
            translate_text("", source_lang="en", target_lang="hi")

    def test_invalid_target_language_raises_error(self):
        with self.assertRaises(TranslationError):
            translate_text("Hello", source_lang="en", target_lang="xx-invalid")

    def test_too_long_text_raises_error(self):
        long_text = "a" * 6000
        with self.assertRaises(TranslationError):
            translate_text(long_text, source_lang="en", target_lang="hi")

    @patch("translator_app.services._translate_with_google")
    def test_successful_translation_calls_google_engine(self, mock_translate):
        mock_translate.return_value = "Bonjour"
        result = translate_text("Hello", source_lang="en", target_lang="fr")
        self.assertEqual(result["translated_text"], "Bonjour")
        self.assertEqual(result["target_language"], "fr")

    def test_supported_languages_contains_common_codes(self):
        languages = get_supported_languages()
        self.assertIn("en", languages)
        self.assertIn("hi", languages)
        self.assertIn("auto", languages)


class TranslateAPITests(TestCase):
    """Tests for the /api/translate/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("translator_app:api_translate")

    def test_missing_text_returns_400(self):
        response = self.client.post(self.url, {"target_lang": "hi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_target_lang_returns_400(self):
        response = self.client.post(self.url, {"text": "Hello"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("translator_app.views.translate_text")
    def test_valid_translation_returns_200_and_saves_history(self, mock_translate):
        mock_translate.return_value = {
            "translated_text": "Hola",
            "detected_language": "en",
            "source_language": "auto",
            "target_language": "es",
        }
        response = self.client.post(
            self.url,
            {"text": "Hello", "source_lang": "auto", "target_lang": "es"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["translated_text"], "Hola")
        self.assertEqual(TranslationHistory.objects.count(), 1)


class HistoryAPITests(TestCase):
    """Tests for the /api/history/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("translator_app:api_history")
        TranslationHistory.objects.create(
            original_text="Hello",
            translated_text="Hola",
            source_language="en",
            target_language="es",
        )

    def test_history_returns_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["translated_text"], "Hola")


class LanguagesAPITests(TestCase):
    """Tests for the /api/languages/ endpoint."""

    def test_languages_returns_dict(self):
        client = APIClient()
        url = reverse("translator_app:api_languages")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("en", response.data)


class FrontendViewTests(TestCase):
    """Basic smoke test for the HTML page."""

    def test_index_page_loads(self):
        response = self.client.get(reverse("translator_app:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Language Translator")
