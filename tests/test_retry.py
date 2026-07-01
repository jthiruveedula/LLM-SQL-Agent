import os

from llm_sql_agent.retry import migrate_with_retry


def test_migrate_clean_query_succeeds_first_attempt(monkeypatch):
    monkeypatch.delenv("GCP_PROJECT", raising=False)
    result = migrate_with_retry("SELECT id, name FROM customers", "snowflake", "bigquery")
    assert result.succeeded
    assert result.attempts == 1
    assert result.final_sql


def test_migrate_self_heals_snowflake_idiom(monkeypatch):
    monkeypatch.delenv("GCP_PROJECT", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = migrate_with_retry("SELECT IFF(x > 0, 1, 0) AS flag FROM t", "snowflake", "bigquery")
    assert result.final_sql is not None
