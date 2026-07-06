from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TranslationHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("original_text", models.TextField(help_text="The text the user typed in.")),
                ("translated_text", models.TextField(help_text="The translated result.")),
                ("source_language", models.CharField(help_text="Language code the text was translated from, e.g. 'en' or 'auto'.", max_length=10)),
                ("target_language", models.CharField(help_text="Language code the text was translated to, e.g. 'hi'.", max_length=10)),
                ("detected_language", models.CharField(blank=True, help_text="Actual detected language code when source_language was 'auto'.", max_length=10, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Translation History",
                "verbose_name_plural": "Translation History",
                "ordering": ["-created_at"],
            },
        ),
    ]
