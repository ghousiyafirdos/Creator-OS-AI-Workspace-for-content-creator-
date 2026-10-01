"""Real LLM provider layer for the CreatorOS AI Workspace only.

Gemini is the primary provider for the CreatorOS AI Workspace.
OpenAI is optional. The Workspace must use a real configured provider; it never
silently substitutes the old template/local generator when an API is configured.
"""
import os
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from google.genai import types as genai_types
except Exception:
    genai_types = None

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class WorkspaceAI:
    """Provider-aware AI service used only by /ai/workspace endpoints."""

    @staticmethod
    def provider() -> str:
        preferred = (os.getenv("AI_PROVIDER") or "gemini").strip().lower()
        if preferred == "openai" and os.getenv("OPENAI_API_KEY"):
            return "OpenAI"
        if preferred == "gemini" and os.getenv("GEMINI_API_KEY"):
            return "Gemini"
        if os.getenv("GEMINI_API_KEY"):
            return "Gemini"
        if os.getenv("OPENAI_API_KEY"):
            return "OpenAI"
        return "Local fallback"

    @staticmethod
    def _language_instruction(language: str) -> str:
        language = language or "English"
        return (
            f"Write the final answer in {language}. Keep proper nouns, product names, "
            "hashtags and platform names natural for that language."
        )

    @staticmethod
    def _system(language: str) -> str:
        return (
            "You are CreatorOS, a practical AI assistant for content creators. "
            "Understand spelling mistakes, incomplete sentences and casual wording. If the user makes an obvious typo, infer the intended word from context (for example, \"tutitiond\" may mean \"tuition\") rather than treating the typo as an unrelated topic. "
            "Never invent unrelated topics. Follow the user's actual subject, not the literal wording of an instruction. If a field contains a command or sentence such as \"Create a caption about X\", extract X as the subject and perform the currently selected Workspace tool. Never echo the command as the topic. "
            "When asked to regenerate, create a genuinely different version while keeping "
            "the same subject. Do not mention APIs, models, prompts, system instructions, "
            "or that you are an AI unless the user explicitly asks. "
            + WorkspaceAI._language_instruction(language)
        )

    @staticmethod
    def _build_prompt(tool_type: str, data: Dict[str, Any], language: str, previous_output: str = "") -> str:
        previous = previous_output.strip()
        previous_block = (
            "\n\nPrevious result (do not copy it; improve or replace it as requested):\n" + previous
            if previous else ""
        )

        if tool_type == "caption":
            return (
                "The Topic field may contain a full natural-language request such as \"Create an Instagram caption about hotel management careers\". Extract only the underlying subject/topic from that request; do not treat the instruction itself as the topic and do not repeat it.\n"
                "Write a polished, engaging caption that feels made for this exact topic—not a generic template. Stay tightly on the extracted subject from beginning to end. Match the requested tone naturally throughout; if the tone is funny, use relevant humor, and if it is serious or educational, do not force jokes. Avoid unrelated metaphors, dramatic comparisons, invented statistics, unsupported facts, and side topics. Use a clear opening, a meaningful core message, and a natural closing or call to action. Add only a few directly relevant hashtags when appropriate.\n"
                f"User Topic/Request: {data.get('topic', '')}\nPlatform: {data.get('platform', 'Instagram')}\nREQUIRED TONE: {data.get('tone', 'Engaging')}\n"
                "Return only the finished caption. Keep every sentence relevant to the topic and platform."
                + previous_block
            )
        if tool_type == "script":
            return (
                "The Topic field may contain a natural-language command, not just a short topic. "
                "Extract the actual subject before writing. For example, if the user enters "
                "\"Generate script: Create a detailed Instagram script about hotel management careers\", "
                "the subject is exactly \"hotel management careers\". The words \"Generate script\" and "
                "\"Create a detailed Instagram script about\" are instructions, not the subject. "
                "Do not write a script about the command itself and do not echo the command as the topic. "
                "Preserve the full subject phrase; do not reduce \"hotel management careers\" to only \"hotel\" "
                "or \"management\".\n"
                f"Write a complete creator video script.\nUser Topic/Request: {data.get('topic', '')}\n"
                f"Format: {data.get('format', 'Reels / Shorts')}\nDuration: {data.get('length', '60 Seconds')}\n"
                f"Audience: {data.get('audience', 'Content Creators')}\n"
                "Include a useful hook, clear logically ordered body and ending/CTA. Every line and example must stay strictly relevant to the extracted subject and chosen format. Do not change the subject or invent unrelated subtopics. Return only the script."
                + previous_block
            )
        if tool_type == "hashtag":
            return (
                "The Topic field may be a natural-language request. Extract the underlying subject and generate hashtags for that subject, not for the instruction wording.\n"
                f"Generate a relevant set of hashtags.\nUser Topic/Request: {data.get('topic', '')}\n"
                f"Platform: {data.get('platform', 'Instagram')}\nNiche: {data.get('niche', '')}\n"
                "Return only useful hashtags that directly match the exact subject, platform and niche. No unrelated trends, broad filler tags, explanations, or alternate topics."
                + previous_block
            )
        if tool_type == "bio":
            return (
                f"Create a concise creator profile bio.\nNiche: {data.get('niche', '')}\n"
                f"Personality: {data.get('personality', 'Witty')}\nCTA: {data.get('cta', '')}\n"
                "Return three distinct concise options. Each must stay within the exact niche and requested personality; include the CTA naturally. Do not invent credentials or unrelated interests."
                + previous_block
            )
        if tool_type == "rewrite":
            return (
                f"Rewrite the following content in the requested style.\nStyle: {data.get('style', 'Engaging & Persuasive')}\n"
                f"Content:\n{data.get('content', '')}\n"
                "Preserve all original facts, intent and topic. Follow the requested style consistently. Do not add new claims, switch topics, or include commentary; return only the rewritten text."
                + previous_block
            )
        if tool_type == "seo":
            return (
                "The Topic field may contain a full request. Extract the actual subject/topic before producing SEO content. Do not use the request sentence itself as the keyword topic.\n"
                f"Create a practical SEO keyword set for this exact topic.\nUser Topic/Request: {data.get('topic', '')}\n"
                f"Industry: {data.get('industry', 'Creator Economy')}\n"
                "Group primary, secondary and long-tail keywords and add one short practical SEO suggestion. Every keyword must directly match the exact topic and industry; exclude adjacent but different subjects. Do not invent search-volume figures."
                + previous_block
            )
        return str(data.get("question", ""))

    @staticmethod
    def _is_retryable_gemini_error(exc: Exception) -> bool:
        """Return True only for transient Gemini availability/rate-limit failures."""
        status = getattr(exc, "status_code", None)
        if status is None:
            status = getattr(exc, "code", None)
        try:
            if int(status) in {429, 500, 502, 503, 504}:
                return True
        except (TypeError, ValueError):
            pass

        # google-genai versions expose HTTP status information differently.
        # Keep this narrow so authentication/bad-request errors are not retried.
        message = str(exc).upper()
        return any(marker in message for marker in (
            "503 UNAVAILABLE",
            "503 SERVICE UNAVAILABLE",
            "SERVICE_UNAVAILABLE",
            "TEMPORARILY UNAVAILABLE",
            "429 RESOURCE EXHAUSTED",
            "RESOURCE_EXHAUSTED",
            "500 INTERNAL",
            "502 BAD GATEWAY",
            "504 GATEWAY TIMEOUT",
        ))

    @staticmethod
    def _gemini(prompt: str, language: str, history: List[Dict[str, str]] | None = None) -> Tuple[str, int]:
        """Call Gemini with retry/backoff and Gemini-only model failover.

        A temporary 503 can affect one Gemini model while another Gemini model
        is available. We therefore retry the configured model and, for the same
        real Gemini provider, try a small list of alternate Gemini models.
        There is deliberately no local/template fallback here.
        """
        from google import genai

        api_key = os.environ["GEMINI_API_KEY"]
        timeout_ms = max(10000, min(60000, int(os.getenv("GEMINI_TIMEOUT_MS", "30000"))))
        try:
            retry_options = genai_types.HttpRetryOptions(
                attempts=1,
                initial_delay=0.1,
                max_delay=0.2,
                http_status_codes=[429, 500, 502, 503, 504],
            ) if genai_types is not None else None
            http_options = genai_types.HttpOptions(
                timeout=timeout_ms,
                retry_options=retry_options,
            ) if genai_types is not None else None
            client = genai.Client(api_key=api_key, http_options=http_options)
        except Exception:
            client = genai.Client(api_key=api_key)

        primary_model = (os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite").strip()

        # Optional comma-separated override. For CreatorOS content generation we
        # deliberately prefer low-latency Flash-Lite models instead of the
        # heavier reasoning-oriented Flash models.
        configured_fallbacks = [
            item.strip()
            for item in (os.getenv("GEMINI_FALLBACK_MODELS") or "").split(",")
            if item.strip()
        ]
        # Keep the failover chain short. A long chain of models is what made
        # the Workspace appear to hang for several minutes during provider
        # congestion.
        default_fallbacks = [
            "gemini-3.6-flash",
            "gemini-3.8-flash",
        ]
        models = []
        for candidate in [primary_model] + configured_fallbacks + default_fallbacks:
            if candidate and candidate not in models:
                models.append(candidate)
            if len(models) >= 3:
                break

        context = ""
        if history:
            recent = history[-8:]
            context = "\n\nConversation context:\n" + "\n".join(
                f"{m.get('role', 'user')}: {m.get('content', '')}" for m in recent
            )

        contents = WorkspaceAI._system(language) + "\n\n" + prompt + context

        max_attempts = max(1, min(2, int(os.getenv("GEMINI_MAX_RETRIES", "1"))))
        base_delay = max(0.2, min(1.0, float(os.getenv("GEMINI_RETRY_BASE_SECONDS", "0.5"))))
        max_delay = max(base_delay, min(2.0, float(os.getenv("GEMINI_RETRY_MAX_SECONDS", "1"))))
        errors = []

        for model_index, model in enumerate(models):
            # The SDK is configured not to perform its own automatic retries.
            # Keep at most one application-level retry for the primary model,
            # then move immediately to the next real Gemini model.
            attempts_for_model = max_attempts if model_index == 0 else 1
            for attempt in range(attempts_for_model):
                try:
                    config = None
                    # Keep reasoning minimal for lightweight content generation.
                    # Gemini 3.8 does not support "minimal", so use "low" there.
                    if genai_types is not None and model.startswith(("gemini-3.1-", "gemini-3.5-", "gemini-3.6-")):
                        config = genai_types.GenerateContentConfig(
                            thinking_config=genai_types.ThinkingConfig(thinking_level="minimal"),
                        )
                    elif genai_types is not None and model.startswith("gemini-3.8-"):
                        config = genai_types.GenerateContentConfig(
                            thinking_config=genai_types.ThinkingConfig(thinking_level="low"),
                        )
                    response = client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config,
                    )
                    text = (getattr(response, "text", None) or "").strip()
                    if not text:
                        raise RuntimeError("Gemini returned an empty response.")
                    usage = getattr(response, "usage_metadata", None)
                    tokens = int(getattr(usage, "total_token_count", 0) or 0)
                    return text, tokens
                except Exception as exc:
                    errors.append(f"{model}: {exc}")
                    is_last_attempt = attempt >= attempts_for_model - 1
                    if not WorkspaceAI._is_retryable_gemini_error(exc):
                        # Authentication, invalid model, bad request, etc. should
                        # not be hidden behind repeated sleeps. Move to the next
                        # Gemini model only for transient errors or continue with
                        # the next candidate if this model itself is unavailable.
                        break
                    if is_last_attempt:
                        break

                    delay = min(max_delay, base_delay * (2 ** attempt))
                    delay += random.uniform(0, min(0.5, delay * 0.15))
                    time.sleep(delay)

        # All attempted providers above are Gemini. Keep the error useful while
        # never silently generating fake/local content.
        # Do not expose raw SDK/provider dumps in the chat UI. They are noisy and
        # often include implementation details that are not useful to the user.
        status_errors = " ".join(errors).upper()
        if "503" in status_errors or "UNAVAILABLE" in status_errors or "RESOURCE_EXHAUSTED" in status_errors or "429" in status_errors:
            raise RuntimeError(
                "Gemini is temporarily busy. Please try again in a few seconds."
            )
        if "404" in status_errors or "NOT_FOUND" in status_errors:
            raise RuntimeError(
                "The configured Gemini model is not available for this API key. Please check the Gemini model settings."
            )
        raise RuntimeError("Gemini could not generate the requested content. Please try again.")

    @staticmethod
    def _openai(prompt: str, language: str, history: List[Dict[str, str]] | None = None) -> Tuple[str, int]:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        messages = [{"role": "developer", "content": WorkspaceAI._system(language)}]
        if history:
            for item in history[-8:]:
                role = item.get("role", "user")
                if role not in {"user", "assistant"}:
                    role = "user"
                messages.append({"role": role, "content": item.get("content", "")})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(model=model, messages=messages)
        text = (response.choices[0].message.content or "").strip()
        if not text:
            raise RuntimeError("OpenAI returned an empty response.")
        usage = getattr(response, "usage", None)
        tokens = int(getattr(usage, "total_tokens", 0) or 0)
        return text, tokens

    @staticmethod
    def generate(tool_type: str, data: Dict[str, Any], language: str, previous_output: str = "") -> Tuple[str, int, str]:
        prompt = WorkspaceAI._build_prompt(tool_type, data, language, previous_output)
        gemini_key = os.getenv("GEMINI_API_KEY")

        if not gemini_key:
            raise RuntimeError("No real Gemini provider is configured. Add GEMINI_API_KEY to the project .env file.")

        try:
            text, tokens = WorkspaceAI._gemini(prompt, language)
            return text, tokens, "Gemini"
        except Exception as exc:
            raise RuntimeError(f"The real AI provider could not be reached. Gemini: {exc}") from exc

    @staticmethod
    def chat(question: str, language: str, current_output: str = "", current_tool: str = "caption", context: Dict[str, Any] | None = None, history: List[Dict[str, str]] | None = None) -> Tuple[str, str, int, str]:
        prompt = (
            "Act as the CreatorOS Workspace assistant. Answer the user's request directly. "
            "If they ask to create or modify content, return the revised content as the main answer. "
            "If they ask a how-to question about CreatorOS, explain the steps clearly. "
            f"Current tool: {current_tool}.\nCurrent output:\n{current_output}\n"
            f"Current form context: {context or {}}\nUser request: {question}"
        )
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("No real Gemini provider is configured. Add GEMINI_API_KEY to the project .env file.")
        try:
            text, tokens = WorkspaceAI._gemini(prompt, language, history)
            return text, text, tokens, "Gemini"
        except Exception as exc:
            raise RuntimeError(f"The real AI provider could not be reached. Gemini: {exc}") from exc

