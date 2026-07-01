"""LLM SQL Agent: cross-dialect SQL migration with lineage validation."""

from .parser import ParsedQuery, parse_and_validate
from .lineage import LineageReport, extract_lineage
from .corrector import correct_query
from .executor import DryRunResult, dry_run
from .retry import migrate_with_retry
from .report import ValidationReport, build_report

__version__ = "0.1.0"

__all__ = [
    "ParsedQuery",
    "parse_and_validate",
    "LineageReport",
    "extract_lineage",
    "correct_query",
    "DryRunResult",
    "dry_run",
    "migrate_with_retry",
    "ValidationReport",
    "build_report",
]
