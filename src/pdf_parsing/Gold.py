# Databricks notebook source
# DBTITLE 1,Importing libraries
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, regexp_replace, trim, length, expr
from pyspark.sql.functions import col, current_timestamp, expr, posexplode, length


# COMMAND ----------

# DBTITLE 1,Getting Variables defined in DABS
silver_catalog= dbutils.widgets.get("silver_catalog")
silver_schema= dbutils.widgets.get("silver_schema")
silver_table= dbutils.widgets.get("silver_table")
silver_volume_path= dbutils.widgets.get("silver_volume_path")

gold_catalog=dbutils.widgets.get("gold_catalog")
gold_schema=dbutils.widgets.get("gold_schema")
gold_table=dbutils.widgets.get("gold_table")
gold_volume_path=dbutils.widgets.get("gold_volume_path")

# COMMAND ----------

# DBTITLE 1,Function to clean Data
def clean_text(df: DataFrame, column_name: str) -> DataFrame:
    """
    Clean text content by removing extra whitespace and special characters.
    
    Args:
        df: Input DataFrame
        column_name: Name of the text column to clean
        
    Returns:
        DataFrame with cleaned text column
    """
    cleaned_col = f"{column_name}_cleaned"
    return (
        df.withColumn(
            cleaned_col,
            trim(regexp_replace(col(column_name), r"\s+", " "))
        )
    )



# COMMAND ----------

# DBTITLE 1,Preparing UC table to sync
# Chunking configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
CHUNK_STEP = CHUNK_SIZE - CHUNK_OVERLAP  # 800 characters between chunk starts

# Read from silver and clean text before chunking
df = (
    spark.readStream.table(f"{silver_catalog}.{silver_schema}.{silver_table}")
    .filter(col("document").isNotNull())
)

# Clean text to remove extra whitespace and normalize
df = clean_text(df, "document")

# Create overlapping chunks using native Spark SQL functions
df = (
    df
    .withColumn("doc_length", length(col("document_cleaned")))
    .withColumn(
        "chunk_starts",
        expr(f"sequence(0, doc_length - 1, {CHUNK_STEP})")
    )
    .withColumn(
        "chunks_array",
        expr(f"transform(chunk_starts, x -> substring(document_cleaned, x + 1, {CHUNK_SIZE}))")
    )
    .selectExpr("*", "posexplode(chunks_array) as (chunk_index, chunk_text)")
    .withColumn("chunk_length", length(col("chunk_text")))
    .withColumn("chunk_id", expr("concat(file_name, '_chunk_', chunk_index)"))
    .withColumn("chunk_timestamp", current_timestamp())
)

result = df.select(
    col("chunk_id"),
    col("file_name"),
    col("path"),
    col("chunk_text"),
    col("chunk_index"),
    col("chunk_length"),
    col("file_size_mb"),
    col("modificationTime"),
    col("chunk_timestamp")
)
result.writeStream.option("checkpointLocation", f"{gold_volume_path}/{gold_table}/checkpoints").trigger(availableNow=True).toTable(f"{gold_catalog}.{gold_schema}.{gold_table}")


# COMMAND ----------

