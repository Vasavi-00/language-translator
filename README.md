# 🌍 LingoStamp — Language Translation Web App

A production-ready, full-stack language translation tool built with **Django**,
**Django REST Framework**, and vanilla JavaScript/Bootstrap. No paid API keys
required — translation is powered by the free `deep-translator` package
(Google Translate's public endpoint) with an optional LibreTranslate backend.

---

## ✨ Features

- Translate text between 30+ languages
- Auto-detect source language
- Swap source/target languages with one click
- Copy translated text to clipboard
- Text-to-speech playback (via gTTS) for both input and output text
- Live character counter with a hard limit
- Translation history (stored in the database, shown in the UI)
- Dark mode with persisted preference
- Responsive, distinctively-styled UI (no Bootstrap-default look)
- Robust error handling: empty input, oversized input, invalid language,
  network failures, timeouts
- REST API you can consume from any other client
- Deployment-ready: Gunicorn, WhiteNoise, environment-based settings

---

## 🧱 Tech Stack

| Layer      | Tech |
|------------|------|
| Backend    | Django 5, Django REST Framework |
| Frontend   | HTML5, CSS3, Bootstrap 5, vanilla JavaScript |
| Translation| `deep-translator` (free Google Translate backend) or LibreTranslate |
| Speech     | gTTS (Google Text-to-Speech) |
| Server     | Gunicorn + WhiteNoise (static files) |
| Database   | SQLite (default; swap for Postgres in production if you like) |

---

## 📁 Project Structure

```
LanguageTranslator/
├── manage.py                  # Django's command-line management tool
├── requirements.txt           # Python dependencies
├── Procfile                   # Process definitions for Render/Railway/Heroku
├── runtime.txt                # Python version pin for some hosts
├── .env.example                # Template for environment variables
├── .gitignore
├── README.md
│
├── translator_project/        # Django project (global settings & routing)
│   ├── settings.py             # All configuration (see comments inline)
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # Entry point for Gunicorn
│   └── asgi.py                 # Entry point for async servers
│
├── translator_app/            # The translator Django app
│   ├── models.py                # TranslationHistory model
│   ├── views.py                 # Page view + REST API views
│   ├── urls.py                  # App-level routing (/, /api/...)
│   ├── serializers.py           # DRF request/response validation
│   ├── services.py              # Translation & TTS business logic
│   ├── admin.py                 # Django admin registration
│   ├── tests.py                 # Unit + API tests
│   └── migrations/               # Database migrations
│
├── templates/translator_app/
│   └── index.html               # Single-page frontend UI
│
├── static/
│   ├── css/style.css            # All styling (light + dark mode)
│   ├── js/script.js             # All frontend behavior
│   └── images/                  # Place any images/icons here
│
├── media/                      # Generated files (gTTS audio) — created at runtime
├── screenshots/                # Put your app screenshots here for the README
└── docs/                       # Extra documentation, diagrams, etc.
```

---

## 🚀 Step 1 — Create/activate the environment

```bash
# Create a virtual environment (isolates this project's Python packages)
python -m venv venv

# Activate it
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

You'll know it worked because your terminal prompt will be prefixed with `(venv)`.

## 🚀 Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs Django, DRF, deep-translator, gTTS, gunicorn, whitenoise,
django-cors-headers, Pillow, requests, and python-dotenv.

## 🚀 Step 3 — Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and adjust values if needed. The defaults work fine for local
development — you do **not** need any paid API key.

## 🚀 Step 4 — Run migrations

```bash
python manage.py migrate
```

This creates the SQLite database and the `TranslationHistory` table.

## 🚀 Step 5 — (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

Lets you view translation history at `/admin/`.

## 🚀 Step 6 — Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser. That's it — translate away!

---

## 🔌 REST API Reference

All endpoints return JSON.

### `GET /api/languages/`
Returns supported languages as `{code: name}`.

### `POST /api/translate/`
```json
{ "text": "Good morning", "source_lang": "auto", "target_lang": "hi" }
```
Response:
```json
{
  "original_text": "Good morning",
  "translated_text": "सुप्रभात",
  "source_language": "auto",
  "detected_language": "en",
  "target_language": "hi"
}
```
Errors return `400` with `{"error": "..."}` for empty text, text over 5000
characters, or an unsupported language code.

### `POST /api/speak/`
```json
{ "text": "सुप्रभात", "lang": "hi" }
```
Response: `{ "audio_url": "/media/audio/<uuid>.mp3" }`

### `GET /api/history/?limit=10`
Returns the most recent translations as a list.

Test it with curl:
```bash
curl -X POST http://127.0.0.1:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "source_lang": "auto", "target_lang": "fr"}'
```

---

## 🧪 Testing

```bash
python manage.py test
```

This runs unit tests for the translation service (empty input, oversized
input, invalid language) and API tests for `/api/translate/`, `/api/history/`,
and `/api/languages/`.

---

## 🌐 Switching Translation Engines

By default, `TRANSLATION_ENGINE=google` in `.env`, which uses the free
`deep-translator` `GoogleTranslator` — no API key, no billing.

To use LibreTranslate instead (fully open-source, self-hostable):

```env
TRANSLATION_ENGINE=libre
LIBRETRANSLATE_URL=https://libretranslate.com/translate
LIBRETRANSLATE_API_KEY=            # optional, only if your instance requires one
```

You can run your own LibreTranslate server with Docker if you want to avoid
public rate limits:
```bash
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate
```
Then set `LIBRETRANSLATE_URL=http://localhost:5000/translate`.

---

## 🔒 Security & Production Settings

- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` are all read from environment
  variables — never hard-code secrets.
- When `DEBUG=False`, `settings.py` automatically enables:
  `SECURE_SSL_REDIRECT`, secure cookies, HSTS, XSS filtering, and
  clickjacking protection.
- CSRF protection is enabled by default (Django's built-in middleware);
  the frontend reads the `csrftoken` cookie and sends it as `X-CSRFToken`.
- All API input is validated through DRF serializers before touching any
  business logic.
- `deep-translator` calls are wrapped in try/except so network failures,
  timeouts, and invalid languages return clean `400`/`500` JSON errors
  instead of crashing.

---

## 📦 Deployment

### Before deploying (any platform)
```bash
python manage.py collectstatic --noinput
```
This gathers static files into `staticfiles/`, which WhiteNoise then serves.

### Render
1. Push this project to a GitHub repository.
2. In the Render dashboard, click **New → Web Service** and connect your repo.
3. Set:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn translator_project.wsgi`
4. Add environment variables in the Render dashboard: `SECRET_KEY`, `DEBUG=False`,
   `ALLOWED_HOSTS=<your-app>.onrender.com`.
5. Click **Create Web Service**. Render builds and deploys automatically.

### Railway
1. Push to GitHub, then in Railway click **New Project → Deploy from GitHub repo**.
2. Railway auto-detects Python. Add a **Variables** tab entry for `SECRET_KEY`,
   `DEBUG=False`, `ALLOWED_HOSTS=<your-app>.up.railway.app`.
3. Under **Settings → Deploy**, set the start command to
   `gunicorn translator_project.wsgi`.
4. Railway will run `pip install -r requirements.txt` automatically; add a
   **Deploy Hook** or a `release` step (already defined in the `Procfile`) to
   run migrations.

### PythonAnywhere
1. Upload/clone the project into your PythonAnywhere account (Bash console:
   `git clone <your-repo-url>`).
2. Create a virtualenv: `mkvirtualenv --python=python3.12 lingostamp-env`
   then `pip install -r requirements.txt`.
3. In the **Web** tab, create a new web app, choose **Manual configuration**,
   and point the WSGI file to `translator_project.wsgi.application`.
4. Set the working directory and virtualenv path in the Web tab.
5. In the **Files** tab or a Bash console, run
   `python manage.py migrate` and `python manage.py collectstatic --noinput`.
6. Add your `.env` values as actual environment variables in the WSGI
   configuration file (PythonAnywhere doesn't read `.env` automatically —
   `import os; os.environ["SECRET_KEY"] = "..."` before importing Django).
7. Reload the web app.

---

## ✅ Deployment Checklist

- [ ] `DEBUG=False` in production environment variables
- [ ] Strong, unique `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` set to your real domain
- [ ] `python manage.py migrate` run against the production database
- [ ] `python manage.py collectstatic --noinput` run
- [ ] HTTPS enabled (most PaaS providers do this automatically)
- [ ] `.env` file is **not** committed to git (already in `.gitignore`)

---

## 🐛 Common Errors & Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'django'` | Activate your virtualenv and re-run `pip install -r requirements.txt` |
| Translation returns a 500 / network error | The free Google backend can be rate-limited; wait a moment or switch `TRANSLATION_ENGINE=libre` |
| Static files (CSS/JS) missing in production | Run `python manage.py collectstatic --noinput` and confirm WhiteNoise middleware is installed |
| `CSRF verification failed` on POST requests | Make sure cookies are enabled and you're hitting the app from the same host that's in `ALLOWED_HOSTS` |
| gTTS audio doesn't play | Check that `MEDIA_URL`/`MEDIA_ROOT` are being served (in development this is automatic; in production, serve `/media/` via WhiteNoise, S3, or your host's static file config) |

---

## 🔭 Ideas for Version 2

- User accounts so history is personal instead of global
- Favorite/star translations
- File upload translation (.txt, .docx)
- Voice input (speech-to-text)
- Offline-first PWA support
- Batch translation API endpoint

---

## 📄 License

MIT — free to use, modify, and deploy.

## 👤 Author

Built as a complete reference implementation of a Django + DRF translation app.
