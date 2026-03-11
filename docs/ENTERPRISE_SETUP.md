# Enterprise Snowflake Environment Setup

This document details the administrative infrastructure, governance, and CI/CD security protocols established before any data transformation code was written.

## 1. Role-Based Access Control (RBAC) Strategy
To ensure a secure, scalable environment, permissions are isolated by entity rather than just function.
* **Developer Access:** The `dbt_dev_role` is granted to human users for interactive query development and local testing.
* **Service Roles:** To enforce a strict Separation of Duties, the same `dbt_dev_role` is explicitly assigned to a service account (`dbt_svc_user`) for CI/CD. This ensures scheduled pipeline runs are insulated from human authentication errors or password expirations.

## 2. Compute Isolation (Virtual Warehouses)
Compute resources are decoupled from storage. A dedicated warehouse (`dbt_dev_wh`) was provisioned exclusively for dbt transformations.
* **Benefit:** Eliminates "noisy neighbor" problems. Heavy analytical queries run by data scientists will not steal compute cycles from scheduled dbt data loading jobs.
* **Cost Control:** Configured with an aggressive 60-second `AUTO_SUSPEND` to minimize credit burn during idle development periods.

## 3. CI/CD Authentication (No Passwords)
For enterprise-grade Continuous Integration/Continuous Deployment (CI/CD), password authentication is a severe security vulnerability.
* **Implementation:** The `dbt_svc_user` relies entirely on **Key-Pair Authentication**.
* **Key Generation:** Unencrypted 2048-bit RSA keys were generated locally via OpenSSL. The Public Key was assigned to the Snowflake user via `SECURITYADMIN`.
* **Secrets Management:** The Private Key is strictly excluded from version control via `.gitignore`. In a production CI/CD environment (like GitHub Actions), this key is securely injected at runtime via GitHub Secrets.

## 4. Version Control (Git)
Unlike UI-based ETL tools (e.g., Azure Synapse), this dbt pipeline utilizes a rigorous software engineering workflow.
* **Protected Main:** The `main` branch is locked. Direct pushes are rejected.
* **Feature Branching:** All development occurs on isolated feature branches (e.g., `feature/python-extraction`).
* **Pull Requests:** Code is only merged into `main` after passing automated CI checks and peer review, preventing broken logic from reaching the production data models.