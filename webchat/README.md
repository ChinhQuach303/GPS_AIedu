# GPS AIedu Web Chat (Next.js) + Auto Logging

This app provides a single web chat UI and automatically logs each Q/A turn into Google Sheets `Raw Data` via an Apps Script Web App (`doPost`).

## Local dev

1. Copy env:
   - `cp .env.example .env.local`
2. Install + run:
   - `npm install`
   - `npm run dev`

Notes:
- The OpenAI API is separate from the ChatGPT app. You need an API key and active billing/credits for API usage.
- You can view the server's available models at `GET /api/models` (requires `OPENAI_API_KEY`).
- If you want a truly free option, switch to `LLM_PROVIDER=ollama` and run an open-weight math model locally.

## Deploy

- Recommended: create a Vercel project with root directory = `webchat/` and set env vars from `.env.example`.
