# Wikipedia RAG Pipeline

An end-to-end data engineering pipeline that extracts Wikipedia articles, transforms them through a Medallion architecture in Snowflake, and serves them to an AI chatbot via vector search.

Built to bridge traditional data engineering (ETL/dbt) and modern AI (vector databases/LLMs), with full CI/CD automation.

**Wikipedia API → Snowflake Stage → Bronze (Raw) → Silver (Cleaned) → Gold (Embeddings) → RAG Chatbot**

## Tech Stack

| Component      | Tool                   |
| -------------- | ---------------------- |
| Database       | Snowflake (Cortex AI)  |
| Transformation | dbt                    |
| Language       | Python 3.12            |
| Automation     | GitHub Actions (daily) |
| Security       | RSA Key-Pair Auth      |

## Pipeline

1. **Extraction** — Python pulls article text from the Wikipedia API and stages it in Snowflake.
2. **Bronze** — Raw text loaded as-is for full audit trail.
3. **Silver** — dbt models clean, filter, and standardize. Tests enforce row counts, null checks, and minimum text length before promotion.
4. **Gold** — Snowflake Cortex generates 768-dimension vector embeddings for semantic search.
5. **Chatbot** — Converts your question to a vector, finds the closest matches in Gold, and passes context to an LLM for a natural-language answer.

## Setup

Requires a Snowflake account with Cortex AI enabled and RSA key-pair authentication.

```bash
pip install -r requirements.txt
python scripts/extract_docs.py
dbt run && dbt test
python scripts/rag_chatbot.py
```

> Runs daily in production via GitHub Actions. See `.github/workflows/` for CI/CD config.
