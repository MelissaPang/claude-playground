"""Create catalog and schema in the target workspace using the Databricks SDK (no cluster required)."""
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors.platform import NotFound, ResourceDoesNotExist

CATALOG = "melissap"
SCHEMA = "melissa_pang"
PROFILE = "tko"

w = WorkspaceClient(profile=PROFILE)
print(f"Workspace: {w.config.host}")

# Create catalog if it doesn't exist (requires UC privileges)
try:
    w.catalogs.get(CATALOG)
    print(f"Catalog {CATALOG} already exists.")
except (ResourceDoesNotExist, NotFound):
    w.catalogs.create(name=CATALOG)
    print(f"Created catalog {CATALOG}.")

# Create schema if it doesn't exist
try:
    w.schemas.get(f"{CATALOG}.{SCHEMA}")
    print(f"Schema {CATALOG}.{SCHEMA} already exists.")
except (ResourceDoesNotExist, NotFound):
    w.schemas.create(name=SCHEMA, catalog_name=CATALOG)
    print(f"Created schema {CATALOG}.{SCHEMA}.")
