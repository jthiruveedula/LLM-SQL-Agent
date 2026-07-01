"""LLM-driven semantic correction for queries SQLGlot can't transpile outright.

Calls OpenAI's GPT-5.5 when ``OPENAI_API_KEY`` is set. Without a key (e.g. in
CI or local dry runs) it falls back to a small table of known Snowflake ->
BigQuery idioms so the pipeline stays runnable end to end without network
access or billing.
"""

from __future__ import annotations

import os
import re

SYSTEM_PROMPT = (
    "You are a SQL migration expert. Rewrite the given {source} query so it "
    "runs correctly on {target}, preserving semantics exactly. Return only "
    "the corrected SQL, no commentary."
)

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


def correct_query(sql: str, error: str, source_dialect: str, target_dialect: str) -> str:
    """Return a semantically corrected version of ``sql`` given a transpile ``error``."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _fallback_correct(sql)

    from openai import OpenAI  # imported lazily so the package works without the SDK installed

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-5.5",
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
