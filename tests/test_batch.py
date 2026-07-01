from llm_sql_agent.batch import migrate_batch_sync


def test_migrate_batch_runs_concurrently(monkeypatch):
    monkeypatch.delenv("GCP_PROJECT", raising=False)
    queries = ["SELECT id FROM t1", "SELECT id FROM t2", "SELECT id FROM t3"]
    results = migrate_batch_sync(queries, "snowflake", "bigquery", concurrency=2)
    assert len(results) == 3
    assert all(r.succeeded for r in results)
