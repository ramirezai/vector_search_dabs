# Databricks notebook source
# DBTITLE 1,Getting Variables defined in DABS
catalog = dbutils.widgets.get("bronze_catalog")
schema = dbutils.widgets.get("bronze_schema")
table = dbutils.widgets.get("bronze_table")
volume = dbutils.widgets.get("bronze_volume_path")
maxfilespertrigger = dbutils.widgets.get("maxfilespertrigger")

# COMMAND ----------

# DBTITLE 1,Incremental ingestion using autoloader from a volume
from pyspark.sql.functions import expr
from pyspark.sql.functions import col, current_timestamp, regexp_extract, round


input_path = f"{volume}/input_data/*.pdf"
schema_location = f"{volume}/schema"
checkpoint_location = f"{volume}/checkpoints"

df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "binaryFile")
    .option("cloudFiles.schemaLocation", schema_location)
    .option("cloudFiles.maxBytesPerTrigger", maxfilespertrigger)
    .load(input_path)
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("file_name", regexp_extract(col("path"), r"[^/]+$", 0))
    .withColumn("file_size_mb", round(col("length") / (1024 * 1024), 2))

)
(
    df.writeStream.option("checkpointLocation", checkpoint_location).trigger(availableNow=True).toTable(f"{catalog}.{schema}.{table}")
)