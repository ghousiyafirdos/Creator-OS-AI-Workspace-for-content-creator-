CreatorOS Images & Thumbnails — fast Gemini image generation

Images & Thumbnails now uses Gemini only:
GEMINI_IMAGE_MODEL=gemini-3.1-flash-lite-image

Performance configuration:
- 1K output
- 16:9 aspect ratio
- exactly one Gemini image-generation request
- no OpenAI fallback
- no model failover
- no application-level retries
- server request timeout: 55 seconds
- browser request timeout: 60 seconds

AI Workspace settings are not changed.
The user still needs to place their Gemini API key in .env:
GEMINI_API_KEY=your_key_here
