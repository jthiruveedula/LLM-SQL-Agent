#!/usr/bin/env python3
"""CLI entry point: batch-migrate SQL files between dialects with validation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from llm_sql_agent.batch import migrate_batch_sync
from llm_sql_agent.report import build_report


def split_statements(sql_text: str) -> list[str]:
    """Split a .sql file into individual statements on top-level semicolons."""
    return [s.strip() for s in re.split(r";\s*(?:\n|$)", sql_text) if s.strip()]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate SQL between warehouse dialects.")
    parser.add_argument("--input", required=True, type=Path, help="Path to a .sql file")
    parser.add_argument("--source", required=True, help="Source SQL dialect, e.g. snowflake")
    parser.add_argument("--target", required=True, help="Target SQL dialect, e.g. bigquery")
    parser.add_argument("--concurrency", type=int, default=16)
    parser.add_argument("--report", type=Path, default=None, help="Write the markdown report here")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    queries = split_statements(args.input.read_text())
    if not queries:
        print(f"No statements found in {args.input}", file=sys.stderr)
        return 1

    results = migrate_batch_sync(queries, args.source, args.target, args.concurrency)
    report = build_report(results)

    print(report.to_markdown())
    if args.report:
        args.report.write_text(report.to_markdown())

    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
