# Databricks notebook source
# DBTITLE 1,Getting Variables defined in DABS
bronze_catalog = dbutils.widgets.get("bronze_catalog")
bronze_schema = dbutils.widgets.get("bronze_schema")
bronze_table = dbutils.widgets.get("bronze_table")

silver_catalog= dbutils.widgets.get("silver_catalog")
silver_schema= dbutils.widgets.get("silver_schema")
silver_table= dbutils.widgets.get("silver_table")
silver_volume_path= dbutils.widgets.get("silver_volume_path")

# COMMAND ----------

# DBTITLE 1,Adding Data Quality and parsing documents with AI Queries
from pyspark.sql import functions as F


df = (
    spark.readStream.table(f"{bronze_catalog}.{bronze_schema}.{bronze_table}")
    .withColumn("parsed_content", F.expr("ai_parse_document(content)"))
    .withColumn("document", F.expr("variant_get(parsed_content, '$.document', 'string')"))
    .withColumn("extraction_timestamp", F.current_timestamp())
)

selected_df = df.select(
    F.col("path"),
    F.col("file_name"),
    F.col("file_size_mb"),
    F.col("parsed_content"),
    F.col("document"),
    F.col("modificationTime"),
    F.col("extraction_timestamp"),
    F.col("ingestion_timestamp"),
)


selected_df.writeStream.option("checkpointLocation", f"{silver_volume_path}/{silver_table}/checkpoints").trigger(availableNow=True).toTable(f"{silver_catalog}.{silver_schema}.{silver_table}")