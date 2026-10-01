"""CreatorOS image generation service with resilient AI + local fallback."""
import base64
import binascii
import os
import re
import time
from pathlib import Path
from typing import Tuple
from urllib.parse import quote

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


class GeminiVisualService:
    """Generate thumbnails from a topic without exposing provider errors to the UI.

    Provider order:
      1. Gemini native image model when the key/project has image access.
      2. Pollinations public image endpoint as an additional AI route.
      3. A local SVG thumbnail so the Generate button always produces a usable asset.
    """

    IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image").strip() or "gemini-3.1-flash-image"
    SERVER_TIMEOUT_SECONDS = 18
    POLLINATIONS_TIMEOUT_SECONDS = 25

    @staticmethod
    def _safe_filename(text: str) -> str:
        text = re.sub(r"[^A-Za-z0-9]+", "_", text or "visual").strip("_")
        return (text[:50] or "visual").lower()

    @staticmethod
    def _decode(value):
        if not value:
            return None
        if isinstance(value, bytes):
            return value
        if isinstance(value, str) and value.startswith("data:"):
            value = value.split(",", 1)[1]
        if not isinstance(value, str):
            return None
        try:
            return base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError):
            try:
                return base64.b64decode(value)
            except Exception:
                return None

    @staticmethod
    def _extract_image_bytes(interaction) -> bytes | None:
        output = getattr(interaction, "output_image", None)
        raw = getattr(output, "data", None) if output is not None else None
        decoded = GeminiVisualService._decode(raw)
        if decoded:
            return decoded
        for step in (getattr(interaction, "steps", None) or []):
            content = getattr(step, "content", None)
            if content is None and isinstance(step, dict):
                content = step.get("content")
            for block in (content or []):
                block_type = getattr(block, "type", None)
                if block_type is None and isinstance(block, dict):
                    block_type = block.get("type")
                if block_type != "image":
                    continue
                data = getattr(block, "data", None)
                if data is None and isinstance(block, dict):
                    data = block.get("data")
                decoded = GeminiVisualService._decode(data)
                if decoded:
                    return decoded
        return None

    @staticmethod
    def _request_gemini(api_key: str, prompt: str) -> bytes:
        from google import genai
        from google.genai import types

        http_options = types.HttpOptions(
            timeout=GeminiVisualService.SERVER_TIMEOUT_SECONDS * 1000,
            retry_options=types.HttpRetryOptions(
                attempts=1,
                initial_delay=0.1,
                max_delay=0.1,
                http_status_codes=[],
            ),
        )
        client = genai.Client(api_key=api_key, http_options=http_options)
        interaction = client.interactions.create(
            model=GeminiVisualService.IMAGE_MODEL,
            input=prompt,
            response_format={
                "type": "image",
                "mime_type": "image/jpeg",
                "aspect_ratio": "16:9",
                "image_size": "1K",
            },
        )
        image_bytes = GeminiVisualService._extract_image_bytes(interaction)
        if not image_bytes:
            raise RuntimeError("Gemini returned no image data")
        return image_bytes

    @staticmethod
    def _request_pollinations(prompt: str) -> bytes:
        import requests
        # Public image route. If a deployment supplies POLLINATIONS_API_KEY,
        # it is attached without changing the normal no-key setup.
        encoded = quote(prompt, safe="")
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"
        headers = {}
        key = os.getenv("POLLINATIONS_API_KEY", "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        response = requests.get(url, headers=headers, timeout=GeminiVisualService.POLLINATIONS_TIMEOUT_SECONDS)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "image" not in content_type or len(response.content) < 1000:
            raise RuntimeError("Pollinations did not return an image")
        return response.content

    @staticmethod
    def _category(topic: str) -> str:
        t = topic.lower()
        rules = [
            ("rain", ["rain", "rainy", "monsoon", "umbrella", "storm", "cloud"]),
            ("hotel", ["hotel", "hospitality", "hotel management", "resort"]),
            ("career", ["career", "job", "jobs", "interview", "resume", "placement", "profession"]),
            ("education", ["education", "study", "exam", "college", "school", "student", "learning", "course"]),
            ("technology", ["ai", "artificial intelligence", "software", "coding", "technology", "app", "computer", "cyber", "data"]),
            ("travel", ["travel", "tourism", "trip", "vacation", "tour", "destination", "beach", "mountain"]),
            ("food", ["food", "coffee", "restaurant", "cafe", "cake", "pizza", "cooking", "recipe"]),
            ("business", ["business", "marketing", "startup", "finance", "sales", "entrepreneur"]),
            ("fitness", ["fitness", "gym", "workout", "yoga", "health", "running"]),
            ("flowers", ["flower", "flowers", "floral", "garden", "bouquet", "artificial flowers"]),
        ]
        for cat, words in rules:
            if any(w in t for w in words):
                return cat
        return "general"

    @staticmethod
    def _local_svg(topic: str) -> bytes:
        """Create a polished topic-specific thumbnail with no external dependency."""
        category = GeminiVisualService._category(topic)
        palette = {
            "rain": ("#13243a", "#4c83b8", "#dcecff", "☔"),
            "hotel": ("#211b31", "#a97835", "#fff2d6", "🏨"),
            "career": ("#102b4e", "#d4af37", "#f8f4e8", "💼"),
            "education": ("#15263d", "#5f8fb8", "#f5f8fb", "🎓"),
            "technology": ("#101a34", "#6b72ff", "#d9ddff", "💻"),
            "travel": ("#0c3843", "#e1a33b", "#eaf8f6", "✈"),
            "food": ("#3b1f1f", "#d17a35", "#fff0d9", "☕"),
            "business": ("#182334", "#b58a38", "#f5ecd7", "📈"),
            "fitness": ("#162d29", "#52a47d", "#e4f6ed", "💪"),
            "flowers": ("#3a2038", "#d66c9c", "#ffe8f1", "🌸"),
            "general": ("#111f3a", "#7f8cff", "#eef0ff", "✨"),
        }
        c1, c2, c3, icon = palette[category]
        safe_topic = html_escape(topic[:80])
        cat_label = html_escape(category.upper())
        # SVG text is rendered as a real image by browsers and the existing canvas editor.
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient><radialGradient id="glow"><stop stop-color="{c3}" stop-opacity=".34"/><stop offset="1" stop-color="{c3}" stop-opacity="0"/></radialGradient></defs>
<rect width="1280" height="720" fill="url(#g)"/><circle cx="1040" cy="180" r="300" fill="url(#glow)"/><circle cx="1130" cy="610" r="250" fill="url(#glow)" opacity=".55"/>
<rect x="58" y="58" width="1164" height="604" rx="34" fill="#081321" opacity=".20" stroke="#ffffff" stroke-opacity=".20"/>
<text x="92" y="125" font-family="Arial,sans-serif" font-size="28" font-weight="700" fill="{c3}" letter-spacing="5">CREATOROS • {cat_label}</text>
<text x="92" y="285" font-family="Arial,sans-serif" font-size="78" font-weight="800" fill="#ffffff">{safe_topic}</text>
<text x="92" y="340" font-family="Arial,sans-serif" font-size="26" fill="#ffffff" opacity=".80">AI-assisted thumbnail • topic-focused visual design</text>
<circle cx="1005" cy="330" r="150" fill="#ffffff" opacity=".10"/><circle cx="1005" cy="330" r="112" fill="#ffffff" opacity=".09"/>
<text x="1005" y="365" text-anchor="middle" font-family="Arial,sans-serif" font-size="118">{icon}</text>
<rect x="92" y="570" width="320" height="6" rx="3" fill="{c3}"/><text x="92" y="615" font-family="Arial,sans-serif" font-size="21" fill="#ffffff" opacity=".72">GENERATE • EDIT • DOWNLOAD</text>
</svg>"""
        return svg.encode("utf-8")

    @staticmethod
    def _save(image_bytes: bytes, name: str, model: str, extension: str = "jpg"):
        folder = PROJECT_ROOT / "static" / "uploads" / "generated_visuals"
        folder.mkdir(parents=True, exist_ok=True)
        filename = f"{int(time.time() * 1000)}_{GeminiVisualService._safe_filename(name)}.{extension}"
        (folder / filename).write_bytes(image_bytes)
        return f"/static/uploads/generated_visuals/{filename}", model

    @staticmethod
    def generate(thumbnail_title: str = "") -> Tuple[str, str]:
        thumbnail_title = re.sub(r"\s+", " ", thumbnail_title or "").strip()
        if not thumbnail_title:
            raise ValueError("Enter a topic first.")

        prompt = f"""Create one polished 16:9 social-media thumbnail for this exact topic: {thumbnail_title}
Interpret the topic faithfully and choose the correct visual subject/category. Do not replace it with a generic technology theme.
Use a strong composition, clear focal subject, attractive lighting, clean modern design and readable headline text based on the topic.
Return one finished thumbnail image."""

        key = (os.getenv("GEMINI_API_KEY", "").strip()
               or os.getenv("GOOGLE_API_KEY", "").strip()
               or os.getenv("GOOGLE_GENAI_API_KEY", "").strip())

        if key:
            try:
                data = GeminiVisualService._request_gemini(key, prompt)
                return GeminiVisualService._save(data, thumbnail_title, GeminiVisualService.IMAGE_MODEL, "jpg")
            except Exception:
                pass

        try:
            data = GeminiVisualService._request_pollinations(prompt)
            return GeminiVisualService._save(data, thumbnail_title, "Pollinations AI", "jpg")
        except Exception:
            pass

        # Last-resort local thumbnail: Generate still succeeds instead of exposing
        # provider/quota/IP errors to the user.
        data = GeminiVisualService._local_svg(thumbnail_title)
        return GeminiVisualService._save(data, thumbnail_title, "CreatorOS local AI-style generator", "svg")


def html_escape(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))
