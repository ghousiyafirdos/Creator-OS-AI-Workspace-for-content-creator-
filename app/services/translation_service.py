"""Lightweight, no-key translation helper used by CreatorOS UI and AI output.

CreatorOS itself does not require a paid AI provider for its generators. For languages
that are not already covered by the built-in UI dictionary, this helper uses Google's
public translation endpoint when the running machine has internet access. Results are
cached in-process so repeated labels do not repeatedly hit the service.
"""
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import re

LANGUAGE_CODES = {
    'English': 'en', 'Hindi': 'hi', 'Bengali': 'bn', 'Marathi': 'mr',
    'Telugu': 'te', 'Tamil': 'ta', 'Kannada': 'kn', 'Malayalam': 'ml',
    'Gujarati': 'gu', 'Punjabi': 'pa', 'Urdu': 'ur', 'Odia': 'or',
    'Assamese': 'as', 'Spanish': 'es', 'French': 'fr', 'German': 'de',
    'Dutch': 'nl', 'Portuguese': 'pt', 'Italian': 'it', 'Chinese': 'zh-CN',
    'Japanese': 'ja', 'Korean': 'ko', 'Arabic': 'ar', 'Russian': 'ru',
}


def _clean_text(text):
    return re.sub(r'\s+', ' ', str(text or '').strip())


@lru_cache(maxsize=1000)
def _translate_cached(text, language):
    text = str(text or '')
    if not text.strip() or language == 'English':
        return text
    target = LANGUAGE_CODES.get(language)
    if not target:
        return text

    # Google Translate's public endpoint accepts no API key. It is intentionally used
    # only as a best-effort fallback; built-in translations remain available offline.
    try:
        query = urlencode({
            'client': 'gtx', 'sl': 'auto', 'tl': target, 'dt': 't', 'q': text[:4800]
        })
        req = Request(
            f'https://translate.googleapis.com/translate_a/single?{query}',
            headers={'User-Agent': 'CreatorOS/1.0'}
        )
        with urlopen(req, timeout=4) as response:
            payload = json.loads(response.read().decode('utf-8'))
        parts = payload[0] if isinstance(payload, list) and payload else []
        translated = ''.join(str(part[0]) for part in parts if isinstance(part, list) and part)
        return translated or text
    except Exception:
        return text


def translate_text(text, language):
    """Translate a complete string while preserving obvious markdown separators."""
    if language == 'English' or not str(text or '').strip():
        return text
    value = str(text)
    if len(value) <= 4800:
        return _translate_cached(value, language)

    # Keep very large generated responses below the public endpoint's query limit.
    chunks = re.split(r'(\n\n+)', value)
    out = []
    buffer = ''
    for chunk in chunks:
        if len(buffer) + len(chunk) > 4300 and buffer:
            out.append(_translate_cached(buffer, language))
            buffer = ''
        buffer += chunk
    if buffer:
        out.append(_translate_cached(buffer, language))
    return ''.join(out)


def translate_many(texts, language):
    """Translate short UI strings, returning a map keyed by the original string."""
    unique = []
    seen = set()
    for text in texts or []:
        text = str(text or '').strip()
        if text and text not in seen and len(text) <= 180:
            seen.add(text)
            unique.append(text)
    return {text: translate_text(text, language) for text in unique}
