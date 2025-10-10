# Land ReGen — AI for Land Degradation

Full-stack starter: Django backend with Firebase Admin + simple SPA frontend.

## Project Structure

- `backend/`: Django project `landdeg_backend` and app `api`
- `frontend/`: Static SPA (`index.html`, `app.js`) using Firebase Auth

## Prerequisites

- Python 3.11+
- Node optional (frontend is plain HTML/JS)
- Firebase project + Service Account JSON

## Setup (Backend)

```bash
cd "land degradation/backend"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env to point FIREBASE_CREDENTIALS_FILE to your service account JSON

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Health check: `GET http://127.0.0.1:8000/api/health`

## Setup (Frontend)

Open `frontend/index.html` with a static server, or via VS Code Live Server. Update `frontend/app.js` with your Firebase Client config, and set `getBackendBase()` to your backend URL (e.g., `http://127.0.0.1:8000`).

## Firebase

- Create a Firebase project
- Generate Service Account (Firebase Admin SDK) and download JSON
- Put path in `.env` as `FIREBASE_CREDENTIALS_FILE`
- Enable Google Sign-In under Authentication for the web client

## Endpoints

- `POST /api/analyze` — Requires Firebase Bearer token, body with `location`, `observations`, optional `goals`, `data`. Saves to Firestore and returns a plan.
- `GET /api/agromet` — Requires Firebase Bearer token, returns mock agro-met data.
- `GET /api/projects` — Requires Firebase Bearer token, lists your analyses from Firestore.
- `GET /api/health` — No auth. Health check.

## Deployment

- Render.com / Railway: Add environment variables from `.env`, build with `pip install -r requirements.txt`, run `gunicorn landdeg_backend.wsgi`.
- Static frontend can be hosted on Netlify/Vercel/GitHub Pages. Point it to your backend URL.

## Notes

- Replace rules-based `generate_action_plan` with an LLM call (OpenAI/Claude) or your model.
- For production, restrict CORS and CSRF origins and set `DEBUG=0`.
