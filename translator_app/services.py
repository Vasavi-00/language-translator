"""
translator_app/services.py

All the "business logic" for translating text lives here, kept separate
from views.py so it's easy to test and easy to swap translation engines.

Two free engines are supported (no paid Google Cloud key required):

1. "google"  -> uses the `deep-translator` package's GoogleTranslator,
                which calls Google Translate's public web endpoint.
                This is the default and works out of the box.

2. "libre"   -> uses a LibreTranslate server (self-hosted or
                https://libretranslate.com), fully open-source.

The active engine is chosen via the TRANSLATION_ENGINE setting
(see .env.example).
"""

import uuid
import requests
from django.conf import settings
from django.core.cache import cache
from deep_translator import GoogleTranslator
from gtts import gTTS
import os


class TranslationError(Exception):
    """Raised for any translation failure (bad language, network issue, etc.)."""
    pass


# A reasonably complete set of languages supported by both Google Translate
# and LibreTranslate, with human-readable names for the UI dropdowns.
SUPPORTED_LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-CN": "Chinese (Simplified)",
    "ar": "Arabic",
    "bn": "Bengali",
    "ur": "Urdu",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "tr": "Turkish",
    "nl": "Dutch",
    "pl": "Polish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "sv": "Swedish",
    "el": "Greek",
    "he": "Hebrew",
    "uk": "Ukrainian",
}

MAX_INPUT_LENGTH = 5000


def get_supported_languages():
    """Return the dictionary of language code -> language name for the UI."""
    return SUPPORTED_LANGUAGES


def _validate_input(text, source_lang, target_lang):
    if text is None or text.strip() == "":
        raise TranslationError("Input text cannot be empty.")

    if len(text) > MAX_INPUT_LENGTH:
        raise TranslationError(
            f"Text is too long ({len(text)} characters). "
            f"Please limit input to {MAX_INPUT_LENGTH} characters."
        )

    if target_lang not in SUPPORTED_LANGUAGES or target_lang == "auto":
        raise TranslationError(f"Unsupported or invalid target language: '{target_lang}'.")

    if source_lang not in SUPPORTED_LANGUAGES:
        raise TranslationError(f"Unsupported or invalid source language: '{source_lang}'.")


def _translate_with_google(text, source_lang, target_lang):
    """Uses deep-translator's GoogleTranslator (free, no API key)."""
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        result = translator.translate(text)
        if result is None:
            raise TranslationError("Translation service returned an empty result.")
        return result
    except Exception as exc:
        raise TranslationError(f"Google translation failed: {exc}") from exc


def _translate_with_libre(text, source_lang, target_lang):
    """Uses a LibreTranslate HTTP endpoint (free / self-hostable)."""
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text",
    }
    if settings.LIBRETRANSLATE_API_KEY:
        payload["api_key"] = settings.LIBRETRANSLATE_API_KEY

    try:
        response = requests.post(settings.LIBRETRANSLATE_URL, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        translated = data.get("translatedText")
        if not translated:
            raise TranslationError("LibreTranslate returned no translated text.")
        return translated
    except requests.exceptions.Timeout as exc:
        raise TranslationError("Translation request timed out. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise TranslationError(f"Network error while translating: {exc}") from exc


def detect_language(text):
    """
    Attempts to auto-detect the language of the given text.
    Uses deep-translator's single_detection via GoogleTranslator fallback:
    we translate a snippet to English and inspect the source language
    that GoogleTranslator reports, since deep-translator doesn't expose
    a bare detection API for the free Google backend.
    """
    try:
        translator = GoogleTranslator(source="auto", target="en")
        translator.translate(text[:200])
        detected = getattr(translator, "source", None)
        return detected or "en"
    except Exception:
        # Detection failing shouldn't crash the whole request; default to English.
        return "en"


def translate_text(text, source_lang="auto", target_lang="en"):
    """
    Main entry point used by the API views.

    Returns a dict:
        {
            "translated_text": "...",
            "detected_language": "en" | None,
            "source_language": "...",
            "target_language": "...",
        }
    Raises TranslationError on any failure.
    """
    _validate_input(text, source_lang, target_lang)

    engine = getattr(settings, "TRANSLATION_ENGINE", "google")

    detected_language = None
    effective_source = source_lang

    if source_lang == "auto":
        detected_language = detect_language(text)
        effective_source = "auto"  # GoogleTranslator supports "auto" natively.

    # Simple in-process cache to avoid re-translating identical requests.
    cache_key = f"translate:{engine}:{effective_source}:{target_lang}:{hash(text)}"
    cached = cache.get(cache_key)
    if cached:
        return {
            "translated_text": cached,
            "detected_language": detected_language,
            "source_language": source_lang,
            "target_language": target_lang,
        }

    if engine == "libre":
        translated = _translate_with_libre(text, effective_source, target_lang)
    else:
        translated = _translate_with_google(text, effective_source, target_lang)

    cache.set(cache_key, translated, timeout=60 * 10)  # cache for 10 minutes

    return {
        "translated_text": translated,
        "detected_language": detected_language,
        "source_language": source_lang,
        "target_language": target_lang,
    }


def generate_speech(text, lang="en"):
    """
    Converts text to speech using gTTS and saves it as an MP3 file under
    MEDIA_ROOT/audio/. Returns the relative media URL to the generated file.
    """
    if not text or not text.strip():
        raise TranslationError("Cannot generate speech for empty text.")

    # gTTS only supports a subset of language codes; fall back to English
    # if the requested one isn't supported, rather than raising a hard error.
    try:
        tts = gTTS(text=text, lang=lang)
    except ValueError:
        tts = gTTS(text=text, lang="en")

    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(audio_dir, filename)
    tts.save(filepath)

    return f"{settings.MEDIA_URL}audio/{filename}"
