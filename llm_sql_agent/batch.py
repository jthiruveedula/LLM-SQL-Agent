"""Async batch processing: migrate many queries concurrently."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from .retry import MigrationResult, migrate_with_retry


async def migrate_batch(
    queries: Iterable[str],
    source_dialect: str,
    target_dialect: str,
    concurrency: int = 16,
) -> list[MigrationResult]:
    """Migrate ``queries`` concurrently, bounded by ``concurrency`` in-flight tasks."""
    semaphore = asyncio.Semaphore(concurrency)

    async def _run(sql: str) -> MigrationResult:
        async with semaphore:
            return await asyncio.to_thread(migrate_with_retry, sql, source_dialect, target_dialect)

    return await asyncio.gather(*(_run(q) for q in queries))


def migrate_batch_sync(
    queries: Iterable[str],
    source_dialect: str,
    target_dialect: str,
    concurrency: int = 16,
) -> list[MigrationResult]:
    """Synchronous entry point for CLI usage; wraps :func:`migrate_batch`."""
    return asyncio.run(migrate_batch(queries, source_dialect, target_dialect, concurrency))
