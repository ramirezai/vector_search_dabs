# How to Configure `databricks.yml` for the `documents_parsing` Asset Bundle

This guide explains how to fill out the `databricks.yml` file for the `documents_parsing` Databricks Asset Bundle.  
**Important:** You must create all referenced catalogs, schemas, and volumes in your Databricks workspace *before* deploying this bundle.

## 1. Prerequisites

Before using this bundle, ensure the following resources exist in your Databricks workspace:

- **Catalogs:**  
  - `genai` (or your chosen catalog name)

- **Schemas:**  
  - `bronze`, `silver`, `gold` (or your chosen schema names within the catalog)

- **Volumes:**  
  - `/Volumes/genai/bronze/raw_data/university_docs/`
  - `/Volumes/genai/silver/docs_parsed`
  - `/Volumes/genai/gold/docs_chunked_parsed`

You can create catalogs, schemas, and volumes using SQL commands in a Databricks notebook, for example:
sql
CREATE CATALOG IF NOT EXISTS genai;
CREATE SCHEMA IF NOT EXISTS genai.bronze;
CREATE SCHEMA IF NOT EXISTS genai.silver;
CREATE SCHEMA IF NOT EXISTS genai.gold;

CREATE VOLUME IF NOT EXISTS genai.bronze.raw_data;
CREATE VOLUME IF NOT EXISTS genai.silver.docs_parsed;
CREATE VOLUME IF NOT EXISTS genai.gold.docs_chunked_parsed;


## 2. Filling Out `databricks.yml`

The `databricks.yml` file defines variables for your data pipeline, such as which catalogs, schemas, tables, and volumes to use for each stage (bronze, silver, gold).  
You must set these variables for each deployment target (`dev`, `prod`).

### Example Variable Assignments

- **bronze_catalog**: Name of the catalog for the bronze layer (e.g., `genai`)
- **bronze_schema**: Name of the schema for the bronze layer (e.g., `bronze`)
- **bronze_table**: Name of the table for raw documents (e.g., `university_docs`)
- **bronze_volume_path**: Path to the volume for raw data (e.g., `/Volumes/genai/bronze/raw_data/university_docs/`)
- **maxfilespertrigger**: Maximum number of files to process per trigger (e.g., `10`)

Repeat similarly for `silver_*` and `gold_*` variables.

### Example `dev` Target Configuration

yaml
dev:
  mode: development
  default: true
  workspace:
    host: https://adb-1115853741771969.9.azuredatabricks.net
  variables:
    bronze_catalog: genai
    bronze_schema: bronze
    bronze_table: "university_docs"
    bronze_volume_path: "/Volumes/genai/bronze/raw_data/university_docs/"
    maxfilespertrigger: 10

    silver_catalog: genai
    silver_schema: silver
    silver_table: "university_docs_parsed"
    silver_volume_path: "/Volumes/genai/silver/docs_parsed"

    gold_catalog: genai
    gold_schema: gold
    gold_table: "university_docs_parsed_chunks"
    gold_volume_path: "/Volumes/genai/gold/docs_chunked_parsed"

    gold_table_primary_key: "chunk_index"
    gold_table_text: "chunk_text"
    vector_search_endpoint_name: "vector_search_demo_endpoint"
    embedding_model_endpoint_name: "databricks-gte-large-en"


### Example `prod` Target Configuration

yaml
prod:
  mode: production
  workspace:
    host: https://adb-1115853741771969.9.azuredatabricks.net
    root_path: /Workspace/Users/joel.ramirez@databricks.com/.bundle/${bundle.name}/${bundle.target}
  variables:
    catalog: genai
    schema: prod
  permissions:
    - user_name: joel.ramirez@databricks.com
      level: CAN_MANAGE


## 3. Additional Notes

- **Variable Descriptions:** Each variable in the `variables` section is described in the YAML file. Adjust values as needed for your environment.
- **Resource Creation:** If you change catalog, schema, or volume names, ensure you create them in Databricks before deploying.
- **Documentation:** For more details, see [Databricks Asset Bundles documentation](https://docs.databricks.com/dev-tools/bundles/index.html).

---
**Summary:**  
1. Create all referenced catalogs, schemas, and volumes in Databricks.  
2. Fill in the `databricks.yml` variables with your resource names and paths.  
3. Deploy the bundle using the appropriate target (`dev` or `prod`).