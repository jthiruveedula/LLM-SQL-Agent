import os

from llm_sql_agent.corrector import correct_query


def test_fallback_correction_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    sql = "SELECT IFF(x > 0, 1, 0) AS flag FROM t"
    corrected = correct_query(sql, error="unsupported IFF", source_dialect="snowflake", target_dialect="bigquery")
    assert "IF(" in corrected
    assert "IFF(" not in corrected


def test_fallback_rewrites_dateadd():
    sql = "SELECT DATEADD('day', -7, created_at) FROM t"
    corrected = correct_query(sql, error="unsupported DATEADD", source_dialect="snowflake", target_dialect="bigquery")
    assert "DATE_ADD(" in corrected
