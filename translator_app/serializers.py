from rest_framework import serializers
from .models import TranslationHistory


class TranslateRequestSerializer(serializers.Serializer):
    """Validates incoming POST /api/translate/ requests."""

    text = serializers.CharField(allow_blank=False, trim_whitespace=False)
    source_lang = serializers.CharField(default="auto")
    target_lang = serializers.CharField()

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Text cannot be empty or just whitespace.")
        return value


class TextToSpeechRequestSerializer(serializers.Serializer):
    """Validates incoming POST /api/speak/ requests."""

    text = serializers.CharField(allow_blank=False, trim_whitespace=False)
    lang = serializers.CharField(default="en")


class TranslationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationHistory
        fields = [
            "id",
            "original_text",
            "translated_text",
            "source_language",
            "target_language",
            "detected_language",
            "created_at",
        ]
        read_only_fields = fields
