# 🤖 LLM SQL Agent

[![OpenAI](https://img.shields.io/badge/LLM-OpenAI_GPT4-green?logo=openai)](https://openai.com)
[![SQLGlot](https://img.shields.io/badge/SQL-SQLGlot-blue)](https://github.com/tobymao/sqlglot)

An autonomous agentic system that handles cross-dialect SQL migration (Snowflake to BigQuery) and performs real-time data lineage validation. Designed for enterprise data warehouse modernization projects.

**[▶ See the full pipeline in motion — docs/story.html](docs/story.html)**

## 🚀 Key Capabilities
- **Autonomous SQL Migration**: Converts Snowflake SQL to BigQuery syntax using GPT-4o + SQLGlot.
- **Lineage Validation**: Traces column-level lineage through transformation layers and flags drift after migration.
- **Error Recovery**: Self-healing agent loop with retry logic (parse → correct → re-parse) on syntax errors.
- **Batch Processing**: Migrates thousands of SQL statements concurrently with `asyncio`.

## 🛠️ Tech Stack
- **LLM**: OpenAI GPT-4o (falls back to a rule-based idiom table when `OPENAI_API_KEY` is unset)
- **SQL Transpiler**: SQLGlot
- **Concurrency**: `asyncio` batch runner with a bounded semaphore
- **Output Validation**: Dry run against the BigQuery API + column-level lineage diff

## 🏗️ Architecture

```
Snowflake SQL
      ||
      v
  SQL Parser (SQLGlot) -----> Syntax Validation
      ||
      v
  LLM Agent (GPT-4o) -------> Semantic Corrections
      ||
      v
  BigQuery Executor ---------> Lineage Capture
      ||
      v
  Validation Report
```

Implemented in [`llm_sql_agent/`](llm_sql_agent/):

| Module | Responsibility |
|---|---|
| [`parser.py`](llm_sql_agent/parser.py) | SQLGlot parsing + cross-dialect transpilation |
| [`corrector.py`](llm_sql_agent/corrector.py) | GPT-4o semantic correction with an offline fallback |
| [`retry.py`](llm_sql_agent/retry.py) | Self-healing parse → correct → re-parse loop |
| [`executor.py`](llm_sql_agent/executor.py) | BigQuery dry-run validation |
| [`lineage.py`](llm_sql_agent/lineage.py) | Column-level lineage extraction and drift detection |
| [`batch.py`](llm_sql_agent/batch.py) | Concurrent async migration of many statements |
| [`report.py`](llm_sql_agent/report.py) | Markdown validation report generation |

## 📦 Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables (optional — the agent runs offline without them, using rule-based correction and skipping the live dry run):
   ```bash
   export OPENAI_API_KEY="your_key"
   export GCP_PROJECT="your_project"
   ```
3. Run migration:
   ```bash
   python agent.py --input sample_queries/queries.sql --source snowflake --target bigquery
   ```

## ✅ Tests

```bash
pip install -r requirements.txt
pytest
```

## 📄 License
MIT License
