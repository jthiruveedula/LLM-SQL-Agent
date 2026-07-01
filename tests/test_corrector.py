from llm_sql_agent.corrector import _resolve_provider_config, correct_query

ALL_LLM_ENV_VARS = ["OPENAI_API_KEY", "OPENROUTER_API_KEY", "LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL", "LLM_PROVIDER"]


def _clear_llm_env(monkeypatch):
    for var in ALL_LLM_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_fallback_correction_without_api_key(monkeypatch):
    _clear_llm_env(monkeypatch)
    sql = "SELECT IFF(x > 0, 1, 0) AS flag FROM t"
    corrected = correct_query(sql, error="unsupported IFF", source_dialect="snowflake", target_dialect="bigquery")
    assert "IF(" in corrected
    assert "IFF(" not in corrected


def test_fallback_rewrites_dateadd(monkeypatch):
    _clear_llm_env(monkeypatch)
    sql = "SELECT DATEADD('day', -7, created_at) FROM t"
    corrected = correct_query(sql, error="unsupported DATEADD", source_dialect="snowflake", target_dialect="bigquery")
    assert "DATE_ADD(" in corrected


def test_resolve_defaults_to_openai(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    base_url, api_key, model = _resolve_provider_config()
    assert base_url is None
    assert api_key == "sk-test"
    assert model == "gpt-5.5"


def test_resolve_openrouter_provider(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-test")
    base_url, api_key, model = _resolve_provider_config()
    assert base_url == "https://openrouter.ai/api/v1"
    assert api_key == "or-test"
    assert model == "anthropic/claude-fable"


def test_resolve_custom_base_url_and_model_overrides_provider(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen2.5-coder:32b")
    monkeypatch.setenv("LLM_API_KEY", "local-key")
    base_url, api_key, model = _resolve_provider_config()
    assert base_url == "http://localhost:11434/v1"
    assert api_key == "local-key"
    assert model == "qwen2.5-coder:32b"
