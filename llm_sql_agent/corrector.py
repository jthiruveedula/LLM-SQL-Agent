"""LLM-driven semantic correction for queries SQLGlot can't transpile outright.

The correction call is provider-agnostic: any OpenAI-compatible chat
completions endpoint works, so this plugs into OpenAI, OpenRouter, or a
local/self-hosted runner (Ollama, LM Studio, OpenCode, vLLM, etc.) via
environment variables alone — no code changes needed to switch providers.

Environment variables:
    LLM_PROVIDER    "openai" (default) or "openrouter". Only picks a default
                    base URL; any provider works via LLM_BASE_URL directly.
    LLM_BASE_URL    Explicit API base URL, overrides the provider default.
                    e.g. "http://localhost:11434/v1" for a local runner.
    LLM_MODEL       Model name/id passed to the API, e.g. "gpt-5.5",
                    "anthropic/claude-fable", "qwen2.5-coder:32b".
    LLM_API_KEY     API key. Falls back to OPENAI_API_KEY or
                    OPENROUTER_API_KEY depending on LLM_PROVIDER.

Without a resolvable API key (e.g. in CI or local dry runs) this falls back
to a small table of known Snowflake -> BigQuery idioms so the pipeline stays
runnable end to end without network access or billing.
"""

from __future__ import annotations

import os
import re

SYSTEM_PROMPT = (
    "You are a SQL migration expert. Rewrite the given {source} query so it "
    "runs correctly on {target}, preserving semantics exactly. Return only "
    "the corrected SQL, no commentary."
)

_PROVIDER_DEFAULTS = {
    "openai": {"base_url": None, "model": "gpt-5.5", "api_key_env": "OPENAI_API_KEY"},
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "anthropic/claude-fable",
        "api_key_env": "OPENROUTER_API_KEY",
    },
}

_FALLBACK_REWRITES: list[tuple[str, str]] = [
    (r"\bIFF\s*\(", "IF("),
    (r"\bTRY_CAST\s*\(", "SAFE_CAST("),
    (r"\bDATEADD\(\s*'?(\w+)'?\s*,\s*(-?\d+)\s*,\s*([^)]+)\)", r"DATE_ADD(\3, INTERVAL \2 \1)"),
    (r"\bOBJECT_CONSTRUCT\s*\(", "STRUCT("),
    (r"\bLISTAGG\s*\(", "STRING_AGG("),
    (r"\bCURRENT_TIMESTAMP\(\)", "CURRENT_TIMESTAMP()"),
]


def _fallback_correct(sql: str) -> str:
    corrected = sql
    for pattern, replacement in _FALLBACK_REWRITES:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
    return corrected


def _resolve_provider_config() -> tuple[str | None, str | None, str]:
    """Resolve (base_url, api_key, model) from env vars, provider defaults first."""
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    defaults = _PROVIDER_DEFAULTS.get(provider, _PROVIDER_DEFAULTS["openai"])

    base_url = os.environ.get("LLM_BASE_URL", defaults["base_url"])
    model = os.environ.get("LLM_MODEL", defaults["model"])
    api_key = (
        os.environ.get("LLM_API_KEY")
        or os.environ.get(defaults["api_key_env"])
        or os.environ.get("OPENAI_API_KEY")
    )
    return base_url, api_key, model


def correct_query(sql: str, error: str, source_dialect: str, target_dialect: str) -> str:
    """Return a semantically corrected version of ``sql`` given a transpile ``error``.

    Talks to whichever OpenAI-compatible provider is configured via
    ``LLM_PROVIDER``/``LLM_BASE_URL``/``LLM_MODEL``/``LLM_API_KEY``. Falls
    back to rule-based rewrites when no API key is resolvable.
    """
    base_url, api_key, model = _resolve_provider_config()
    if not api_key:
        return _fallback_correct(sql)

    from openai import OpenAI  # imported lazily so the package works without the SDK installed

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(source=source_dialect, target=target_dialect),
            },
            {
                "role": "user",
                "content": f"Query:\n{sql}\n\nTranspile error:\n{error}",
            },
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()
