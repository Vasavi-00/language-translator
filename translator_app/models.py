from django.db import models


class TranslationHistory(models.Model):
    """
    Stores every translation performed, so the UI can show a
    'recent translations' list.
    """

    original_text = models.TextField(help_text="The text the user typed in.")
    translated_text = models.TextField(help_text="The translated result.")
    source_language = models.CharField(
        max_length=10, help_text="Language code the text was translated from, e.g. 'en' or 'auto'."
    )
    target_language = models.CharField(
        max_length=10, help_text="Language code the text was translated to, e.g. 'hi'."
    )
    detected_language = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Actual detected language code when source_language was 'auto'.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Translation History"
        verbose_name_plural = "Translation History"

    def __str__(self):
        return f"[{self.source_language} -> {self.target_language}] {self.original_text[:40]}"
