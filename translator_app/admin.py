from django.contrib import admin
from .models import TranslationHistory


@admin.register(TranslationHistory)
class TranslationHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "source_language", "target_language", "detected_language", "created_at")
    list_filter = ("source_language", "target_language")
    search_fields = ("original_text", "translated_text")
    readonly_fields = ("created_at",)
