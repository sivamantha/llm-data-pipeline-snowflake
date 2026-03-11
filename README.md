# Snowflake & dbt: LLM Instruction-Tuning Data Pipeline

## Project Overview
This project demonstrates an enterprise-grade, code-first data pipeline designed to ingest, process, and transform unstructured text data into high-quality training datasets for Large Language Models (LLMs). 

Moving away from UI-driven ELT, this architecture utilizes **dbt-core** and **Snowpark (Python)** to build a strictly version-controlled, Medallion-architecture data warehouse natively inside **Snowflake**.

## Architecture & Stack
* **Data Warehouse & Compute:** Snowflake (Isolated Virtual Warehouses)
* **Transformation & Orchestration:** dbt (Data Build Tool)
* **Data Processing (Text/LLM):** Snowpark (Python 3.12)
* **Version Control & CI/CD:** Git, GitHub Actions
* **Security:** RSA Key-Pair Authentication (Machine-to-Machine)

## Data Flow (Medallion Architecture)
1. **Extraction:** A local Python extraction script pulls raw text documents and uses the Snowflake Python Connector to `PUT` them into a secure internal Snowflake Stage (`raw_text_stage`).
2. **Bronze Layer (Raw):** dbt maps the internal stage to a structured table, establishing an immutable history of raw text payloads.
3. **Silver Layer (Cleaned & Chunked):** dbt executes Snowpark Python models to clean the text, remove PII, and chunk the documents into LLM-optimized token limits (e.g., 512 tokens).
4. **Gold Layer (Ready):** Finalized vector embeddings and instruction-tuning pairs, ready for downstream AI consumption.

## Security & Governance
This project implements strict Enterprise Role-Based Access Control (RBAC):
* **Separation of Compute:** Dedicated, auto-suspending virtual warehouses (`dbt_dev_wh`) to prevent resource contention.
* **Service Accounts:** All automated deployments run via a locked-down service account (`dbt_svc_user`), not a personal developer login, utilizing the `dbt_dev_role`.
* **Secret Management:** Passwords are disabled for machine roles. Authentication is handled via 2048-bit RSA Private/Public Key-Pairs.