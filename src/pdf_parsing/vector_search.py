# Databricks notebook source
# DBTITLE 1,Installing Vector Search
# MAGIC %pip install databricks-vectorsearch

# COMMAND ----------

# DBTITLE 1,Libraries
from databricks.vector_search.client import VectorSearchClient


# COMMAND ----------

# DBTITLE 1,Getting Variables defined in DABS
gold_catalog=dbutils.widgets.get("gold_catalog")
gold_schema=dbutils.widgets.get("gold_schema")
gold_table=dbutils.widgets.get("gold_table")

gold_table_primary_key= dbutils.widgets.get("gold_table_primary_key")
gold_table_text= dbutils.widgets.get("gold_table_text")



vector_search_endpoint_name= dbutils.widgets.get("vector_search_endpoint_name")
#"vector_search_demo_endpoint"

embedding_model_endpoint_name=dbutils.widgets.get("embedding_model_endpoint_name")
#"databricks-gte-large-en"

# COMMAND ----------

# DBTITLE 1,Creating Vector Search Endpoint
# The following line automatically generates a PAT Token for authentication
client = VectorSearchClient()

client.create_endpoint(
    name=vector_search_endpoint_name,
    endpoint_type="STANDARD" # or "STORAGE_OPTIMIZED"
)

# COMMAND ----------

# DBTITLE 1,Creating delta sync index
client = VectorSearchClient()

index = client.create_delta_sync_index(
  endpoint_name=vector_search_endpoint_name,
  source_table_name=f"{gold_catalog}.{gold_schema}.{gold_table}",
  index_name=f"{gold_catalog}.{gold_schema}.{gold_table}_index",
  pipeline_type="TRIGGERED",
  primary_key=gold_table_primary_key,
  embedding_source_column=gold_table_text,
  embedding_model_endpoint_name= embedding_model_endpoint_name,
)