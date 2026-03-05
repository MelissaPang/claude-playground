#!/usr/bin/env python3
"""Run setup_volume_and_genie notebook cells in sequence."""
# Config
CATALOG = "melissap"
SCHEMA = "melissa_pang"
VOLUME_NAME = "project_volume"
GENIE_SPACE_TITLE = "My Genie Space"
GENIE_SPACE_DESCRIPTION = "Natural language SQL exploration"
WAREHOUSE_ID = None
TABLE_IDENTIFIERS = []
TEMPLATE_SPACE_ID = None

from databricks.sdk import WorkspaceClient
w = WorkspaceClient(profile="DEFAULT")

from databricks.sdk.service.catalog import VolumeType
existing = [v for v in w.volumes.list(catalog_name=CATALOG, schema_name=SCHEMA) if v.name == VOLUME_NAME]
if existing:
    print(f"Volume already exists: {CATALOG}.{SCHEMA}.{VOLUME_NAME}")
else:
    vol = w.volumes.create(
        catalog_name=CATALOG,
        schema_name=SCHEMA,
        name=VOLUME_NAME,
        volume_type=VolumeType.MANAGED,
        comment="Project volume for file storage",
    )
    print(f"Created volume: {vol.full_name}")

if WAREHOUSE_ID:
    warehouse_id = WAREHOUSE_ID
    print(f"Using configured warehouse: {warehouse_id}")
else:
    warehouses = list(w.warehouses.list())
    running = [wh for wh in warehouses if getattr(wh, "state", None) == "RUNNING"]
    if not running:
        raise RuntimeError(
            "No running SQL warehouse found. Start a warehouse or set WAREHOUSE_ID in the config cell."
        )
    warehouse_id = running[0].id
    print(f"Using warehouse: {running[0].name} ({warehouse_id})")

import json
if TEMPLATE_SPACE_ID:
    template = w.genie.get_space(space_id=TEMPLATE_SPACE_ID, include_serialized_space=True)
    serialized_space = template.serialized_space or "{}"
    print(f"Using serialized_space from template space {TEMPLATE_SPACE_ID}")
else:
    serialized_space = json.dumps({"version": 1})

space = w.genie.create_space(
    warehouse_id=warehouse_id,
    serialized_space=serialized_space,
    title=GENIE_SPACE_TITLE,
    description=GENIE_SPACE_DESCRIPTION or None,
)
print(f"Created Genie space: {getattr(space, 'title', GENIE_SPACE_TITLE)} (id: {space.id})")
print(f"Open in workspace: AI/BI Genie > find space by title '{GENIE_SPACE_TITLE}' or id {space.id}")
