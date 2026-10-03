"""Shared helpers for talking to Gemini and parsing its JSON replies."""
import json
import re
from typing import Any, Callable, List, TypeVar

from app.config import get_settings

T = TypeVar("T")


def get_client():
    """Create a Gemini client (google-genai SDK)."""
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to your .env file.")
    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def extract_json(text: str) -> Any:
    """Parse JSON from a model reply, tolerating ```json fences and stray prose."""
    if not text or not text.strip():
        raise ValueError("Gemini returned an empty response.")
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Fall back to the first {...} or [...] block in the text.
    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = cleaned.find(opener), cleaned.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"Could not parse JSON from Gemini response: {cleaned[:200]!r}")


def panels_from_json(data: Any) -> List[dict]:
    """Accept {"panels": [...]}, a bare list, or a dict holding a list."""
    if isinstance(data, dict):
        if isinstance(data.get("panels"), list):
            data = data["panels"]
        else:
            lists = [v for v in data.values() if isinstance(v, list)]
            if lists:
                data = lists[0]
    if not isinstance(data, list) or not all(isinstance(p, dict) for p in data):
        raise ValueError("Gemini response did not contain a list of panels.")
    return data


def call_with_model_fallback(models: List[str], build_and_parse: Callable[[Any, str], T], attempts_per_model: int = 2) -> T:
    """Run build_and_parse(client, model) for each model until one succeeds."""
    client = get_client()
    errors: List[str] = []
    for model in models:
        for attempt in range(1, attempts_per_model + 1):
            try:
                return build_and_parse(client, model)
            except Exception as exc:  # noqa: BLE001 - we report all errors together
                errors.append(f"{model} (try {attempt}): {exc}")
                message = str(exc).lower()
                # Model missing / retired / quota exhausted -> no point retrying the same model.
                if any(k in message for k in ("not found", "no longer available", "404", "not supported", "permission", "api key", "429", "quota", "resource_exhausted")):
                    break
    raise RuntimeError("Gemini request failed for all configured models:\n" + "\n".join(errors[-6:]))


def generate_text(client, model: str, prompt: str, temperature: float) -> str:
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=temperature),
    )
    text = getattr(response, "text", None)
    if not text:
        raise ValueError("Gemini returned no text (the reply may have been blocked).")
    return text
