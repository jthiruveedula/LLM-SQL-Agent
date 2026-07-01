"""SQLGlot-backed parsing and cross-dialect syntax validation."""

from __future__ import annotations

from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


@dataclass
class ParsedQuery:
    sql: str
    source_dialect: str
    target_dialect: str
    transpiled_sql: str | None = None
    syntax_errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.syntax_errors


def parse_and_validate(sql: str, source_dialect: str, target_dialect: str) -> ParsedQuery:
    """Parse ``sql`` in ``source_dialect`` and transpile it to ``target_dialect``.

    Syntax errors surfaced by SQLGlot are captured rather than raised, so the
    caller can route them into the self-healing retry loop.
    """
    result = ParsedQuery(sql=sql, source_dialect=source_dialect, target_dialect=target_dialect)
    try:
        tree = sqlglot.parse_one(sql, read=source_dialect)
    except ParseError as e:
        result.syntax_errors.append(str(e))
        return result

    try:
        result.transpiled_sql = tree.sql(dialect=target_dialect, pretty=True)
    except Exception as e:  # sqlglot raises plain Exception for unsupported constructs
        result.syntax_errors.append(str(e))

    return result


def referenced_tables(sql: str, dialect: str) -> list[str]:
    """Return the fully-qualified table names referenced by ``sql``."""
    tree = sqlglot.parse_one(sql, read=dialect)
    return sorted({table.sql(dialect=dialect) for table in tree.find_all(exp.Table)})
