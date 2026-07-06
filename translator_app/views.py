from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import TranslationHistory
from .serializers import (
    TranslateRequestSerializer,
    TextToSpeechRequestSerializer,
    TranslationHistorySerializer,
)
from .services import (
    translate_text,
    generate_speech,
    get_supported_languages,
    TranslationError,
)


def index(request):
    """Renders the single-page frontend UI."""
    languages = get_supported_languages()
    return render(request, "translator_app/index.html", {"languages": languages})


@api_view(["GET"])
def languages_view(request):
    """
    GET /api/languages/
    Returns the list of supported languages as {code: name}.
    """
    return Response(get_supported_languages(), status=status.HTTP_200_OK)


@api_view(["POST"])
def translate_view(request):
    """
    POST /api/translate/
    Body: { "text": "...", "source_lang": "auto", "target_lang": "hi" }

    Returns: {
        "original_text": "...",
        "translated_text": "...",
        "source_language": "auto",
        "detected_language": "en",
        "target_language": "hi"
    }
    """
    serializer = TranslateRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid request.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    text = serializer.validated_data["text"]
    source_lang = serializer.validated_data.get("source_lang", "auto")
    target_lang = serializer.validated_data["target_lang"]

    try:
        result = translate_text(text, source_lang=source_lang, target_lang=target_lang)
    except TranslationError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:  # noqa: BLE001 - catch-all so the API never 500s silently
        return Response(
            {"error": f"Unexpected server error: {exc}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Save to history (best-effort; failure here shouldn't break the response).
    try:
        TranslationHistory.objects.create(
            original_text=text,
            translated_text=result["translated_text"],
            source_language=source_lang,
            target_language=target_lang,
            detected_language=result.get("detected_language"),
        )
    except Exception:
        pass

    return Response(
        {
            "original_text": text,
            "translated_text": result["translated_text"],
            "source_language": source_lang,
            "detected_language": result.get("detected_language"),
            "target_language": target_lang,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def speak_view(request):
    """
    POST /api/speak/
    Body: { "text": "...", "lang": "hi" }
    Returns: { "audio_url": "/media/audio/xxxx.mp3" }
    """
    serializer = TextToSpeechRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid request.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    text = serializer.validated_data["text"]
    lang = serializer.validated_data.get("lang", "en")

    try:
        audio_url = generate_speech(text, lang=lang)
    except TranslationError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:  # noqa: BLE001
        return Response(
            {"error": f"Unexpected server error: {exc}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"audio_url": audio_url}, status=status.HTTP_200_OK)


@api_view(["GET"])
def history_view(request):
    """
    GET /api/history/?limit=10
    Returns the most recent translations.
    """
    try:
        limit = int(request.GET.get("limit", 10))
        limit = max(1, min(limit, 100))
    except ValueError:
        limit = 10

    history = TranslationHistory.objects.all()[:limit]
    serializer = TranslationHistorySerializer(history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
