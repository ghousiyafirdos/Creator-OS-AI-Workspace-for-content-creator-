CreatorOS — Gemini AI Workspace Speed Build

1. Extract this ZIP.
2. Keep your own local .env file in the project root.
3. Put your Gemini key in .env as GEMINI_API_KEY=your_key_here
4. Optional: GEMINI_MODEL=gemini-3.5-flash-lite
5. Run: python app.py

This build changes only the AI Workspace Gemini provider layer. It uses real Gemini models only.

Speed changes:
- Primary model is Gemini 3.5 Flash-Lite for low-latency content generation.
- Gemini 3.x Flash-Lite requests use minimal thinking for routine creator tasks.
- Maximum retries are capped at 2 for the primary model.
- Only two fast Gemini fallbacks are used, preventing long chains of retries.
- Transient 429/5xx errors still use short exponential backoff.
- There is no fake/local/template AI fallback.

Fallback order: 3.5 Flash-Lite, 3.1 Flash-Lite, 2.5 Flash-Lite.

If Gemini itself is unavailable or the API quota is exhausted, the application reports the real provider error rather than inventing output.


CreatorOS uses Gemini 3.5 Flash-Lite first for low-latency content generation, then Gemini 3.6 Flash and Gemini 3.8 Flash if the first model is temporarily unavailable. The SDK automatic retry loop is disabled so the UI does not wait several minutes on repeated 503 responses.
