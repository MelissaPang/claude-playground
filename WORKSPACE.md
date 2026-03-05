# Databricks workspace for this project

This project uses the following workspace:

**https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com**

The **EHR Clinical Explorer** app is deployed to this workspace (profile **tko**). Use the same profile for CLI deploy and for running notebooks that target this workspace.

## Profiles

Use the **tko** profile to target this workspace (OAuth, no token).

### 1. Add the tko profile

Edit `~/.databrickscfg` and add:

```ini
[tko]
host = https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com
# Use serverless compute so you don't need a cluster_id
serverless_compute_id = auto
```

Do **not** add a `token` line; authentication uses OAuth.

**Skipping cluster:** With `serverless_compute_id = auto`, Databricks Connect uses serverless compute and you do **not** need to set `cluster_id`. If you prefer a cluster instead, omit `serverless_compute_id` and set `cluster_id = <your-cluster-id>`.

### 2. Log in with OAuth

```bash
databricks auth login --profile tko
```

A browser window opens. Sign in to the workspace; the CLI stores OAuth credentials locally.

### 3. Verify

```bash
databricks auth token --profile tko
```

If this returns a token, the tko profile is set and authenticated.

### Using the tko profile in code

- **CLI:** `databricks ... --profile tko`
- **Python (SDK / Connect):** `WorkspaceClient(profile="tko")` or `DatabricksSession.builder.profile("tko").getOrCreate()`

To use this workspace by default, point `[DEFAULT]` at the same host or set `DATABRICKS_CONFIG_PROFILE=tko`. The example config (`.databrickscfg.example`) includes both DEFAULT and tko.
