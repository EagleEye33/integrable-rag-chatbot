# Website Chatbot (FastAPI + Gemini + RAG)

This project provides a website-integrated chatbot that answers questions about your organization/website from curated content.

## What is included

- `backend/`: FastAPI API, retrieval index builder, and chat service.
- `widget/`: Drop-in JavaScript/CSS chatbot widget.
- `website/`: Example website page that integrates the widget.

## 1) Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

## 2) Configure environment

1. Copy `.env.example` to `.env`.
2. Set:
   - `GEMINI_API_KEY`: your Gemini API key.
   - `GEMINI_MODEL`: optional, default `gemini-1.5-flash`.
   - `ALLOW_ORIGINS`: comma-separated origins or `*`.

## 3) Add knowledge sources

Edit `backend/data/content_sources.json`. Supported source types:

- `text`: inline content.
- `url`: fetches and parses visible webpage text.

Example entry:

```json
{
  "id": "company-about",
  "type": "url",
  "url": "https://example.org/about"
}
```

## 4) Build retrieval index

```bash
python -m backend.app.ingest
```

This generates `backend/data/index.json`.

## 5) Run backend

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:

- `GET /health`
- `POST /api/chat`

Request body:

```json
{
  "question": "What services do you offer?"
}
```

## 6) Embed chatbot in a website

Add these tags to your page:

```html
<script src="/widget/chatbot.js"></script>
<script>
  window.WebsiteChatbot.init({
    apiBaseUrl: "http://localhost:8000",
    apiPrefix: "/api",
    organizationName: "Acme Organization",
    cssUrl: "/widget/chatbot.css"
  });
</script>
```

Widget config options:

- `apiBaseUrl`: backend base URL.
- `apiPrefix`: route prefix (default `/api`).
- `organizationName`: bot title shown in widget.
- `cssUrl`: stylesheet path for widget UI.

## 7) Run tests

```bash
pytest backend/tests -q
```

## Notes on grounded answers

- The backend always retrieves top matching chunks from the index.
- The model prompt instructs Gemini to answer only from retrieved context.
- If context is insufficient, the API returns a safe fallback response.
