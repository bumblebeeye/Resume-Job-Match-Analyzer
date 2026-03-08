import json
import re
import urllib.error
import urllib.request
from typing import Any


class AISuggestionError(RuntimeError):
    pass


def generate_gemini_suggestions(
    *,
    missing_skills: list[str],
    role_title: str,
    company_name: str | None,
    api_key: str,
    model: str,
    timeout_seconds: float,
) -> list[str]:
    if not missing_skills:
        return []

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": _build_prompt(
                            missing_skills=missing_skills,
                            role_title=role_title,
                            company_name=company_name,
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }

    response = _call_gemini_api(
        api_key=api_key,
        model=model,
        payload=payload,
        timeout_seconds=timeout_seconds,
    )
    text_content = _extract_text_content(response)
    if not text_content:
        raise AISuggestionError("Gemini returned an empty response.")

    suggestions = _parse_suggestions(text_content)
    if not suggestions:
        raise AISuggestionError("Gemini response did not include valid suggestions.")

    return suggestions


def _build_prompt(
    *,
    missing_skills: list[str],
    role_title: str,
    company_name: str | None,
) -> str:
    company_segment = f" at {company_name}" if company_name else ""
    missing_text = ", ".join(missing_skills)

    return (
        "You are a resume coach. Return output as JSON only.\\n"
        f"Role: {role_title}{company_segment}.\\n"
        f"Missing skills: {missing_text}.\\n\\n"
        "Task:\\n"
        "Write 3 to 5 concise, actionable resume improvement suggestions.\\n"
        "Suggestions should help the candidate show evidence for missing skills.\\n"
        "Keep each suggestion under 20 words.\\n"
        "Do not include markdown or explanations.\\n\\n"
        "Output schema exactly:\\n"
        '{"suggestions":["...","..."]}'
    )


def _call_gemini_api(
    *,
    api_key: str,
    model: str,
    payload: dict[str, Any],
    timeout_seconds: float,
) -> dict[str, Any]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise AISuggestionError(
            f"Gemini API request failed with status {exc.code}. {error_body[:300]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise AISuggestionError(f"Gemini API connection error: {exc.reason}") from exc

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise AISuggestionError("Gemini API returned invalid JSON.") from exc


def _extract_text_content(response: dict[str, Any]) -> str:
    candidates = response.get("candidates")
    if not isinstance(candidates, list):
        return ""

    text_chunks: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content")
        if not isinstance(content, dict):
            continue
        parts = content.get("parts")
        if not isinstance(parts, list):
            continue

        for part in parts:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                text_chunks.append(text.strip())

    return "\n".join(text_chunks).strip()


def _parse_suggestions(text_content: str) -> list[str]:
    try:
        parsed = json.loads(text_content)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        suggestions = parsed.get("suggestions")
        if isinstance(suggestions, list):
            cleaned = _clean_suggestions(suggestions)
            if cleaned:
                return cleaned

    fallback_lines = _extract_bullet_lines(text_content)
    return _clean_suggestions(fallback_lines)


def _extract_bullet_lines(text_content: str) -> list[str]:
    lines = text_content.splitlines()
    extracted: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        stripped = re.sub(r"^\d+[.)]\s+", "", stripped)
        if stripped:
            extracted.append(stripped)
    return extracted


def _clean_suggestions(raw_suggestions: list[Any]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()

    for suggestion in raw_suggestions:
        if not isinstance(suggestion, str):
            continue
        normalized = re.sub(r"\s+", " ", suggestion).strip().strip('"')
        if not normalized:
            continue

        dedupe_key = normalized.lower()
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        deduped.append(normalized)

    return deduped[:5]
