from llm_sql_agent.lineage import diff_lineage, extract_lineage


def test_extract_lineage_returns_one_report_per_output_column():
    sql = "SELECT a.id AS user_id, a.name FROM tbl a"
    reports = extract_lineage(sql, "snowflake")
    columns = {r.column.lower() for r in reports}
    assert columns == {"user_id", "name"}


def test_diff_lineage_detects_changed_sources():
    before = extract_lineage("SELECT a.id AS user_id FROM tbl_a a", "snowflake")
    after = extract_lineage("SELECT b.id AS user_id FROM tbl_b b", "snowflake")
    changed = {c.lower() for c in diff_lineage(before, after)}
    assert "user_id" in changed


def test_diff_lineage_no_change():
    reports = extract_lineage("SELECT a.id AS user_id FROM tbl_a a", "snowflake")
    assert diff_lineage(reports, reports) == []
