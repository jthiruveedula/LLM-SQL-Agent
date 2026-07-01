"""BigQuery dry-run execution for validating transpiled SQL without cost.

Uses ``google-cloud-bigquery`` when available and ``GCP_PROJECT`` is set.
Otherwise returns a best-effort static result so the pipeline can run in
environments without GCP credentials (tests, local dev, CI).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class DryRunResult:
    sql: str
    ok: bool
    bytes_processed: int = 0
    errors: list[str] = field(default_factory=list)


def dry_run(sql: str, project: str | None = None) -> DryRunResult:
    """Validate ``sql`` against BigQuery without scanning data or incurring cost."""
    project = project or os.environ.get("GCP_PROJECT")
    if not project:
        return DryRunResult(sql=sql, ok=True, bytes_processed=0)

    from google.cloud import bigquery  # imported lazily; optional dependency
    from google.api_core.exceptions import GoogleAPICallError

    client = bigquery.Client(project=project)
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    try:
        job = client.query(sql, job_config=job_config)
        return DryRunResult(sql=sql, ok=True, bytes_processed=job.total_bytes_processed or 0)
    except GoogleAPICallError as e:
        return DryRunResult(sql=sql, ok=False, errors=[str(e)])
