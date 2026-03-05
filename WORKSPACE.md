# Databricks workspace for this project

This project uses the following workspace:

**https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com**

## Configure your environment

### Option 1: Databricks CLI / SDK (profile DEFAULT)

Point the `DEFAULT` profile in `~/.databrickscfg` to this workspace:

```ini
[DEFAULT]
host = https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com
token = <your-personal-access-token>
```

Or use environment variables:

```bash
export DATABRICKS_HOST=https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com
export DATABRICKS_TOKEN=<your-token>
```

### Option 2: Copy the example config

```bash
cp .databrickscfg.example ~/.databrickscfg
# Edit ~/.databrickscfg and add your token.
```

All notebooks and the app use `profile="DEFAULT"` or `Config()`, so they will use this workspace once configured.
