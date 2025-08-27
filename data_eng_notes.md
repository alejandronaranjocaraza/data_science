Notes
---

Reference: Data Warehouse Toolkit -  Ralph Kimball

## CONCEPTS

- 3NF: Model design technique that looks to remove data redunancies. Data is divided into descrete entities (each a table in a relational database.
- Dimensional model: Denormalized, focusing instead on readability and performance for end-users.
- OLTP (Online Transaction Processing): Systems designed for high-speed, real-time transaction management and are optimized for frequent, short operations like order processing and customer interactions.
- OLAP (Online Analytical Processing): Systems optimized for complex analysis and reporting on massive historical datasets, serving data scientists and analysts who need to uncover trends and insights for strategic decision-making.

## BASIC MODEL

                 +--------------------+
                 |   Source Systems   |
                 | (RDS, CSV, APIs)  |
                 +---------+----------+
                           |
                           | Extract
                           v
                 +--------------------+
                 |   Raw Layer (S3)   |
                 | - Parquet files    |
                 | - Partitioned by date
                 +---------+----------+
                           |
                           | Transform (clean, type-cast, dedup)
                           | Tools: Polars / DuckDB / PyArrow
                           v
                 +--------------------+
                 | Curated Layer (S3) |
                 | - Cleaned Parquet  |
                 | - Standardized schema
                 +---------+----------+
                           |
                           | Transform → Build Fact + Dimension Tables
                           | Tools: Polars / DuckDB / SQL (dbt optional)
                           v
                 +--------------------+
                 | Dimensional Layer  |
                 | - Fact Tables      |
                 | - Dimension Tables |
                 | - Partitioned for analytics
                 +---------+----------+
                           |
                           | Query / Analytics
                           | Tools: DuckDB, Athena, BI tools
                           v
                 +--------------------+
                 |    Analytics / BI  |
                 | - Dashboards       |
                 | - Reports          |
                 +--------------------+


AI DUMP
---

# 🔑 Core Skills to Cover Before Starting

## SQL (Intermediate Level)
- Be comfortable writing `SELECT`s, `JOIN`s, `GROUP BY`s, and **window functions**.
- Understand how to query your **RDS** efficiently.
- If you’ll later use **Athena, BigQuery, or Redshift**, learn their SQL dialect nuances.

## Data Warehousing Concepts
- Difference between **staging vs production** schemas.
- **Partitioning** and **incremental loading** (so you don’t reprocess all history each time).
- Basics of **Star schema** / **Snowflake schema**.

## Data Storage in S3 (or another Data Lake)
- How to organize data in S3 buckets (**raw / processed / curated**).
- File formats:  
  - **CSV**  
  - **Parquet** (usually best for analytics)  
  - **JSON**  
  *(learn when to use each)*

## Python for Data Pipelines
- Using **SQLAlchemy** or other connectors to pull from RDS.
- **Pandas basics** for transformations.
- Writing to **S3** (e.g., with `boto3`).

## Airflow Deeper Dive
- DAG structure (scheduling, retries, dependencies).
- Operators you’ll actually use:  
  - `PythonOperator`  
  - `S3Hook`  
  - `PostgresOperator`  
- Connections and variables management in Airflow.
- Logging, monitoring, and retries.

## ETL/ELT Best Practices
- When to do **ELT** (load raw data, transform later in warehouse) vs full ETL.
- **Idempotency** (running a DAG twice should not corrupt data).
- **Metadata tracking** (what was extracted, when).

---

# 🚀 Optional but Strongly Recommended
- **dbt (Data Build Tool)**: for transformations after loading into S3 or warehouse.
- **Airbyte / Fivetran**: understand when you’d use a connector instead of writing custom extraction.
- **Docker basics**: since Airflow often runs in containers, good to know how to tweak environments.

---

# 👉 Suggested Mini-Project
Before building your first production ETL, try:

1. **Extract** 1–2 tables from RDS  
2. **Load** them as Parquet files into S3  
3. **Query** them with Athena  
4. **Orchestrate** this with a simple Airflow DAG (one DAG, 3 tasks)

This small cycle will expose most of the pain points you’ll face later.

# 📚 Core Reading / Learning Resources

## 1. Airflow
- **Official Docs → Airflow Concepts**  
  Clear explanations of DAGs, tasks, operators, retries, scheduling.
- **The Data Engineering Cookbook** *(Andreas Kretz, free PDF online)*  
  Great intro to pipelines, orchestration, and ELT.

## 2. SQL & Warehousing
- **SQL for Data Analysis** *(Mode Analytics, free)* → *Guide*  
  Excellent refresher and covers window functions.
- **Kimball’s The Data Warehouse Toolkit** *(optional, but classic)*  
  Skim the parts on star/snowflake schema design.

## 3. Data Lakes / S3
- **AWS Docs → Best Practices for Organizing S3 Data Lakes**  
- **Blog:** *"Why Parquet is the Best File Format for Big Data"*

## 4. Python for ETL
- **Data Engineering with Python** *(Paul Crickard)*  
  Covers Pandas + Airflow + S3.
- **Boto3 Docs → S3 Examples**

## 5. ETL/ELT Practices
- **Blog:** *"ETL vs ELT — What’s the Difference?"*  
- **Astronomer Blog (makers of Airflow):** *"ETL Best Practices"*

---

# 🎯 Suggested Reading Structure
- **Week 1**: Airflow concepts (official docs) + Mode SQL tutorial  
- **Week 2**: S3 + Parquet articles + boto3 basics  
- **Week 3**: Astronomer ETL best practices + small toy project  
- **Ongoing**: Skim Kretz’s *Data Engineering Cookbook* for mindset  

---

# ⚡ Bonus (Deeper Dive)
- **Fundamentals of Data Engineering** *(O’Reilly, Joe Reis & Matt Housley)*  
  Modern and practical.

