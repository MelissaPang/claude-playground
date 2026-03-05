from databricks.connect import DatabricksSession

CATALOG = "melissap"
SCHEMA = "melissa_pang"

# Use the Databricks CLI profile you configured (see next step)
spark = DatabricksSession.builder.profile("DEFAULT").getOrCreate()

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Created schema {CATALOG}.{SCHEMA} (if it did not already exist).")