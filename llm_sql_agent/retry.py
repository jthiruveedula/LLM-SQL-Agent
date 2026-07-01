"""Self-healing retry loop: parse -> (correct -> reparse)* -> dry run."""

from __future__ import annotations

from dataclasses import dataclass, field

from .corrector import correct_query
from .executor import DryRunResult, dry_run
from .lineage import LineageReport, extract_lineage
from .parser import ParsedQuery, parse_and_validate

DEFAULT_MAX_ATTEMPTS = 3


@dataclass
class MigrationResult:
    original_sql: str
    final_sql: str | None
    attempts: int
    succeeded: bool
    lineage_before: list[LineageReport] = field(default_factory=list)
    lineage_after: list[LineageReport] = field(default_factory=list)
    dry_run_result: DryRunResult | None = None
    errors: list[str] = field(default_factory=list)


def migrate_with_retry(
    sql: str,
    source_dialect: str,
    target_dialect: str,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    validate_dry_run: bool = True,
) -> MigrationResult:
    """Migrate ``sql`` from ``source_dialect`` to ``target_dialect``, self-healing on errors."""
    current_sql = sql
    parsed: ParsedQuery | None = None

    for attempt in range(1, max_attempts + 1):
        parsed = parse_and_validate(current_sql, source_dialect, target_dialect)
        if parsed.is_valid:
            break
        error = parsed.syntax_errors[-1]
        current_sql = correct_query(current_sql, error, source_dialect, target_dialect)
    else:
        return MigrationResult(
            original_sql=sql,
            final_sql=None,
            attempts=max_attempts,
            succeeded=False,
            errors=parsed.syntax_errors if parsed else ["parsing never ran"],
        )

    lineage_before = extract_lineage(sql, source_dialect)
    lineage_after = extract_lineage(parsed.transpiled_sql, target_dialect)

    dry_run_result = None
    if validate_dry_run:
        dry_run_result = dry_run(parsed.transpiled_sql)

    return MigrationResult(
        original_sql=sql,
        final_sql=parsed.transpiled_sql,
        attempts=attempt,
        succeeded=dry_run_result.ok if dry_run_result else True,
        lineage_before=lineage_before,
        lineage_after=lineage_after,
        dry_run_result=dry_run_result,
        errors=dry_run_result.errors if dry_run_result and not dry_run_result.ok else [],
    )
