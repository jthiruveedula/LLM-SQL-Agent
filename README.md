# 🤖 LLM SQL Agent

[![OpenAI](https://img.shields.io/badge/LLM-OpenAI_GPT4-green?logo=openai)](https://openai.com)
[![SQLGlot](https://img.shields.io/badge/SQL-SQLGlot-blue)](https://github.com/tobymao/sqlglot)

An autonomous agentic system that handles cross-dialect SQL migration (Snowflake to BigQuery) and performs real-time data lineage validation. Designed for enterprise data warehouse modernization projects.

## 🚀 Key Capabilities
- **Autonomous SQL Migration**: Converts Snowflake SQL to BigQuery syntax using GPT-4 + SQLGlot.
- **Lineage Validation**: Traces data flow through transformation layers and validates column-level lineage.
- **Error Recovery**: Self-healing agent loop with retry logic on syntax errors.
- **Batch Processing**: Processes thousands of SQL queries in parallel with async execution.

## 🛠️ Tech Stack
- **LLM**: OpenAI GPT-4o
- **SQL Transpiler**: SQLGlot
- **Orchestration**: LangChain Agents / OpenAI Function Calling
- **Output Validation**: DRY run on BigQuery sandbox

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

## 📦 Quick Start
1. Set environment variables:
   ```bash
   export OPENAI_API_KEY=\"your_key\"
   export GCP_PROJECT=\"your_project\"
   ```
2. Run migration:
   ```bash
   python agent.py --input queries.sql --source snowflake --target bigquery
   ```

## 📄 License
MIT License
