from llm_sql_agent.report import build_report
from llm_sql_agent.retry import MigrationResult


def test_build_report_counts_success_and_failure():
    results = [
        MigrationResult(original_sql="a", final_sql="a", attempts=1, succeeded=True),
        MigrationResult(original_sql="b", final_sql=None, attempts=3, succeeded=False, errors=["boom"]),
    ]
    report = build_report(results)
    assert report.total == 2
    assert report.succeeded == 1
    assert report.failed == 1
    assert report.success_rate == 0.5
    assert "query_1" in report.failures


def test_report_to_markdown_contains_summary():
    report = build_report([MigrationResult(original_sql="a", final_sql="a", attempts=1, succeeded=True)])
    md = report.to_markdown()
    assert "Success rate: 100.0%" in md
