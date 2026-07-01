"""Column-level lineage extraction and cross-dialect lineage comparison."""

from __future__ import annotations

from dataclasses import dataclass, field

import sqlglot
from sqlglot.lineage import lineage as sqlglot_lineage
from sqlglot.optimizer.qualify import qualify


@dataclass
class LineageReport:
    column: str
    source_columns: list[str] = field(default_factory=list)


def extract_lineage(sql: str, dialect: str, schema: dict | None = None) -> list[LineageReport]:
    """Trace each output column of ``sql`` back to its upstream source columns.

    ``schema`` is the optional table/column schema SQLGlot needs to resolve
    ``SELECT *`` and ambiguous column references; without it lineage is best
    effort and limited to columns that are unambiguous from the query text
    alone.
    """
    tree = sqlglot.parse_one(sql, read=dialect)
    try:
        qualified = qualify(tree, schema=schema, dialect=dialect)
    except Exception:
        qualified = tree

    output_columns = [c.alias_or_name for c in qualified.selects]
    reports = []
    for column in output_columns:
        try:
            node = sqlglot_lineage(column, qualified, schema=schema, dialect=dialect)
            sources = sorted({leaf.name for leaf in node.walk() if not leaf.downstream and leaf is not node})
        except Exception:
            sources = []
        reports.append(LineageReport(column=column, source_columns=sources))
    return reports


def diff_lineage(before: list[LineageReport], after: list[LineageReport]) -> list[str]:
    """Return column names whose upstream sources changed between two lineage traces."""
    before_map = {r.column: set(r.source_columns) for r in before}
    after_map = {r.column: set(r.source_columns) for r in after}
    changed = []
    for column in set(before_map) | set(after_map):
        if before_map.get(column, set()) != after_map.get(column, set()):
            changed.append(column)
    return sorted(changed)
