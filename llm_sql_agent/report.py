"""Human-readable validation report generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .lineage import diff_lineage
from .retry import MigrationResult


@dataclass
class ValidationReport:
    total: int
    succeeded: int
    failed: int
    lineage_changes: dict[str, list[str]] = field(default_factory=dict)
    failures: dict[str, list[str]] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return self.succeeded / self.total if self.total else 0.0

    def to_markdown(self) -> str:
        lines = [
            "# SQL Migration Validation Report",
            "",
            f"- Queries processed: {self.total}",
            f"- Succeeded: {self.succeeded}",
            f"- Failed: {self.failed}",
            f"- Success rate: {self.success_rate:.1%}",
        ]
        if self.lineage_changes:
            lines += ["", "## Lineage Drift", ""]
            for query_id, columns in self.lineage_changes.items():
                lines.append(f"- `{query_id}`: {', '.join(columns)}")
        if self.failures:
            lines += ["", "## Failures", ""]
            for query_id, errors in self.failures.items():
                lines.append(f"- `{query_id}`: {'; '.join(errors)}")
        return "\n".join(lines)


def build_report(results: list[MigrationResult]) -> ValidationReport:
    """Summarize a batch of :class:`~llm_sql_agent.retry.MigrationResult` into a report."""
    lineage_changes = {}
    failures = {}
    succeeded = 0

    for i, result in enumerate(results):
        query_id = f"query_{i}"
        if result.succeeded:
            succeeded += 1
        else:
            failures[query_id] = result.errors

        if result.lineage_before and result.lineage_after:
            changed = diff_lineage(result.lineage_before, result.lineage_after)
            if changed:
                lineage_changes[query_id] = changed

    return ValidationReport(
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        lineage_changes=lineage_changes,
        failures=failures,
    )
